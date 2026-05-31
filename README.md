# 🧠 AxonBridge: Universal Agentic Automation Layer for Healthcare
**Client Demo Presentation & Architecture Guide**

## 1. Complete Project Overview
Hospitals worldwide are locked into legacy Hospital Information Systems (HIS) and Electronic Health Records (EHR). Switching costs are catastrophic, and vendor APIs are often closed, expensive, or non-existent.

**AxonBridge is the solution.** It is an AI-powered middleware that operates on top of *any* existing application exactly as a skilled human operator would—without requiring API access, vendor cooperation, or system replacement. By utilizing Vision-based AI, Natural Language Processing, and Browser Automation, AxonBridge converts manual, repetitive HIS tasks into fully autonomous, AI-augmented workflows. 

## 2. Features and Functionalities
- **Agent Monitor (Phase 1 & 2):** A real-time control center tracking Autonomous AI RPA agents navigating HIS systems (like eHospital, Practo, Epic, Cerner).
- **Human-in-the-Loop (HITL) Safety:** Critical actions (submitting billing codes, prescribing medications) pause the agent and trigger an approval request, ensuring zero autonomous clinical errors.
- **Clinical Docs (Phase 4):** Complete Clinical Intelligence Layer. Replaces manual typing with:
  - **Voice Dictation:** Transcribing spoken notes into structured clinical context.
  - **AxonMD Specialty Bots:** Dynamic LLM prompt routing to assist with specialist differential diagnoses (e.g., Cardiology bot).
  - **Clinical Decision Support (CDS):** Real-time anomaly detection for vitals and AI-driven prescribing with allergy cross-checking.
  - **Auto SOAP Note Generation:** Using AI to convert raw transcripts and vitals into structured Subjective, Objective, Assessment, and Plan notes.
- **Workflow AI Extraction:** Dedicated NLP pipelines for parsing Patient Registration, Billing Codes, Lab Results, Discharge Summaries, and Appointment Scheduling from raw text or voice.

## 3. Tech Stack Used
**Current Demonstration Stack:**
- **Frontend:** Next.js 14, React 18, TypeScript, TailwindCSS
- **Backend:** FastAPI (Python 3.12), Pydantic
- **AI / LLM Engine:** Groq API (`llama-3.3-70b-versatile`) for blazing-fast inference and workflow simulation.
- **State Management:** In-memory Python caching & local JSON persistence (`agents_db.json`, `encounters_db.json`).
- **Containerization:** Docker & Docker Compose.

**Production (Enterprise) Additions:**
- PostgreSQL + `pgvector` (Vector Database for RAG & Clinical Knowledge Graphs)
- Redis (Session caching and queue management)
- MinIO (S3-compatible object storage for HIPAA-compliant clinical artifacts)
- Playwright / Puppeteer (For actual headless browser manipulation of the target HIS).

## 4. API Routes
The backend exposes the following core microservices on port `8004`:

**Agent Orchestration:**
- `GET /api/v1/agents` - Fetch real-time active agents and pending HITL actions.
- `POST /api/v1/agents/new` - Spawn a new AI agent session.
- `POST /api/v1/agents/{id}/simulate` - Trigger Groq to generate the next logical UI action.
- `POST /api/v1/agents/actions/{id}/approve` - HITL approval to unblock an agent.

**Clinical Intelligence:**
- `GET /api/v1/clinical/encounters/encounters` - Fetch patient encounters.
- `POST /api/v1/clinical/encounters/encounters` - Save new encounters.
- `POST /api/v1/clinical/axonmd/consult` - Trigger specialty-specific differential diagnoses.
- `POST /api/v1/clinical/cds/check` - Real-time anomaly and contraindication checking.
- `POST /api/v1/clinical/encounters/generate-soap` - LLM generation of structured clinical notes.

## 5. Docker Images Used
- `node:20-alpine`: Extremely lightweight Linux image for compiling and serving the Next.js frontend (`axonbridge-web`).
- `python:3.12-slim`: Minimal Python environment serving the FastAPI backend (`axonbridge-api`).
- *(Optional Production Layer)*: `postgres:16-alpine`, `redis:7-alpine`.

## 6. Current Limitations (Demo Phase)
- **Simulated Actuation:** The current build uses a *Headless Simulation Engine*. The Groq LLM generates realistic RPA instructions (e.g., "Click Login"), but we are not currently launching a physical headless browser to click buttons on a real hospital website (as we do not have target credentials).
- **In-Memory/File Persistence:** For demo speed and portability, databases are mocked via local JSON files.
- **Voice Scribe API:** Speech-to-text uses the Web Speech API (browser native), which lacks the clinical accuracy of a dedicated medical model like Azure Clinical Speech.

## 7. End-to-End System & Infrastructure Requirements
To deploy AxonBridge at scale in a hospital, you must plan for the following compute and software resources:

### Hardware Requirements (Per Node)
- **RAM:** Minimum 32GB RAM (64GB Recommended for running 50+ concurrent Playwright Chromium instances).
- **CPU:** 8-16 vCPUs.
- **Storage:** 500GB NVMe SSD for fast PostgreSQL I/O and short-term caching.
- **Vision Models Storage:** If hosting open-source Vision models locally (e.g., Llama-3-Vision, Qwen-VL) to bypass cloud APIs for data privacy, expect **40GB to 100GB of storage per model**, and a dedicated **NVIDIA A100 or H100 GPU** cluster (80GB VRAM).

### Paid APIs & Third-Party Requirements
- **Groq API / OpenAI GPT-4o / Anthropic Claude 3.5 Sonnet:** Enterprise contracts required for the core reasoning engine.
- **Medical STT:** Nuance/Azure Clinical Speech or AWS Medical Transcribe ($0.03 to $0.06 per minute of audio).
- **Proxy/Gateway:** Enterprise Kong API Gateway for rate limiting and OAuth 2.0 integration.

### Enterprise Scaling & Advanced Libraries
To scale this to an enterprise level processing thousands of patient workflows daily:
- **Kubernetes (K8s):** Horizontal pod autoscaling of the Python Playwright agents to handle peak hospital load.
- **LangGraph / Temporal.io:** Implementing durable, stateful AI execution. If an agent crashes halfway through a billing form, Temporal guarantees it resumes exactly where it left off.
- **Kafka / RabbitMQ:** Event-driven messaging to queue thousands of RPA tasks asynchronously.

## 8. Client Demo Script
**Use this exact script to guide your client through the software:**

> **Presenter:** "Hospitals are trapped by legacy software. You can't easily integrate modern AI into a 15-year-old EHR system. AxonBridge fixes this without touching a single line of your hospital's code. Let me show you."

**(Open the Agent Monitor)**
> **Presenter:** "This is the Agent Control Center. Let's spawn a few AI agents." *(Click '+ New Agent Session' 3 times)*. "In the background, our AI Brain (powered by Groq) is currently mapping out how to navigate systems like Practo or eHospital. Look at the **Live Action Log**—you can see the AI actively reasoning and deciding what buttons to click next."

**(Wait for an Agent to hit 'Pending Human Confirmation')**
> **Presenter:** "Notice how the agent paused. In healthcare, safety is critical. The AI is not allowed to submit a billing code autonomously. It stops, alerts the administrator, and waits. Watch." *(Click 'Approve')*. "The agent instantly resumes its task. Complete automation, but with 100% human oversight."

**(Open Clinical Docs)**
> **Presenter:** "Now let's look at the clinician's side. Doctors spend 40% of their time typing. With AxonBridge, they just talk." *(Create a New Encounter with Emergency symptoms)*. "The AI instantly analyzes the vitals and flags anomalies. By clicking **Run CDS**, our AxonMD Specialty Bots provide real-time differential diagnoses. Finally, click **Generate SOAP**—the AI perfectly formats the entire consultation into a structured clinical note, ready to be automatically pushed into your EHR by our RPA agents."

## 9. Testing Examples (For the 'Workflows' Tab)
To demonstrate the AI's data extraction capabilities, navigate to the **Workflows** tab and use these inputs:

**1. Patient Registration**
> *Input:* Patient Robert Chen, born October 14, 1975, presented to the front desk at 9:00 AM today. He stated his current address is 4421 Pine Lane, Seattle, WA 98101. His contact number is (206) 555-0199 and he identifies as male. He handed over his insurance card from UnitedHealthcare, policy number UHC-9988776655.

**2. Billing Code Entry**
> *Input:* Chief Complaint: 45-year-old female presents with severe right lower quadrant abdominal pain, nausea, and low-grade fever. Assessment: Acute appendicitis with localized peritonitis. Plan: Patient was prepped for emergency surgery. Performed a laparoscopic appendectomy under general anesthesia.

**3. Discharge Summary**
> *Input:* Pt is Michael Barnes. Admitted on 05/18/2026 via ER for shortness of breath and wheezing. Found to have an acute exacerbation of COPD triggered by a viral upper respiratory infection. Treated with IV Solu-Medrol and continuous albuterol nebulizers. Transitioned to oral prednisone 40mg daily and Combivent inhaler. Pt improved significantly by day 3 and is stable for discharge today, 05/21/2026. Discharge Dx: Acute COPD exacerbation, URI.

## 10. Anticipated Client Questions & Recommended Answers

**Q: Doesn't the hospital's EHR vendor (e.g., Epic, Cerner) block this kind of automation?**
> **A:** "No. AxonBridge uses Vision-based AI and Playwright to interact with the frontend User Interface exactly like a human doctor does. We do not use backend APIs or reverse-engineer databases, so we bypass vendor lock-in completely and are legally fully compliant."

**Q: What happens if the EHR updates their software and the buttons move?**
> **A:** "Traditional RPA bots break instantly. AxonBridge does not. Because we use Vision LLMs, the AI 'looks' at the screen. If the 'Submit' button moves from the left side to the right side, the AI visually finds it and clicks it anyway."

**Q: Is patient data safe? Does it go to OpenAI or Groq?**
> **A:** "For this demo, we are using cloud APIs. However, for a production enterprise deployment, we deploy Open-Source models (like Llama-3 70B) directly on the hospital's local bare-metal servers. No Patient Health Information (PHI) ever leaves the hospital's secure network, ensuring 100% HIPAA and GDPR compliance."

**Q: Will this replace our administrative staff?**
> **A:** "AxonBridge is designed as an *augmentation* tool, not a replacement. As you saw with the 'Agent Monitor', it operates in an 'Assisted Mode'. It handles the heavy lifting of clicking and typing, but relies on your staff to review and approve the actions. It makes your existing staff 10x faster."
