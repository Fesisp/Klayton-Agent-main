"""
Config Validator - Validador de Configuração de Runtime
========================================================

Valida chaves, tipos e intervalos dos arquivos de configuração YAML/JSON (Fail-Fast).

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ConfigValidationError(Exception):
    """Exceção para configurações inválidas."""
    pass


class ConfigValidator:
    """Validador de esquema de configuração."""

    def validate(self, config_data: Dict[str, Any]) -> bool:
        """Verifica chaves e intervalos obrigatórios na configuração."""
        if not isinstance(config_data, dict):
            raise ConfigValidationError("Configuração deve ser um dicionário")

        if "input" in config_data:
            max_actions = config_data["input"].get("max_actions_per_second", 15)
            if not isinstance(max_actions, (int, float)) or max_actions <= 0:
                raise ConfigValidationError("input.max_actions_per_second deve ser um número positivo")

        return True
