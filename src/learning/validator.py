"""
Experience Validator - Validação Empírica de Efeitos no Ambiente
================================================================

Compara os estados do WorldState antes e depois de um teste de ação e retorna
um ValidationResult contendo o resultado empírico (success), nível de confiança e razão.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any
from .models import ValidationResult


class ExperienceValidator:

    def validate(
        self,
        before: Any,
        after: Any,
        expectation: str,
    ) -> ValidationResult:

        if before is None or after is None:
            return ValidationResult(
                success=False,
                confidence=0.0,
                reason="missing_state_snapshot"
            )

        if expectation == "map_changed":
            before_map = getattr(before.location, "current_map", None) if hasattr(before, "location") else getattr(before, "current_map", None)
            after_map = getattr(after.location, "current_map", None) if hasattr(after, "location") else getattr(after, "current_map", None)

            success = (
                before_map is not None
                and after_map is not None
                and before_map != after_map
                and after_map not in ["Unknown", ""]
            )

            return ValidationResult(
                success=success,
                confidence=0.95 if success else 0.30,
                reason="map_transition_observed" if success
                else "map_transition_not_observed",
            )

        if expectation == "movement_success":
            before_pos = getattr(before.player, "position", None) if hasattr(before, "player") else getattr(before, "player_position", None)
            after_pos = getattr(after.player, "position", None) if hasattr(after, "player") else getattr(after, "player_position", None)

            success = (
                before_pos is not None
                and after_pos is not None
                and before_pos != after_pos
            )

            return ValidationResult(
                success=success,
                confidence=0.90 if success else 0.35,
                reason="player_position_changed" if success
                else "movement_not_confirmed",
            )

        if expectation == "dialog_opened":
            before_interaction = getattr(before, "interaction", None)
            after_interaction = getattr(after, "interaction", None)

            before_dialog = getattr(before_interaction, "dialog_open", False) if before_interaction else getattr(before, "dialog_open", False)
            after_dialog = getattr(after_interaction, "dialog_open", False) if after_interaction else getattr(after, "dialog_open", False)

            success = (not before_dialog) and bool(after_dialog)

            return ValidationResult(
                success=success,
                confidence=0.95 if success else 0.35,
                reason="dialog_opened" if success
                else "dialog_not_detected",
            )

        return ValidationResult(
            success=False,
            confidence=0.0,
            reason="unsupported_expectation",
        )
