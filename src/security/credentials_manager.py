"""
Credentials Manager - Gerenciador Seguro de Credenciais
======================================================

Carrega chaves de API e segredos sensíveis estritamente via variáveis de ambiente ou arquivos .env.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

from __future__ import annotations

import os
from typing import Optional


class CredentialsManager:
    """Gerenciador seguro de credenciais e chaves de API (Herança do Projeto Interview)."""

    def __init__(self, env_path: Optional[str] = None):
        self.env_path = env_path

    def get_credential(self, key_name: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém a credencial a partir do ambiente do sistema operacional."""
        return os.environ.get(key_name, default)

    def mask_secret(self, secret: str) -> str:
        """Mascara o segredo para ser exibido em logs de forma segura."""
        if not secret or len(secret) <= 8:
            return "***"
        return f"{secret[:4]}...{secret[-4:]}"
