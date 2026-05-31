# Phase 4: Clinical Intelligence & Documentation — Testing Guide

## Overview & Significance

This Clinical Docs feature realizes **Phase 4** of the AxonBridge FRD: "Clinical Intelligence & Documentation." It differentiates AxonBridge from generic RPA tools by providing a **clinical intelligence layer** with AxonMD specialty bot integration, clinical decision support (CDS) with non-obstructive overlay rendering, human-in-the-loop confirmation UI with confidence scoring, anomaly detection for out-of-range values, and a complete safety control system ensuring no autonomous clinical decisions are made without human oversight.

**Alignment with FRD:**
1. **Clinical Service Architecture:** We have built the FastAPI backend (`apps/clinical-service`) running in Docker.
2. **AxonMD Specialty Bots:** Dynamic LLM prompt routing (e.g., Cardiology/Emergency bot triggered by chest pain).
3. **Clinical Decision Support (CDS):** Runs on vitals, differentials, and guidelines (RAG).
4. **Safety Control System:** All AI actions (SOAP notes, prescriptions) include a confidence score and a mandatory "Approve" workflow. Anomalies (e.g., abnormal vitals) trigger immediate alerts.

---

## Complete Testing Guide

Everything is fully wired to the backend API (`http://localhost:8004`). Every button now triggers a real, end-to-end operation.

### Step 1: Create a Clinical Encounter
1. Navigate to **Clinical Docs** from the sidebar.
2. Click the **"New Encounter"** button in the top right.
3. Fill out the patient information and clinical details.
   - **Tip:** Try an emergency scenario to see the AxonMD Emergency Bot in action.
   - *Example Data:* 
     - Chief Complaint: `Severe chest pain radiating to left arm`
     - Symptoms: `chest pain, shortness of breath, diaphoresis`
     - Vitals: Systolic BP `210`, Diastolic `110`, SpO2 `91`
4. Click **"Create Encounter"**. The system will save this to the in-memory database and take you to the Encounter Detail View.

### Step 2: Test Anomaly Detection & CDS
1. Notice the **Anomaly Alerts** at the top of the detail view (e.g., "Abnormal systolic_bp" or "Abnormal spo2"). This is the Safety Engine running statistical anomaly detection on the vitals you entered.
2. Click **"Run CDS"** (Clinical Decision Support) at the top.
3. This triggers the **AxonMD Specialty Router**. It will detect the emergency symptoms and invoke the appropriate bot (e.g., Emergency Medicine/Cardiology).
4. A **Clinical Advisory** panel will slide out on the right showing:
   - Priority alerts (e.g., from the Safety Engine).
   - Differential diagnoses from the AxonMD Bot.
   - Relevant guidelines retrieved via RAG.

### Step 3: Test AI-Powered SOAP Note Generation
1. Click the **"Generate SOAP"** button.
2. The AI will ingest the patient context, symptoms, and vitals, and generate a fully structured SOAP note (Subjective, Objective, Assessment, Plan) formatted in JSON and rendered elegantly in the UI.
3. Notice the **AI Confidence** score in the top right of the SOAP card. 
4. The note status will initially be **"Pending Review"** (Yellow).

### Step 4: Test Human-in-the-Loop Safety Confirmation
1. Click the **"Approve SOAP"** button (Green Shield).
2. The **ClinicalConfirmationDialog** will appear. This satisfies the FRD requirement for "Human-in-the-loop confirmation UI".
3. Review the AI-generated data.
4. You can click **"Modify"** to enter edit mode, allowing the clinician to rewrite parts of the SOAP note before approval.
5. Click **"Approve & Save"**. The status changes to **"Approved"** (Green).

### Step 5: Test AI Prescription Generation
1. Once a SOAP note is generated and an Assessment/Diagnosis is available, the **"Generate Prescription"** button becomes active.
2. Click it. The AI will act as a clinical pharmacology bot.
3. It will recommend medications (including dosage, route, frequency) while cross-checking against the patient's listed allergies and current medications.
4. It will also generate **Contraindications** and **Drug Interactions** warnings.

### Step 6: Test Encounter State Management
1. Click **"← Back"** to return to the Encounter List.
2. You will see a dashboard tracking "Total Encounters", "Active", "Pending Review", and "Approved".
3. Your newly created and approved encounter will appear in the list with its corresponding status badge and generated ICD-10 codes.
4. Clicking the encounter will re-load all of its saved data seamlessly.
