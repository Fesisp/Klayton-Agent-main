"""
Test Self-Supervised Learning Subsystem - Aprendizado Auto-Supervisionado por Hipóteses
========================================================================================

Valida:
1. Instanciação de LearnedFact e transições de status (HYPOTHESIS -> LIKELY -> CONFIRMED -> TRUSTED / REFUTED).
2. Trava de Risco (ExplorationRisk) bloqueando ações comerciais/destrutivas autônomas.
3. Banco de Dados SQLite KnowledgeBase (salvamento, recuperação e relatórios estatísticos).
4. Motor de Hipóteses (HypothesisEngine) mapeando tipos semânticos para planos executáveis.
5. ExperienceValidator validando ground truth do ambiente (map_changed, dialog_opened, movement_success).
6. Algoritmo probabilístico ConfidenceUpdater (sucessos e falhas).
7. Supervisão Humana (HumanFeedbackSystem).
8. Execução soberana do LearningEngine.

Autor: Klayton Companion Agent Framework
Data: 2026-08-31
"""

import sys
import asyncio
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.learning.learned_fact import LearnedFact, KnowledgeStatus, ExplorationRisk
from src.learning.knowledge_base import KnowledgeBase
from src.learning.hypothesis_engine import HypothesisEngine
from src.learning.experience_validator import ExperienceValidator
from src.learning.confidence_updater import ConfidenceUpdater
from src.learning.human_feedback import HumanFeedbackSystem, DecisionRecord
from src.learning.learning_engine import LearningEngine
from src.perception.semantic.semantic_vision import SemanticVision
from src.perception.semantic.providers.base_provider import NullVisionProvider


class MockWorldState:
    def __init__(self, current_map="Pallet Town", dialog_open=False, position=(5, 5), in_battle=False):
        self.location = type("Loc", (), {"current_map": current_map})()
        self.dialog_open = dialog_open
        self.player_position = position
        self.battle = type("Bat", (), {"in_battle": in_battle})()
        self.agent = type("Ag", (), {"current_goal": "EXPLORE"})()
        self.game_state = "EXPLORING"

    def snapshot(self):
        import copy
        return copy.deepcopy(self)


class MockExecutor:
    def __init__(self, world):
        self.world = world

    async def execute_learning_action(self, action: str, fact: LearnedFact):
        await asyncio.sleep(0.01)
        if action == "approach_and_cross":
            self.world.location.current_map = "Route 1"
        elif action == "approach_and_interact":
            self.world.dialog_open = True
        elif action == "walk_over":
            self.world.player_position = (5, 6)


def test_self_supervised_learning_pipeline():
    print("🧪 Testando Subsistema de Aprendizado Auto-Supervisionado (Self-Supervised Learning)...")

    # 1. Teste de LearnedFact e Inicialização
    fact = LearnedFact(
        concept="door_pallet_town_house",
        properties={"semantic_type": "door", "possible_interaction": "walk_into"},
        confidence=0.5,
        status=KnowledgeStatus.HYPOTHESIS
    )
    assert fact.confidence == 0.5
    assert fact.status == KnowledgeStatus.HYPOTHESIS
    assert fact.risk_level == ExplorationRisk.SAFE
    print("  ✅ LearnedFact instanciado com o princípio 'IA sugere hipótese com confiança 0.5'")

    # 2. Teste da Trava de Risco (ExplorationRisk)
    hyp_engine = HypothesisEngine()
    safe_test = hyp_engine.create_test(fact)
    assert safe_test is not None
    assert safe_test["action"] == "approach_and_cross"
    assert safe_test["expected"] == "map_changed"
    print("  ✅ HypothesisEngine gerou plano executável SAFE para 'door'")

    dangerous_fact = LearnedFact(
        concept="shop_buy_potion",
        properties={"semantic_type": "merchant", "possible_interaction": "buy_item"},
        risk_level=ExplorationRisk.DANGEROUS
    )
    dangerous_test = hyp_engine.create_test(dangerous_fact)
    assert dangerous_test is None
    print("  ✅ Trava de Risco (ExplorationRisk) bloqueou com sucesso ação DANGEROUS de compra autônoma")

    # 3. Teste do ExperienceValidator (Ground Truth do Ambiente)
    validator = ExperienceValidator()
    before_state = MockWorldState(current_map="Pallet Town")
    after_state = MockWorldState(current_map="Route 1")

    map_val = validator.validate(before_state, after_state, "map_changed")
    assert map_val is True
    print("  ✅ ExperienceValidator confirmou mudanÃ§a empírica de mapa ('Pallet Town' ➔ 'Route 1')")

    before_dialog = MockWorldState(dialog_open=False)
    after_dialog = MockWorldState(dialog_open=True)
    dialog_val = validator.validate(before_dialog, after_dialog, "dialog_opened")
    assert dialog_val is True
    print("  ✅ ExperienceValidator confirmou abertura empírica de diálogo no jogo")

    # 4. Teste do Algoritmo ConfidenceUpdater
    fact_test = LearnedFact(concept="test_concept", properties={}, confidence=0.5, status=KnowledgeStatus.HYPOTHESIS)
    
    # 1º Sucesso
    ConfidenceUpdater.success(fact_test)
    assert fact_test.confidence == 0.625
    assert fact_test.successes == 1

    # 2º Sucesso
    ConfidenceUpdater.success(fact_test)
    assert fact_test.successes == 2
    assert fact_test.status == KnowledgeStatus.LIKELY

    # 3º Sucesso
    ConfidenceUpdater.success(fact_test)
    assert fact_test.successes == 3
    assert fact_test.confidence >= 0.75
    assert fact_test.status == KnowledgeStatus.CONFIRMED
    print("  ✅ ConfidenceUpdater promoveu a hipótese para CONFIRMED após 3 sucessos práticos (Confiança: {:.2f})".format(fact_test.confidence))

    # Teste de Falha
    bad_fact = LearnedFact(concept="bad_concept", properties={}, confidence=0.5)
    ConfidenceUpdater.failure(bad_fact)
    ConfidenceUpdater.failure(bad_fact)
    ConfidenceUpdater.failure(bad_fact)
    assert bad_fact.status == KnowledgeStatus.REFUTED
    print("  ✅ ConfidenceUpdater refutou a hipótese (REFUTED) após 3 falhas seguidas")

    # 5. Teste da Supervisão Humana (HumanFeedbackSystem)
    human_fact = LearnedFact(concept="human_concept", properties={}, confidence=0.5)
    HumanFeedbackSystem.apply_feedback(human_fact, "correct")
    assert human_fact.status == KnowledgeStatus.CONFIRMED
    assert human_fact.confidence >= 0.95
    print("  ✅ HumanFeedbackSystem validou a entrada do supervisor com prioridade CONFIRMED")

    # 6. Teste da KnowledgeBase em SQLite
    kb_path = Path("scratch/test_knowledge.db")
    if kb_path.exists():
        try:
            kb_path.unlink()
        except Exception:
            pass

    kb = KnowledgeBase(db_path=kb_path)
    kb.save_fact(fact_test)
    kb.save_fact(bad_fact)

    retrieved = kb.get_fact("test_concept")
    assert retrieved is not None
    assert retrieved.status == KnowledgeStatus.CONFIRMED
    assert len(kb.list_facts()) == 2
    print("  ✅ KnowledgeBase salvou e recuperou com sucesso fatos aprendidos no SQLite")

    # 7. Teste de Execução E2E do LearningEngine
    async def run_learning_e2e():
        world = MockWorldState(current_map="Viridian City")
        executor = MockExecutor(world)
        vision = SemanticVision(provider=NullVisionProvider())

        engine = LearningEngine(semantic_vision=vision, knowledge_base=kb)
        
        # Simula criação de hipótese vinda da visão semântica
        sim_fact = LearnedFact(
            concept="door_viridian_center",
            properties={"semantic_type": "door", "possible_interaction": "walk_into"},
            confidence=0.5
        )

        test_plan = engine.hypothesis_engine.create_test(sim_fact)
        assert test_plan["action"] == "approach_and_cross"

        before = world.snapshot()
        await executor.execute_learning_action(test_plan["action"], sim_fact)
        after = world.snapshot()

        success = engine.validator.validate(before, after, test_plan["expected"])
        assert success is True

        ConfidenceUpdater.success(sim_fact)
        kb.save_fact(sim_fact)

        metrics = engine.get_metrics()
        assert metrics["total_facts_in_kb"] >= 3
        print("  ✅ LearningEngine orquestrou com sucesso a investigação auto-supervisionada E2E!")
        print(f"     📊 Métricas: KB Facts={metrics['total_facts_in_kb']} | Confirmed={metrics['confirmed_facts']} | Reuse Rate={metrics['knowledge_reuse_rate']*100:.1f}%")

    asyncio.run(run_learning_e2e())


if __name__ == "__main__":
    test_self_supervised_learning_pipeline()
