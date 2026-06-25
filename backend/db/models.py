# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
﻿"""
SQLAlchemy ORM models for the application database.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import relationship

from db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_hash = Column(String(64), nullable=False)
    document_type = Column(String(64), nullable=True)
    status = Column(String(32), default="uploaded")
    page_count = Column(Integer, default=0)
    paragraph_count = Column(Integer, default=0)
    optimized_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    check_results = relationship("CheckResult", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    file_path = Column(String(1024), nullable=False)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="versions")


class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    check_type = Column(String(32), nullable=False)
    severity = Column(String(8), nullable=False)
    rule_id = Column(String(32), nullable=True)
    location = Column(String(256), nullable=True)
    original_text = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="check_results")


class AIConfig(Base):
    __tablename__ = "ai_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(64), nullable=False)
    api_key_encrypted = Column(Text, nullable=True)
    base_url = Column(String(512), nullable=True)
    model = Column(String(128), nullable=True)
    extra_params = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_key = Column(String(64), nullable=False, unique=True)
    name = Column(String(256), nullable=False)
    document_type = Column(String(64), nullable=True)
    source_type = Column(String(16), nullable=False, default="official")
    owner = Column(String(128), nullable=True)
    severity = Column(String(8), nullable=True)
    rule_content = Column(Text, nullable=True)
    rule_version = Column(Integer, nullable=False, default=1)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
