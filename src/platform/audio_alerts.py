"""
Audio Alert Service - Serviço Cross-Platform de Alertas Sonoros
================================================================

Fornece alertas sonoros encapsulados, utilizando winsound no Windows
e fallbacks silenciosos em plataformas Linux/macOS.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import sys


class AudioAlertService:
    """Serviço de alertas sonoros cross-platform."""

    def __init__(self) -> None:
        self._winsound = None

        if sys.platform == "win32":
            try:
                import winsound
                self._winsound = winsound
            except ImportError:
                self._winsound = None

    def warning(self) -> None:
        """Dispara um alerta sonoro de aviso/erro."""
        if self._winsound is not None:
            try:
                self._winsound.MessageBeep(self._winsound.MB_ICONHAND)
            except Exception:
                pass

    def info(self) -> None:
        """Dispara um alerta sonoro informativo."""
        if self._winsound is not None:
            try:
                self._winsound.MessageBeep(self._winsound.MB_ICONASTERISK)
            except Exception:
                pass
