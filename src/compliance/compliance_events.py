"""
Compliance Events - Eventos de Auditoria e Supervisão
======================================================

Constantes dos eventos emitidos pela camada de compliance para registro e auditoria.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

RATE_LIMIT_HIT = "COMPLIANCE_RATE_LIMIT_HIT"
SESSION_LIMIT_HIT = "COMPLIANCE_SESSION_LIMIT_HIT"
LOW_CONFIDENCE_PAUSE = "COMPLIANCE_LOW_CONFIDENCE_PAUSE"
FOCUS_GUARD_TRIGGERED = "COMPLIANCE_FOCUS_GUARD_TRIGGERED"
REPETITIVE_LOOP_DETECTED = "COMPLIANCE_REPETITIVE_LOOP_DETECTED"
MANUAL_RESUME_REQUIRED = "COMPLIANCE_MANUAL_RESUME_REQUIRED"
COMPLIANCE_BLOCK = "COMPLIANCE_BLOCK"
