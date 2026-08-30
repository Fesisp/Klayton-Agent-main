"""
Replay Logger - Gravador de Sessões e Decisões
==============================================

Registra cada ciclo de decisão do agente em um log de replay JSONL:
{timestamp, world_state_summary, goal, decision, active_skill, result}

Permite reproduzir, analisar e debugar a sessão sem necessidade de jogar novamente.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import time


class ReplayLogger:
    """
    Gravador sequencial de log de Replay do Agente.
    """

    def __init__(self, log_filepath: Optional[Path] = None):
        if log_filepath is None:
            log_filepath = Path("debug") / f"replay_{int(time.time())}.jsonl"
        self.log_filepath = log_filepath
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)

    def log_step(self, goal: str, decision: str, active_skill: Optional[str], world_summary: Dict[str, Any], result_msg: str) -> None:
        """
        Grava uma linha de replay no arquivo JSONL.
        """
        entry = {
            'timestamp': time.time(),
            'goal': goal,
            'decision': decision,
            'active_skill': active_skill,
            'world': world_summary,
            'result': result_msg
        }

        with open(self.log_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
