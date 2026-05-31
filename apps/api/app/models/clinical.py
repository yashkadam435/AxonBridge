"""
AxonBridge — Clinical Data Models

Encrypted clinical data models for patient encounters,
SOAP notes, and coded entities (ICD-10, SNOMED, LOINC).
All PHI fields use application-level encryption.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel


class PatientEncounter(TenantScopedModel):
    """
    A clinical encounter/visit. Patient identifiers are encrypted.
    """

    __tablename__ = "patient_encounters"

    # Encrypted identifiers (AES-256)
    encounter_id_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="AES-256 encrypted encounter ID from HIS"
    )
    patient_id_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="AES-256 encrypted patient identifier from HIS"
    )
    patient_name_encrypted: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="AES-256 encrypted patient name"
    )

    # Clinician
    clinician_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Encounter details
    encounter_type: Mapped[str] = mapped_column(
        String(50), default="outpatient", nullable=False,
        comment="Type: outpatient, inpatient, emergency, telehealth"
    )
    encounter_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False,
        comment="Status: active, completed, cancelled"
    )

    # Source tracking
    his_source: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="HIS system where this encounter originated"
    )

    # Relationships
    clinical_notes: Mapped[list["ClinicalNote"]] = relationship(
        "ClinicalNote", back_populates="encounter", lazy="selectin",
        cascade="all, delete-orphan",
    )
    soap_notes: Mapped[list["SOAPNote"]] = relationship(
        "SOAPNote", back_populates="encounter", lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PatientEncounter(id={self.id}, status='{self.status}')>"


class ClinicalNote(TenantScopedModel):
    """
    Free-text clinical note with encrypted content.
    """

    __tablename__ = "clinical_notes"

    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patient_encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Note content (encrypted)
    note_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: progress, admission, discharge, consultation, procedure"
    )
    content_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="AES-256 encrypted note content"
    )
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Processing status
    is_transcribed: Mapped[bool] = mapped_column(default=False, nullable=False)
    transcription_source: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Source: manual, whisper_stt, voice_recording"
    )
    is_coded: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Review
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    encounter: Mapped["PatientEncounter"] = relationship(
        "PatientEncounter", back_populates="clinical_notes"
    )
    coded_entities: Mapped[list["CodedEntity"]] = relationship(
        "CodedEntity", back_populates="note", lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ClinicalNote(id={self.id}, type='{self.note_type}')>"


class SOAPNote(TenantScopedModel):
    """
    Structured SOAP note with encrypted sections.
    Generated from clinical notes via NLP processing.
    """

    __tablename__ = "soap_notes"

    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patient_encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # SOAP sections (encrypted)
    subjective_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    objective_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Coded data
    icd_codes: Mapped[list | None] = mapped_column(
        JSONB, nullable=True,
        comment="List of ICD-10 codes extracted"
    )
    snomed_codes: Mapped[list | None] = mapped_column(
        JSONB, nullable=True,
        comment="List of SNOMED CT codes extracted"
    )
    loinc_codes: Mapped[list | None] = mapped_column(
        JSONB, nullable=True,
        comment="List of LOINC codes for lab/observations"
    )

    # Processing metadata
    generated_by: Mapped[str] = mapped_column(
        String(50), default="manual", nullable=False,
        comment="Source: manual, ai_structured, voice_transcription"
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    llm_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Clinician review gate
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    encounter: Mapped["PatientEncounter"] = relationship(
        "PatientEncounter", back_populates="soap_notes"
    )

    def __repr__(self) -> str:
        return f"<SOAPNote(id={self.id}, approved={self.is_approved})>"


class CodedEntity(TenantScopedModel):
    """
    Extracted clinical entity with coding (ICD-10, SNOMED, LOINC).
    Linked to a clinical note.
    """

    __tablename__ = "coded_entities"

    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Entity
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: diagnosis, medication, allergy, procedure, vital, symptom, lab_result"
    )
    text_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="AES-256 encrypted original text"
    )
    normalized_text: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="Normalized/standardized text (non-PHI)"
    )

    # Coding
    code_system: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="System: ICD-10, SNOMED-CT, LOINC, RxNorm, NDC"
    )
    code_value: Mapped[str | None] = mapped_column(String(50), nullable=True)
    code_display: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Confidence
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_method: Mapped[str] = mapped_column(
        String(50), default="nlp", nullable=False,
        comment="Method: nlp, manual, rule_based"
    )

    # Relationships
    note: Mapped["ClinicalNote"] = relationship(
        "ClinicalNote", back_populates="coded_entities"
    )

    def __repr__(self) -> str:
        return f"<CodedEntity(id={self.id}, type='{self.entity_type}')>"
