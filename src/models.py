# Importa os módulos necessários para a criação de classes de dados e tipagem.
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Define a classe Professor usando dataclass para simplificar a criação de objetos.
@dataclass
class Professor:
    nome: str  # Nome do professor.
    disciplinas: List[str]  # Lista de disciplinas que o professor pode lecionar.
    disponibilidade: List[str]  # Lista de horários em que o professor está disponível (ex: ["Segunda-Manhã", "Terça-Manhã"]).
    aulas_atribuidas: int = 0  # Contador de aulas atribuídas ao professor, inicializado em 0. Usado para a regra de prioridade.

# Define a classe Turma.
@dataclass
class Turma:
    nome: str  # Nome da turma (ex: "Turma A").
    carga_horaria: int  # Carga horária semanal da turma (não totalmente utilizada no algoritmo atual, mas importante para requisitos futuros).
    disciplinas: List[str]  # Lista de disciplinas que a turma deve cursar.
    sala_preferencial: str  # Sala preferencial para esta turma.

# Define a classe Sala.
@dataclass
class Sala:
    numero: str  # Número ou identificador da sala.
    is_laboratorio: bool  # Booleano indicando se a sala é um laboratório (True) ou uma sala de aula comum (False).

# Define a classe Falta, que representa a ausência registrada de um professor.
@dataclass
class Falta:
    data: str           # "11/06/2024"
    professor: str
    dia_semana: str     # "Seg", "Ter", etc.
    bloco: str          # "Manhã", "Tarde", "Noite"
    horario: str        # "1" ou "—" se desconhecido
    motivo: str
    registrado_em: str  # "11/06/2024 14:30"

# Define a classe Aula, que representa uma aula agendada.
@dataclass
class Aula:
    dia: str  # Dia da semana da aula (ex: "Segunda").
    horario: int  # Número do horário da aula no dia (ex: 1 para o primeiro horário, 4 para o quarto).
    bloco: str    # Bloco do dia (ex: "Manhã" ou "Noite").
    turma: str  # Nome da turma que terá a aula.
    disciplina: str  # Nome da disciplina da aula.
    professor: str  # Nome do professor que ministrará a aula.
    sala: str  # Número da sala onde a aula será realizada.
