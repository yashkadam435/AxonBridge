# AxonBridge AI Workflow Testing Examples

Use the following raw text snippets to test the dynamic AI extraction capabilities of the 5 new workflow modules. Simply navigate to the **Workflows** page, click **Run AI Model** on the respective workflow card, paste the exact text into the "Raw Input Data" box, and hit **Run AI Extraction**.

---

## 1. Patient Registration Extraction
**URL Route:** `/dashboard/workflows/registration`

**Test Input:**
> Patient Robert Chen, born October 14, 1975, presented to the front desk at 9:00 AM today. He stated his current address is 4421 Pine Lane, Seattle, WA 98101. His contact number is (206) 555-0199 and he identifies as male. He handed over his insurance card from UnitedHealthcare, policy number UHC-9988776655. In case of an emergency, he asked us to contact his daughter, Emily Chen, at (206) 555-0982.

**Expected AI Output:**
Structured JSON mapped precisely to the `PatientRegistrationSchema` containing Name, DOB, Gender, Address, UnitedHealthcare policy, and Emergency Contact details.

---

## 2. Billing Code Entry
**URL Route:** `/dashboard/workflows/billing`

**Test Input:**
> Chief Complaint: 45-year-old female presents with severe right lower quadrant abdominal pain, nausea, and low-grade fever. 
> Assessment: Acute appendicitis with localized peritonitis.
> Plan: Patient was prepped for emergency surgery. Performed a laparoscopic appendectomy under general anesthesia. Pathology confirmed acute suppurative appendicitis. 

**Expected AI Output:**
Structured JSON identifying ICD-10 codes for Acute Appendicitis (e.g., K35.80) and CPT codes for Laparoscopic Appendectomy (e.g., 44970), along with a clinical justification.

---

## 3. Lab Result Extraction
**URL Route:** `/dashboard/workflows/lab-results`

**Test Input:**
> LABORATORY REPORT - eHospital Labs
> Patient: Sarah Jenkins | Date Collected: Nov 12, 2026
> Comprehensive Metabolic Panel (CMP):
> Sodium: 138 mEq/L (Ref: 135-145)
> Potassium: 4.1 mEq/L (Ref: 3.5-5.2)
> Chloride: 102 mEq/L (Ref: 96-106)
> Glucose: 185 mg/dL (Ref: 70-99) **HIGH**
> BUN: 22 mg/dL (Ref: 7-20) **HIGH**
> Creatinine: 1.1 mg/dL (Ref: 0.6-1.2)
> 
> Complete Blood Count (CBC):
> White Blood Cells (WBC): 14.5 x10^3/uL (Ref: 4.5-11.0) **HIGH**
> Hemoglobin (Hgb): 13.2 g/dL (Ref: 12.0-15.5)
> Platelets: 250 x10^3/uL (Ref: 150-450)

**Expected AI Output:**
An array of 9 distinct structured lab values with extracted test names, values, units, and reference ranges. The `abnormal_findings` array will dynamically flag the high Glucose, BUN, and WBC counts.

---

## 4. Discharge Summary
**URL Route:** `/dashboard/workflows/discharge`

**Test Input:**
> Pt is Michael Barnes. Admitted on 05/18/2026 via ER for shortness of breath and wheezing. Found to have an acute exacerbation of COPD triggered by a viral upper respiratory infection. Treated with IV Solu-Medrol and continuous albuterol nebulizers. Transitioned to oral prednisone 40mg daily and Combivent inhaler. Pt improved significantly by day 3 and is stable for discharge today, 05/21/2026. Discharge Dx: Acute COPD exacerbation, URI. Meds at discharge: Prednisone 40mg PO for 5 days, Symbicort 160/4.5 2 puffs BID, Albuterol HFA 2 puffs q4h PRN. Follow up with Dr. Smith (Pulmonology) in 2 weeks. Return to ER if respiratory distress worsens.

**Expected AI Output:**
A comprehensive, professionally formatted Discharge Summary structured with explicit fields for Hospital Course, Admission/Discharge Dates, Discharge Diagnoses array, and explicitly listed Discharge Medications.

---

## 5. Appointment Scheduling
**URL Route:** `/dashboard/workflows/scheduling`

**Test Input:**
> Hi, this is Amanda Torres calling. I need to make an urgent appointment for my son, David Torres. He's been running a very high fever since yesterday and pulling at his ear. We'd like to see Dr. Evans, the pediatrician, as soon as possible, preferably tomorrow morning around 9:30 AM if he has an opening. It really can't wait.

**Expected AI Output:**
Structured JSON extracting the patient name (David Torres), requested doctor (Dr. Evans), requested date (Tomorrow), requested time (9:30 AM), reason for visit (High fever and ear pain), and classifying the Urgency as "Urgent".
