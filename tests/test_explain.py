"""Teste rápido do ExplainabilityEngine com LLM real."""

from dotenv import load_dotenv
import os

from src.parsing import parse_all
from src.skills import SkillExtractor
from src.scoring import ScoringEngine
from src.explainability import ExplainabilityEngine
from src.llm.client import GeminiClient

# Load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY nao encontrada")
    exit(1)

# Parse
job, candidates = parse_all("data/samples/job.txt", "data/samples/")

# Extract skills
extractor = SkillExtractor()
for c in candidates:
    extractor.extract_from_candidate(c)

# Score
scorer = ScoringEngine()
ranked = scorer.rank_candidates(candidates, job)

# Explain top 1
llm_client = GeminiClient(api_key=api_key, model="gemini-2.5-flash")
explainer = ExplainabilityEngine(llm_client=llm_client)

print(f"Gerando justificativa para: {ranked[0].name}")
print(f"Score: {ranked[0].score:.1f}")
print(f"LLM Client: {explainer.llm_client}")
print("-" * 60)

# Debug: print prompt
prompt = explainer._build_explanation_prompt(ranked[0], job, 1)
print("PROMPT:")
print(prompt[:500])
print("...")
print("-" * 60)

try:
    explanation = explainer.explain_candidate(candidate=ranked[0], job=job, position=1)
    print(explanation)
except Exception as e:
    print(f"ERRO: {e}")
    import traceback

    traceback.print_exc()
print("-" * 60)
print("Sucesso!")
