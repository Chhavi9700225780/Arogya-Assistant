# Arogya Wellness Assistant

**Arogya Wellness Assistant** is a full-stack, multi-agent health and wellness assistant.  
The backend (Flask + LangChain + Google Gemini) coordinates specialized agents for symptoms, lifestyle, diet, and fitness, then synthesizes a **safe wellness plan**.  
The frontend (React + Vite) provides a guided experience for login, profile management, wellness queries, and follow-up questions.

---

## Core Features

### Multi-Agent Wellness Pipeline
- **Symptom Triage Agent** – identifies general wellness concerns (non-diagnostic)
- **Lifestyle Guidance Agent** – sleep, routine, stress-related advice
- **Diet & Nutrition Agent** – food and hydration guidance (with simple RAG context)
- **Fitness & Activity Agent** – low-intensity, safety-first movement suggestions

### Shared Conversational Memory
- Short-term memory shared between agents during orchestration
- Ensures agents are context-aware of each other’s outputs

###  Structured Orchestration Output
The orchestrator combines all agent outputs into a single structured JSON response:
- `synthesized_guidance` – markdown wellness plan with:
  - Overview  
  - When to See a Doctor  
  - Lifestyle & Rest  
  - Hydration & Diet  
  - Hygiene & Environment  
  - Movement & Activity  
  - Final Note
- `recommendations` – concise bullet-point takeaways
- Raw agent outputs:
  - `symptom_analysis`
  - `lifestyle`
  - `diet`
  - `fitness`

###  Follow-up Q&A
- Users can ask follow-up questions after receiving a wellness plan
- Backend uses the **last stored plan + recommendations** as context
- Ensures continuity and safer responses

### Frontend Experience
- Username/password login (demo JSON-based store)
- Profile management:
  - height
  - weight
  - medications
- Wellness dashboard:
  - Full wellness plan or **recommendations-only** view
  - Optional **Agent Communication View**
  - Markdown-rendered summaries
  - Follow-up questions panel
- Shared navbar & branding: **Arogya Wellness Orchestrator**

---

##  Tech Stack

### Backend
- Python 3.11
- Flask (REST API, routing, error handling)
- LangChain (core abstractions, messages, memory)
- `langchain-google-genai`
- `ChatGoogleGenerativeAI` (Google Gemini)
- Shared conversation buffer memory
- JSON-file data storage:
  - User credentials *(demo only, not production-secure)*
  - User profiles
  - Session & orchestration history

### Frontend
- React + Vite
- Axios for API communication
- `react-markdown` for rendering markdown responses
- Custom CSS for:
  - Cards
  - Navbar
  - Buttons
  - Responsive layout

### Configuration & Security
- Environment variables using `.env`
- Gemini API key & model configuration
- Username/password authentication via `/login`
- CORS enabled for local development

---

## API Endpoints

###  Authentication
**POST** `/login`  
{
  "username": "user1",
  "password": "password"
}

## Health Assistance

**POST** /health-assist

{
  "symptoms": "fever and headache",
  "medical_report": ""
}

## Recommendations Only

**POST** /recommendations
Returns only the recommendations in points.

## Follow-Up Questions

**POST** /follow-up



## Running the Project
**Backend Setup**
cd healthbackend
pip install -r requirements.txt

# Set GEMINI API key and model name in .env
python -m healthbackend.app

Backend runs at:
http://127.0.0.1:5000

## Frontend Setup
cd wellness-frontend
npm install
npm run dev


Frontend runs at:
http://127.0.0.1:5173
