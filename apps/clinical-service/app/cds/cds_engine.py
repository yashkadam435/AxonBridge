import uuid
from typing import List
from app.models.schemas import BotRequest, CDSOverlay, CDSAlert, CDSAction
from app.axonmd.bot_client import AxonMDBotClient
from app.axonmd.specialty_router import SpecialtyRouter
from app.guidelines.embedder import ClinicalEmbedder
from app.guidelines.retriever import GuidelineRetriever
from app.safety.anomaly_detector import AnomalyDetector
from app.safety.confidence_scorer import ConfidenceScorer

class CDSEngine:
    def __init__(self, db_url: str):
        self.bot_client = AxonMDBotClient()
        self.retriever = GuidelineRetriever(db_url)
        self.embedder = ClinicalEmbedder()
        self.anomaly_detector = AnomalyDetector()
        self.confidence_scorer = ConfidenceScorer()

    async def evaluate(self, request: BotRequest, session_id: str) -> CDSOverlay:
        alerts = []
        
        # 1. Anomaly Detection (Vitals)
        if request.vital_signs:
            anomalies = await self.anomaly_detector.check_vitals(request.vital_signs)
            for anomaly in anomalies:
                alerts.append(CDSAlert(
                    id=anomaly.id,
                    priority="emergency" if anomaly.severity == "critical" else "high",
                    category="anomaly",
                    title=f"Abnormal {anomaly.field}",
                    description=anomaly.message,
                    evidence_level="A",
                    source="Safety Engine",
                    confidence=1.0,
                    actions=[CDSAction(label=anomaly.suggested_action, action_type="review")],
                    requires_acknowledgment=anomaly.severity == "critical"
                ))

        # 2. AxonMD Specialty Bot
        # Auto-route if specialty is 'auto'
        specialty = request.specialty
        if specialty == "auto":
            specialty = SpecialtyRouter.route_by_context(request.symptoms, request.department, request.current_diagnosis)
            
        bot_response = await self.bot_client.invoke_bot(specialty, {
            "symptoms": request.symptoms,
            "vitals": request.vital_signs,
            "history": request.patient_context,
            "diagnosis": request.current_diagnosis
        })
        
        confidence = await self.confidence_scorer.score_action("differential", bot_response.confidence, len(request.patient_context.keys()))
        
        # Create Differential Alerts
        differentials = bot_response.content.get("differentials", [])
        if differentials:
            desc = "Possible diagnoses: " + ", ".join([d.get("diagnosis", "") for d in differentials])
            alerts.append(CDSAlert(
                id=str(uuid.uuid4()),
                priority="high" if bot_response.requires_immediate_attention else "medium",
                category="differential",
                title="Bot Differentials",
                description=desc,
                evidence_level="B",
                source=f"AxonMD {specialty.title()}",
                confidence=confidence.overall_score,
                actions=[CDSAction(label="Review Differentials", action_type="review")],
                requires_acknowledgment=False
            ))

        # 3. Guideline RAG (Search based on top symptom/diagnosis)
        search_query = " ".join(request.symptoms)
        if request.current_diagnosis:
            search_query += f" {request.current_diagnosis}"
            
        if search_query.strip():
            guideline_matches = await self.retriever.search(search_query)
            
            for match in guideline_matches:
                if match.get("similarity", 0) > 0.6:  # Threshold
                    alerts.append(CDSAlert(
                        id=str(uuid.uuid4()),
                        priority="info",
                        category="guideline",
                        title=f"{match['source']} Guideline",
                        description=match["content"],
                        evidence_level="A",
                        source=f"{match['source']} {match['version']}",
                        confidence=match.get("similarity", 0),
                        actions=[CDSAction(label="Read Full Guideline", action_type="info")],
                        requires_acknowledgment=False
                    ))
                    
        emergency_count = sum(1 for a in alerts if a.priority == "emergency")
        
        return CDSOverlay(
            session_id=session_id,
            alerts=alerts,
            summary=f"Found {len(alerts)} alerts. {emergency_count} critical.",
            total_alerts=len(alerts),
            emergency_count=emergency_count,
            requires_acknowledgment=emergency_count > 0
        )
