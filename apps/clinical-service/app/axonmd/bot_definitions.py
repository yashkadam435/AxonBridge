BOT_DEFINITIONS = {
    "general_medicine": {
        "endpoint": "/api/v1/bots/general-medicine",
        "input_schema": {"symptoms": list, "vitals": dict, "history": str},
        "output_schema": {"differentials": list, "recommendations": list, "confidence": float},
        "timeout": 15,
        "fallback_order": ["emergency_medicine"]
    },
    "cardiology": {
        "endpoint": "/api/v1/bots/cardiology",
        "input_schema": {"ecg_findings": str, "cardiac_risk_factors": list, "symptoms": list},
        "output_schema": {"differentials": list, "investigations": list, "acs_risk": str},
        "timeout": 15,
        "triggers": ["chest_pain", "dyspnea", "palpitation", "syncope", "ecg_abnormal"]
    },
    "emergency_medicine": {
        "endpoint": "/api/v1/bots/emergency",
        "input_schema": {"triage_level": int, "chief_complaint": str, "vitals": dict},
        "output_schema": {"triage_recommendation": str, "red_flags": list, "time_critical_actions": list},
        "timeout": 10,
        "priority": 1  # Always check for emergencies first
    },
    "neurology": {
        "endpoint": "/api/v1/bots/neurology",
        "input_schema": {"neurological_symptoms": list, "gcs_score": int, "focal_deficits": list},
        "output_schema": {"stroke_probability": float, "differentials": list, "imaging_urgency": str},
        "triggers": ["headache", "seizure", "weakness", "numbness", "altered_consciousness"]
    },
    "endocrinology": {
        "endpoint": "/api/v1/bots/endocrinology",
        "triggers": ["diabetes", "thyroid", "hormone", "glucose", "hba1c"]
    },
    "gastroenterology": {
        "endpoint": "/api/v1/bots/gastroenterology",
        "triggers": ["abdominal_pain", "vomiting", "diarrhea", "gi_bleed", "jaundice"]
    },
    "nephrology": {
        "endpoint": "/api/v1/bots/nephrology",
        "triggers": ["ckd", "creatinine", "dialysis", "hematuria", "proteinuria"]
    },
    "pulmonology": {
        "endpoint": "/api/v1/bots/pulmonology",
        "triggers": ["copd", "asthma", "tb", "pneumonia", "dyspnea", "cough"]
    },
    "obstetrics_gynaecology": {
        "endpoint": "/api/v1/bots/obgyn",
        "triggers": ["pregnancy", "antenatal", "postnatal", "gynaecological"]
    },
    "paediatrics": {
        "endpoint": "/api/v1/bots/paediatrics",
        "triggers": ["child", "neonatal", "immunization", "growth", "developmental"]
    },
    "orthopaedics": {
        "endpoint": "/api/v1/bots/orthopaedics",
        "triggers": ["fracture", "joint_pain", "trauma", "sprain", "arthritis"]
    },
    "dermatology": {
        "endpoint": "/api/v1/bots/dermatology",
        "triggers": ["rash", "lesion", "eczema", "psoriasis", "skin_infection"]
    },
    "psychiatry": {
        "endpoint": "/api/v1/bots/psychiatry",
        "triggers": ["depression", "anxiety", "suicidal", "psychosis", "substance_abuse"]
    },
    "oncology": {
        "endpoint": "/api/v1/bots/oncology",
        "triggers": ["cancer", "tumour", "chemotherapy", "radiotherapy", "biopsy"]
    },
    "infectious_disease": {
        "endpoint": "/api/v1/bots/infectious-disease",
        "triggers": ["fever", "sepsis", "malaria", "dengue", "tuberculosis", "hiv"]
    }
}
