"""
AxonBridge — Language Models

Language configuration, translation cache, and voice session tracking
for the multilingual NLP engine.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TenantScopedModel, BaseModel


class LanguageConfig(TenantScopedModel):
    """
    Language configuration per tenant.
    Defines which languages are active and their STT/TTS models.
    """

    __tablename__ = "language_configs"

    language_code: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True,
        comment="ISO 639-1/639-3 code: en, hi, ar, ms, sw, etc."
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Name in the language itself: हिन्दी, العربية"
    )

    # Properties
    is_rtl: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="Right-to-left language: Arabic, Hebrew, Urdu"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # STT configuration
    stt_model: Mapped[str] = mapped_column(
        String(100), default="whisper-large-v3", nullable=False,
        comment="STT model: whisper-large-v3, google-stt-v2, azure-cognitive"
    )
    stt_accuracy_target: Mapped[float] = mapped_column(
        Float, default=0.90, nullable=False,
        comment="Target WER accuracy"
    )

    # TTS configuration
    tts_voice: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="TTS voice ID"
    )
    tts_model: Mapped[str] = mapped_column(
        String(100), default="coqui-xtts-v2", nullable=False
    )

    # Translation
    translation_model: Mapped[str] = mapped_column(
        String(100), default="opus-mt", nullable=False,
        comment="Translation model: indictrans2, opus-mt, google-translate"
    )

    def __repr__(self) -> str:
        return f"<LanguageConfig(code='{self.language_code}', name='{self.display_name}')>"


class TranslationCache(BaseModel):
    """
    Cache for frequently translated medical terms and phrases.
    Keyed by source language + target language + text hash.
    """

    __tablename__ = "translation_cache"

    source_lang: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    target_lang: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    source_text_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        comment="SHA-256 hash of source text"
    )
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Model info
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Usage tracking
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<TranslationCache(src='{self.source_lang}', tgt='{self.target_lang}')>"
