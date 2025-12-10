# Import utilities for JSON parsing, regex cleaning, and LangChain components
import json
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# Quota handling
from google.api_core import exceptions as google_exceptions
from healthbackend.services.api_key_pool import get_next_key, mark_key_quota_exceeded

# Import individual agent functions and supporting services
from healthbackend.services.agents import (
    symptom_agent,
    lifestyle_agent,
    diet_agent,
    fitness_agent,
)
from healthbackend.services.history_store import save_history
from healthbackend.services.memory import get_shared_memory, reset_memory
from healthbackend.config.settings import MODEL_NAME


def _make_synth_llm_with_key():
    """Create the synthesizer LLM using the next available Gemini API key."""
    key = get_next_key()
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,  # Deterministic output for structured JSON
        google_api_key=key,
        convert_system_message_to_human=True,
    )
    return llm, key


# ------------------------------------------------------------
# Main orchestration function
# ------------------------------------------------------------
# Purpose: Coordinate all agents in sequence and synthesize a final wellness plan
async def orchestrate(symptoms: str, medical_report: str, user_id: str):
    # Reset shared memory to start fresh for this user session
    # Ensures no cross-contamination between different users/sessions
    reset_memory()
    memory = get_shared_memory()

    # ------------------------------------------------------------
    # Sequential Agent Execution (dependency chain)
    # ------------------------------------------------------------
    # 1. Symptom agent runs first (standalone)
    symptom_result = await symptom_agent(symptoms)

    # 2. Lifestyle agent uses symptoms (standalone)
    lifestyle_result = await lifestyle_agent(symptoms)

    # 3. Diet agent uses symptoms + medical report + lifestyle results
    diet_result = await diet_agent(
        symptoms=symptoms,
        report=medical_report,
        lifestyle_notes=lifestyle_result,
    )

    # 4. Fitness agent uses symptoms + diet results
    fitness_result = await fitness_agent(
        symptoms=symptoms,
        diet_notes=diet_result,
    )

    # Retrieve complete conversation history after all agents have run
    # This captures all agent interactions for the synthesizer
    history = memory.load_memory_variables({})["chat_history"]

    # ------------------------------------------------------------
    # Synthesizer LLM Setup
    # ------------------------------------------------------------
    # Initialize a separate LLM instance for final synthesis (with key rotation)
    synth_llm, synth_key = _make_synth_llm_with_key()

    # Define comprehensive synthesis prompt with strict JSON output format
    # Specifies exact markdown structure + JSON schema for parsing
    synth_messages = [
        SystemMessage(
            content=(
                "You are an orchestrator summarizing a mild to moderate health concern.\n"
                "Read the full conversation between symptom_agent, lifestyle_agent, "
                "diet_agent, and fitness_agent.\n\n"
                "Write a concise, well-structured wellness plan in markdown with these sections:\n"
                "1. Overview – 2-3 sentences summarizing the situation and overall goal.\n"
                "2. When to See a Doctor – 2-4 bullet points, clearly describing red-flag symptoms.\n"
                "3. Lifestyle & Rest – 3-5 bullet points with specific, gentle daily actions.\n"
                "4. Hydration & Diet – 3-5 bullet points with simple, safe food and fluid guidance.\n"
                "5. Hygiene & Environment – 2-4 bullet points to reduce irritation and infection spread.\n"
                "6. Movement & Activity – 2-4 bullet points with ONLY low-intensity options, "
                "including a bold STOP warning for chest pain, breathing difficulty, dizziness, "
                "or marked worsening.\n"
                "7. Final Note – 1-2 sentences reminding that this is not a diagnosis and to "
                "follow a doctor's advice.\n\n"
                "Tone: calm, reassuring, non-alarming, strictly non-diagnostic. "
                "Never name specific medicines or doses. Never say you replace a doctor.\n\n"
                "Return ONLY valid JSON with keys:\n"
                "  - synthesized_guidance: the markdown text described above\n"
                "  - recommendations: array of short, plain-language recommendation strings\n"
                "Do not wrap JSON in code fences or add any extra text."
            )
        ),
        *history,  # Include full agent conversation history
        HumanMessage(content="Generate the JSON response now."),
    ]

    # Get synthesized response from orchestrator LLM
    try:
        final_answer = await synth_llm.ainvoke(synth_messages)
    except google_exceptions.ResourceExhausted:
        # Quota exceeded for this key → mark it in cooldown and retry once with a new key
        mark_key_quota_exceeded(synth_key)
        synth_llm, synth_key = _make_synth_llm_with_key()
        final_answer = await synth_llm.ainvoke(synth_messages)

    raw = final_answer.content.strip()

    # ------------------------------------------------------------
    # JSON Cleaning and Parsing
    # ------------------------------------------------------------
    # Remove common markdown code fences that LLMs sometimes add
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)     

    # Parse JSON response with error handling
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: treat raw text as guidance, empty recommendations list
        data = {"synthesized_guidance": raw, "recommendations": []}

    # ------------------------------------------------------------
    # Final Output Structure
    # ------------------------------------------------------------
    # Package all agent results + synthesized guidance into single response
    output = {
        "user_id": user_id,
        "query": symptoms,
        "symptom_analysis": symptom_result,
        "lifestyle": lifestyle_result,
        "diet": diet_result,
        "fitness": fitness_result,
        "synthesized_guidance": data.get("synthesized_guidance", ""),
        "recommendations": data.get("recommendations", []),
    }

    # Persist complete session to user-specific history storage
    save_history(user_id, output)

    # Return structured response for frontend/API consumption
    return output
