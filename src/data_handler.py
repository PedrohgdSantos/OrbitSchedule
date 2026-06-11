import csv
from typing import List, Dict, Any
from .models import Professor, Turma, Sala, Aula, Falta


class DataHandler:

    @staticmethod
    def _read_csv(file_path: str) -> List[Dict[str, str]]:
        """Le CSV com suporte a UTF-8 com ou sem BOM."""
        data = []
        try:
            with open(file_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
        except FileNotFoundError:
            pass
        return data

    @staticmethod
    def _write_csv(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str]):
        """Escreve CSV interno com UTF-8-BOM."""
        with open(file_path, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    # ── Professores ────────────────────────────────────────────────────────────

    @staticmethod
    def load_professores(file_path: str) -> List[Professor]:
        professores = []
        for row in DataHandler._read_csv(file_path):
            disciplinas     = [d.strip() for d in row.get("disciplina", "").split(",") if d.strip()]
            disponibilidade = [d.strip() for d in row.get("disponibilidade", "").split(",") if d.strip()]
            professores.append(Professor(row.get("nome", ""), disciplinas, disponibilidade))
        return professores

    @staticmethod
    def save_professores(file_path: str, professores: List[Professor]):
        DataHandler._write_csv(
            file_path,
            [{"nome": p.nome, "disciplina": ",".join(p.disciplinas), "disponibilidade": ",".join(p.disponibilidade)}
             for p in professores],
            ["nome", "disciplina", "disponibilidade"],
        )

    # ── Turmas ─────────────────────────────────────────────────────────────────

    @staticmethod
    def load_turmas(file_path: str) -> List[Turma]:
        turmas = []
        for row in DataHandler._read_csv(file_path):
            disciplinas = [d.strip() for d in row.get("disciplinas", "").split(",") if d.strip()]
            turmas.append(Turma(
                row.get("nome", ""),
                int(row.get("carga_horaria", 0)),
                disciplinas,
                row.get("sala", ""),
            ))
        return turmas

    @staticmethod
    def save_turmas(file_path: str, turmas: List[Turma]):
        DataHandler._write_csv(
            file_path,
            [{"nome": t.nome, "carga_horaria": t.carga_horaria,
              "disciplinas": ",".join(t.disciplinas), "sala": t.sala_preferencial}
             for t in turmas],
            ["nome", "carga_horaria", "disciplinas", "sala"],
        )

    # ── Salas ──────────────────────────────────────────────────────────────────

    @staticmethod
    def load_salas(file_path: str) -> List[Sala]:
        salas = []
        for row in DataHandler._read_csv(file_path):
            is_lab = row.get("laboratorio", "").lower() in ["sim", "s", "true", "1"]
            salas.append(Sala(row.get("numero_sala", ""), is_lab))
        return salas

    @staticmethod
    def save_salas(file_path: str, salas: List[Sala]):
        DataHandler._write_csv(
            file_path,
            [{"numero_sala": s.numero, "laboratorio": "Sim" if s.is_laboratorio else "Nao"}
             for s in salas],
            ["numero_sala", "laboratorio"],
        )

    # ── Faltas ─────────────────────────────────────────────────────────────────

    @staticmethod
    def load_faltas(file_path: str) -> List[Falta]:
        faltas = []
        for row in DataHandler._read_csv(file_path):
            faltas.append(Falta(
                data=row.get("data", ""),
                professor=row.get("professor", ""),
                dia_semana=row.get("dia_semana", ""),
                bloco=row.get("bloco", ""),
                horario=row.get("horario", ""),
                motivo=row.get("motivo", ""),
                registrado_em=row.get("registrado_em", ""),
                substituto=row.get("substituto", ""),
            ))
        return faltas

    @staticmethod
    def save_faltas(file_path: str, faltas: List[Falta]):
        FIELDS = ["data", "professor", "dia_semana", "bloco", "horario",
                  "motivo", "registrado_em", "substituto"]
        DataHandler._write_csv(
            file_path,
            [{"data": f.data, "professor": f.professor, "dia_semana": f.dia_semana,
              "bloco": f.bloco, "horario": f.horario, "motivo": f.motivo,
              "registrado_em": f.registrado_em, "substituto": f.substituto}
             for f in faltas],
            FIELDS,
        )

    # ── Grade (export CSV para usuario) ───────────────────────────────────────

    @staticmethod
    def save_grade(file_path: str, grade: List[Aula]):
        """Exporta a grade em CSV com UTF-8-BOM e separador ; (compativel com Excel PT-BR)."""
        fieldnames = ["Dia", "Horario", "Bloco", "Turma", "Disciplina", "Professor", "Sala"]
        with open(file_path, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for aula in grade:
                writer.writerow({
                    "Dia": aula.dia,
                    "Horario": f"{aula.horario}o Horario",
                    "Bloco": aula.bloco,
                    "Turma": aula.turma,
                    "Disciplina": aula.disciplina,
                    "Professor": aula.professor,
                    "Sala": aula.sala,
                })
