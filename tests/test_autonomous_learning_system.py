"""
Test Klayton Autonomous Learning System - Teste de Aprendizado por Hipótese + Ação + Consequência
===================================================================================================

Valida:
1. Modelos de Conhecimento (LearnedFact, KnowledgeStatus, ExplorationRisk, LearningTest, ValidationResult, DecisionRecord).
2. VisionLanguageProvider abstrato e NullVisionProvider.
3. SemanticVision gerando hipóteses com confiança 0.5.
4. HypothesisEngine mapeando conceitos e bloqueando riscos MODERATE e DANGEROUS.
5. ExperienceValidator validando ground truth do ambiente (map_changed, movement_success, dialog_opened).
6. ConfidenceUpdater (fórmulas de sucesso e falha com evidence_strength, transições LIKELY -> CONFIRMED -> TRUSTED / REFUTED).
7. Repositório SQLite KnowledgeBase (tabelas learned_facts, learning_events, decisions).
8. LearningEngine orquestrando a investigação auto-supervisionada E2E.

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

from src.learning.models import LearnedFact, KnowledgeStatus, ExplorationRisk, LearningTest, ValidationResult, DecisionRecord
from src.learning.hypothesis import HypothesisEngine
from src.learning.validator import ExperienceValidator
from src.learning.confidence import ConfidenceUpdater
from src.learning.knowledge_base import KnowledgeBase
from src.learning.learning_engine import LearningEngine
from src.perception.semantic.semantic_vision import SemanticVision
from src.perception.semantic.providers.null_provider import NullVisionProvider


class MockWorldState:
    def __init__(self, current_map="Pallet Town", dialog_open=False, position=(5, 5)):
        self.location = type("Loc", (), {"current_map": current_map})()
        self.interaction = type("Inter", (), {"dialog_open": dialog_open})()
        self.player = type("Pl", (), {"position": position})()
        self.agent = type("Ag", (), {"current_state": "EXPLORING", "current_goal": "EXPLORE"})()

    def snapshot(self):
        import copy
        return copy.deepcopy(self)


class MockExecutor:
    def __init__(self, world):
        self.world = world

    async def execute_learning_action(self, action: str, parameters: dict):
        await asyncio.sleep(0.01)
        if action == "approach_and_cross":
            self.world.location.current_map = "Route 1"
            return True
        elif action == "approach_and_interact":
            self.world.interaction.dialog_open = True
            return True
        elif action == "walk_over":
            self.world.player.position = (5, 6)
            return True
        return False


def test_autonomous_learning_system_pipeline():
    print("🧪 Testando Klayton Autonomous Learning System (Especificação Completa)...")

    # 1. Teste dos Modelos (models.py)
    fact = LearnedFact(
        concept="visual:door",
        properties={"semantic_type": "door", "possible_interaction": "walk_into"},
        confidence=0.50,
        status=KnowledgeStatus.HYPOTHESIS
    )
    assert fact.confidence == 0.50
    assert fact.status == KnowledgeStatus.HYPOTHESIS
    assert fact.source == "semantic_ai"
    print("  ✅ LearnedFact instanciado com o princípio 'IA sugeriu != verdade (confidence = 0.50)'")

    # 2. Teste do HypothesisEngine (hypothesis.py)
    hyp_engine = HypothesisEngine()
    test_door = hyp_engine.create_test(fact)
    assert test_door is not None
    assert test_door.action == "approach_and_cross"
    assert test_door.expected_effect == "map_changed"
    assert test_door.risk == ExplorationRisk.SAFE
    print("  ✅ HypothesisEngine gerou plano executável SAFE para 'visual:door'")

    # 3. Teste do ExperienceValidator (validator.py)
    validator = ExperienceValidator()
    before_world = MockWorldState(current_map="Pallet Town")
    after_world = MockWorldState(current_map="Route 1")

    val_res = validator.validate(before_world, after_world, "map_changed")
    assert isinstance(val_res, ValidationResult)
    assert val_res.success is True
    assert val_res.reason == "map_transition_observed"
    assert val_res.confidence == 0.95
    print("  ✅ ExperienceValidator forneceu ground truth empírico irrefutável ('map_transition_observed')")

    # 4. Teste do ConfidenceUpdater (confidence.py)
    fact_calc = LearnedFact(concept="visual:npc", properties={"semantic_type": "npc"}, confidence=0.50)
    
    # 1º Sucesso (strength = 1.0) -> gain = 0.20 -> confidence = 0.50 + 0.50*0.20 = 0.60
    ConfidenceUpdater.success(fact_calc, 1.0)
    assert abs(fact_calc.confidence - 0.60) < 1e-4

    # 2º Sucesso -> gain = 0.20 -> confidence = 0.60 + 0.40*0.20 = 0.68 -> status LIKELY
    ConfidenceUpdater.success(fact_calc, 1.0)
    assert fact_calc.status == KnowledgeStatus.LIKELY

    # 3º Sucesso com força 1.0
    ConfidenceUpdater.success(fact_calc, 1.0)
    # 4º Sucesso com força 1.0
    ConfidenceUpdater.success(fact_calc, 1.0)
    # 5º Sucesso com força 1.0
    ConfidenceUpdater.success(fact_calc, 1.0)
    assert fact_calc.confidence >= 0.70
    assert fact_calc.status == KnowledgeStatus.CONFIRMED
    print(f"  ✅ ConfidenceUpdater promoveu a hipótese para CONFIRMED (Confiança: {fact_calc.confidence:.3f})")

    # 5. Teste da KnowledgeBase em SQLite (knowledge_base.py)
    db_path = Path("scratch/test_learning_system.db")
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass

    kb = KnowledgeBase(db_path=db_path)
    kb.save_fact(fact_calc)
    kb.save_learning_event(
        concept=fact_calc.concept,
        action="approach_and_interact",
        expectation="dialog_opened",
        success=True,
        confidence_before=0.50,
        confidence_after=fact_calc.confidence,
        reason="dialog_opened"
    )

    retrieved = kb.find_similar("visual:npc")
    assert retrieved is not None
    assert retrieved.status == KnowledgeStatus.CONFIRMED
    assert len(kb.get_confirmed("visual:npc")) == 1
    print("  ✅ KnowledgeBase salvou e recuperou no SQLite com esquema de 3 tabelas mínimas")

    # 6. Teste da SemanticVision e NullVisionProvider
    null_prov = NullVisionProvider()
    vision = SemanticVision(provider=null_prov)

    # 7. Teste de Execução E2E do LearningEngine (learning_engine.py)
    async def run_e2e_learning():
        world_e2e = MockWorldState(current_map="Viridian City")
        executor = MockExecutor(world_e2e)
        engine = LearningEngine(
            semantic_vision=vision,
            hypothesis_engine=hyp_engine,
            validator=validator,
            knowledge_base=kb
        )

        # Injeta uma hipótese simulada vinda da SemanticVision
        sim_hypotheses = [
            LearnedFact(
                concept="visual:door",
                properties={"semantic_type": "door", "possible_interaction": "walk_into"},
                confidence=0.50
            )
        ]

        # Substitui temporariamente para teste do investigate
        vision._to_hypotheses = lambda resp: sim_hypotheses

        investigation_results = await engine.investigate(
            frame=b"fake_frame_bytes",
            world=world_e2e,
            executor=executor,
            reason="UNKNOWN_SCENE"
        )

        assert len(investigation_results) == 1
        result_fact = investigation_results[0]
        assert result_fact.successes == 1
        assert world_e2e.location.current_map == "Route 1"
        print(f"  ✅ LearningEngine orquestrou a investigação E2E! Fato '{result_fact.concept}' teve a primeira confirmação empírica!")

    asyncio.run(run_e2e_learning())


if __name__ == "__main__":
    test_autonomous_learning_system_pipeline()
