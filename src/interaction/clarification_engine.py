"""
Clarification Engine - Solicitação de Clarificação
=================================================

Gerencia incertezas ou ambiguidades em comandos em linguagem natural ou no sistema de atenção.
Quando a confiança de interpretação estiver abaixo do limite seguro, o companheiro faz uma pergunta
para sanar a dúvida em vez de adivinhar incorretamente.

Autor: Klayton Companion Agent
Data: 2026-08-30
"""

from typing import Optional, List


class ClarificationEngine:
    """
    Motor de perguntas e esclarecimento social.
    """

    def generate_clarification_question(self, ambiguous_options: List[str]) -> str:
        """
        Gera uma pergunta verbal de esclarecimento para o usuário.
        Ex: options = ["O da esquerda", "O perto da água"] -> "Quer que eu vá pro da esquerda ou perto da água?"
        """
        if not ambiguous_options:
            return "Desculpe, não entendi bem. Pode repetir?"

        if len(ambiguous_options) == 2:
            return f"Você quer que eu vá pro {ambiguous_options[0]} ou {ambiguous_options[1]}?"

        options_str = ", ".join(ambiguous_options[:-1]) + f" ou {ambiguous_options[-1]}"
        return f"Qual deles você quer? {options_str}?"
