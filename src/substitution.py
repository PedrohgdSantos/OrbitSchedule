"""
Substitution finder for OrbitSchedule.

Given a registered Falta, searches the professor list for candidates who can
cover the absent professor's grade slots on that day, using the same availability
rules as the Scheduler (_get_professores_disponiveis).
"""
from dataclasses import dataclass, field
from typing import List, Dict
from .models import Falta, Aula, Professor


# Maps abbreviated weekday (stored in Falta.dia_semana) to full name (used in Aula.dia).
_ABBR_TO_FULL: Dict[str, str] = {
    "Seg": "Segunda", "Ter": "Terça",  "Qua": "Quarta",
    "Qui": "Quinta",  "Sex": "Sexta",
}
# Reverse map: full name → abbreviated form used in the professor UI.
# CORREÇÃO BUG 3: a UI de professores instrui o usuário a entrar "Seg-Manhã" (abreviado),
# mas o scheduler armazena aula.dia em nome completo "Segunda". Precisamos aceitar ambos.
_FULL_TO_ABBR: Dict[str, str] = {v: k for k, v in _ABBR_TO_FULL.items()}


@dataclass
class SubstituteOption:
    professor: Professor
    covers: List[Aula]    = field(default_factory=list)
    covers_all: bool      = False   # True when candidate covers every affected slot
    partial_count: int    = 0       # how many slots can be covered
    score: float          = 0.0     # higher is better


def affected_classes(falta: Falta, grade: List[Aula]) -> List[Aula]:
    """Return all grade slots that belong to the absent professor on the falta's weekday."""
    full_day = _ABBR_TO_FULL.get(falta.dia_semana, falta.dia_semana)
    return [
        a for a in grade
        if a.professor == falta.professor and a.dia == full_day
    ]


def find_substitutes(
    falta: Falta,
    grade: List[Aula],
    professores: List[Professor],
) -> List[SubstituteOption]:
    """
    Return candidates ranked best-first.

    A candidate is eligible for a slot when they:
      1. Teach the same disciplina as the affected class.
      2. Are listed as available for that exact "Dia-Bloco" (e.g. "Segunda-Manhã"),
         which is the same format used by the Scheduler.
      3. Are not already occupying that same (dia, horario) in the generated grade.

    Ranking:
      - Candidates who cover ALL affected slots come first.
      - Within each group, higher score (= more coverage − workload penalty) wins.
    """
    affected = affected_classes(falta, grade)
    if not affected:
        return []

    # Build conflict index: professor name → set of (dia, horario) already in grade.
    occupied: Dict[str, set] = {}
    for aula in grade:
        occupied.setdefault(aula.professor, set()).add((aula.dia, aula.horario))

    options: List[SubstituteOption] = []

    for prof in professores:
        if prof.nome == falta.professor:
            continue

        coverable: List[Aula] = []
        for aula in affected:
            # CORREÇÃO BUG 3: verifica disponibilidade nos dois formatos possíveis.
            # O scheduler usa nome completo ("Segunda-Manhã"), mas a UI de professores
            # orienta o usuário a digitar formato abreviado ("Seg-Manhã"). Aceitamos ambos.
            disp_full = f"{aula.dia}-{aula.bloco}"                  # "Segunda-Manhã"
            abbr_day  = _FULL_TO_ABBR.get(aula.dia, aula.dia)
            disp_abbr = f"{abbr_day}-{aula.bloco}"                  # "Seg-Manhã"

            is_available = (
                disp_full in prof.disponibilidade
                or disp_abbr in prof.disponibilidade
            )
            if not is_available:
                continue
            if (aula.dia, aula.horario) in occupied.get(prof.nome, set()):
                continue
            if aula.disciplina in prof.disciplinas:
                coverable.append(aula)

        if not coverable:
            continue

        covers_all = len(coverable) == len(affected)
        # Score: full coverage gives large bonus; partial coverage scales linearly.
        # Subtract a small workload penalty so lighter professors are preferred.
        score = (100.0 if covers_all else len(coverable) * 10.0) - prof.aulas_atribuidas * 0.5

        options.append(SubstituteOption(
            professor    = prof,
            covers       = coverable,
            covers_all   = covers_all,
            partial_count= len(coverable),
            score        = score,
        ))

    # Sort: full-coverage candidates first, then by score descending.
    options.sort(key=lambda o: (not o.covers_all, -o.score))
    return options
