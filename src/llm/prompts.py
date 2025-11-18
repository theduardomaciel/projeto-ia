"""
Gerenciador de prompts para o sistema
Carrega e formata templates de prompts
"""

import os
from typing import Dict, Optional
from pathlib import Path


class PromptManager:
    """Gerencia templates de prompts"""

    def __init__(self, templates_path: Optional[str] = None):
        """
        Inicializa o gerenciador de prompts

        Args:
            templates_path: Caminho para arquivo de templates
                          (padrão: data/config/prompt_templates.txt)
        """
        if templates_path is None:
            # Busca arquivo padrão
            project_root = Path(__file__).parent.parent.parent
            self.templates_path = (
                project_root / "data" / "config" / "prompt_templates.txt"
            )
        else:
            self.templates_path = Path(templates_path)
        self.templates: Dict[str, str] = {}
        self._load_templates()

    def _load_templates(self):
        """Carrega templates do arquivo"""
        if not self.templates_path.exists():
            print(
                f"Aviso: arquivo de templates não encontrado em {self.templates_path}"
            )
            return

        with open(self.templates_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse templates separados por "## Template N:"
        sections = content.split("## Template ")

        for section in sections[1:]:  # Pula primeira seção (cabeçalho)
            lines = section.strip().split("\n")

            # Primeira linha tem número e nome
            header = lines[0]

            # Extrai nome do template
            if ":" in header:
                name = header.split(":", 1)[1].strip()
            else:
                continue

            # Resto é o conteúdo do template
            template_content = "\n".join(lines[1:]).strip()

            # Remove separadores "---"
            template_content = template_content.replace("---\n", "").replace(
                "\n---", ""
            )

            self.templates[name.lower()] = template_content

    def get(self, template_name: str, **kwargs) -> str:
        """
        Retorna template formatado com variáveis substituídas

        Args:
            template_name: Nome do template (case-insensitive)
            **kwargs: Variáveis para substituir no template (ex: resume_text="...")

        Returns:
            Template formatado

        Raises:
            KeyError: Se template não encontrado
        """
        template_name = template_name.lower()

        if template_name not in self.templates:
            available = ", ".join(self.templates.keys())
            raise KeyError(
                f"Template '{template_name}' não encontrado. "
                f"Disponíveis: {available}"
            )

        template = self.templates[template_name]

        # Substitui variáveis {var_name}
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Variável {e} não fornecida para template '{template_name}'"
            )

    def list_templates(self) -> list[str]:
        """Retorna lista de templates disponíveis"""
        return list(self.templates.keys())

    def add_template(self, name: str, content: str):
        """
        Adiciona um novo template em runtime

        Args:
            name: Nome do template
            content: Conteúdo do template
        """
        self.templates[name.lower()] = content


# Instância global (singleton pattern)
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """
    Retorna instância singleton do PromptManager

    Returns:
        PromptManager configurado
    """
    global _prompt_manager

    if _prompt_manager is None:
        _prompt_manager = PromptManager()

    return _prompt_manager


def get_prompt(template_name: str, **kwargs) -> str:
    """
    Atalho para obter prompt formatado

    Args:
        template_name: Nome do template
        **kwargs: Variáveis do template

    Returns:
        Prompt formatado
    """
    return get_prompt_manager().get(template_name, **kwargs)
