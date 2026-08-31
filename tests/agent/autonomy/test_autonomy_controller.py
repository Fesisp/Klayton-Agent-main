"""
Test Autonomy Controller - Ciclo Completo de Autonomia de Metas
================================================================

Valida:
1. Execução do tick completo (Arbitragem ➔ Decomposição ➔ Avaliação).
2. Transição da meta para COMPLETED ao finalizar o progresso.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.agent.autonomy.goal_candidate import GoalCandidate
from src.agent.autonomy.goal_state import GoalState
from src.agent.autonomy.autonomy_controller import AutonomyController
from src.world.world_state import WorldState, PokemonInfo


def test_autonomy_controller_lifecycle():
    print("🧪 Testando AutonomyController (Ciclo Completo de Autonomia)...")

    controller = AutonomyController()
    world = WorldState()
    world.team.members.append(PokemonInfo(name="Pikachu", level=30))

    cand = GoalCandidate(goal_type="TRAIN_POKEMON", target="Pikachu", target_level=35)

    # 1. Tick #1 -> Ativa a meta e decompõe em TaskGraph
    active_goal1 = controller.tick([cand], world, {})
    assert active_goal1 is not None
    assert active_goal1.state == GoalState.ACTIVE
    print("  ✅ Tick #1: Meta ativada e TaskGraph gerado")

    # 2. Tick #2 -> Pikachu atinge nível 35 (Completa a meta)
    world.team.members[0].level = 35
    active_goal2 = controller.tick([cand], world, {})
    assert active_goal1.state == GoalState.COMPLETED
    print("  ✅ Tick #2: Meta concluída ao atingir nível 35 (GoalState.COMPLETED)")


if __name__ == "__main__":
    test_autonomy_controller_lifecycle()
