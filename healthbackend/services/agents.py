from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from healthbackend.config.settings import MODEL_NAME
from healthbackend.services.memory import get_shared_memory
from healthbackend.services.rag import retrieve_context
from healthbackend.services.api_key_pool import get_next_key, mark_key_quota_exceeded
from google.api_core import exceptions as google_exceptions




def _make_llm_with_key():
    """
    Create a Gemini chat model using the next available API key.

    Returns:
        tuple[ChatGoogleGenerativeAI, str]: (llm instance, api_key used)
    """
    # Pick the next key from the pool (handles round‑robin and cooldown logic)
    api_key = get_next_key()

    # Instantiate the Gemini chat model with that key
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=api_key,
        convert_system_message_to_human=True,
    )
    return llm, api_key


def _memory():
    """
    Convenience wrapper to get the shared conversation memory object.
    All agents write into the same buffer so they can see each other’s outputs.
    """
    return get_shared_memory()


# ------------------------------------------------------------
# SYMPTOM AGENT
# ------------------------------------------------------------
async def symptom_agent(symptoms: str) -> str:
    """
    Analyze raw symptoms and comment on possible severity / urgency.
    Does NOT diagnose; only suggests when to see a doctor or seek emergency care.
    """
    memory = _memory()
    # Load previous messages so this agent can see context from other agents
    history = memory.load_memory_variables({})["chat_history"]

    # System prompt describes the role and strict safety constraints
    messages = [
        SystemMessage(
            content=(
                "You are a safe medical triage assistant. "
                "You only assess severity and suggest if the user should see a doctor. "
                "Do not provide diagnoses or prescriptions."
            )
        ),
    ] + history + [
        # Human message for this specific call
        HumanMessage(
            content=f"Analyze these symptoms and their possible severity: {symptoms}"
        )
    ]

    # Create LLM with a specific key and call it once
    llm, key = _make_llm_with_key()
    try:
        result = await llm.ainvoke(messages)
    except google_exceptions.ResourceExhausted:
        # This key exceeded its quota → mark it as cooling down and retry with another key
        mark_key_quota_exceeded(key)
        llm, key = _make_llm_with_key()
        result = await llm.ainvoke(messages)

    # Store the agent’s input and output in shared memory
    memory.save_context(
        {"input": f"[symptom_agent] {symptoms}"},
        {"output": result.content},
    )
    return result.content


# ------------------------------------------------------------
# LIFESTYLE AGENT
# ------------------------------------------------------------
async def lifestyle_agent(symptoms: str) -> str:
    """
    Suggest lifestyle adjustments (sleep, stress, routine) based on symptoms
    and conversation context. Keeps suggestions generic and safe.
    """
    memory = _memory()
    history = memory.load_memory_variables({})["chat_history"]

    # Compose the user‑specific prompt
    prompt = (
        f"Given the conversation so far and these symptoms: {symptoms}, "
        f"suggest lifestyle changes and constraints."
    )

    messages = [
        SystemMessage(
            content=(
                "You are a lifestyle coach collaborating with other agents. "
                "Suggest simple lifestyle habits, sleep hygiene, stress management, "
                "and daily routine tips. Keep suggestions safe and generic."
            )
        ),
    ] + history + [HumanMessage(content=prompt)]

    llm, key = _make_llm_with_key()
    try:
        result = await llm.ainvoke(messages)
    except google_exceptions.ResourceExhausted:
        # Quota hit → disable key temporarily and retry with another key
        mark_key_quota_exceeded(key)
        llm, key = _make_llm_with_key()
        result = await llm.ainvoke(messages)

    # Log input/output for this agent into shared memory
    memory.save_context(
        {"input": f"[lifestyle_agent] {prompt}"},
        {"output": result.content},
    )
    return result.content


# ------------------------------------------------------------
# DIET AGENT
# ------------------------------------------------------------
async def diet_agent(symptoms: str, report: str, lifestyle_notes: str) -> str:
    """
    Propose a safe, balanced diet plan using:
      - user symptoms
      - optional medical report text
      - output of lifestyle_agent
      - retrieved snippets from local knowledge base (RAG)
    The guidance is strictly non‑diagnostic and non‑prescriptive.
    """
    memory = _memory()
    history = memory.load_memory_variables({})["chat_history"]

    # Retrieve relevant snippets from knowledge.json (RAG hook)
    kb = retrieve_context(symptoms)

    # Build a detailed prompt with all relevant context
    prompt = (
        f"User symptoms: {symptoms}\n"
        f"Relevant medical report text (may be empty): {report}\n"
        f"Lifestyle information from lifestyle_agent: {lifestyle_notes}\n"
        f"Evidence / knowledge base snippets: {kb}\n\n"
        "Suggest a safe, balanced diet plan. Mention foods to prefer and foods to avoid. "
        "Highlight that this is not a replacement for a dietician or doctor."
    )

    messages = [
        SystemMessage(
            content=(
                "You are a dietician collaborating with other agents to give general diet guidance. "
                "Never claim to cure diseases or override a doctor's advice."
            )
        ),
    ] + history + [HumanMessage(content=prompt)]

    llm, key = _make_llm_with_key()
    try:
        result = await llm.ainvoke(messages)
    except google_exceptions.ResourceExhausted:
        # If this key is out of quota, cool it down and use another one
        mark_key_quota_exceeded(key)
        llm, key = _make_llm_with_key()
        result = await llm.ainvoke(messages)

    # Persist the diet agent’s reasoning into shared memory
    memory.save_context(
        {"input": f"[diet_agent] {prompt}"},
        {"output": result.content},
    )
    return result.content


# ------------------------------------------------------------
# FITNESS AGENT
# ------------------------------------------------------------
async def fitness_agent(symptoms: str, diet_notes: str) -> str:
    """
    Recommend gentle, low‑risk physical activities that respect
    both the symptoms and the diet constraints.
    Always reminds the user to stop if they feel discomfort and to
    consult a doctor before more intense exercise.
    """
    memory = _memory()
    history = memory.load_memory_variables({})["chat_history"]

    # Include both current symptoms and diet constraints in the prompt
    prompt = (
        f"User symptoms: {symptoms}\n"
        f"Diet constraints from diet_agent: {diet_notes}\n\n"
        "Recommend only low‑risk, gentle physical activities, "
        "and clearly tell the user to stop if they feel pain or discomfort."
    )

    messages = [
        SystemMessage(
            content=(
                "You are a cautious fitness coach. "
                "You design simple, low‑intensity plans that are generally safe. "
                "Always recommend consulting a doctor before heavy exercise."
            )
        ),
    ] + history + [HumanMessage(content=prompt)]

    llm, key = _make_llm_with_key()
    try:
        result = await llm.ainvoke(messages)
    except google_exceptions.ResourceExhausted:
        # Current key has hit its quota → mark and retry with a fresh key
        mark_key_quota_exceeded(key)
        llm, key = _make_llm_with_key()
        result = await llm.ainvoke(messages)

    # Save the fitness guidance into shared memory
    memory.save_context(
        {"input": f"[fitness_agent] {prompt}"},
        {"output": result.content},
    )
    return result.content
