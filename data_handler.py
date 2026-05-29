import csv
from typing import List, Dict, Type, Any
from models import Professor, Turma, Sala, Aula

# A classe DataHandler é responsável por ler e escrever dados em arquivos CSV.
# Ela contém métodos estáticos, o que significa que podem ser chamados diretamente da classe sem criar uma instância.
class DataHandler:

    @staticmethod
    def _read_csv(file_path: str) -> List[Dict[str, str]]:
        """Método auxiliar para ler um arquivo CSV e retornar uma lista de dicionários."""
        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            # Se o arquivo não existir, retorna uma lista vazia, o que é útil para inicializar.
            pass
        return data

    @staticmethod
    def _write_csv(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str]):
        """Método auxiliar para escrever uma lista de dicionários em um arquivo CSV."""
        with open(file_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def load_professores(file_path: str) -> List[Professor]:
        """Carrega os dados dos professores de um arquivo CSV e os converte em objetos Professor."""
        professores = []
        raw_data = DataHandler._read_csv(file_path)
        for row in raw_data:
            # Processa a coluna ‘disciplina’: divide a string por vírgulas e remove espaços em branco.
            disciplinas = [d.strip() for d in row.get('disciplina', '').split(',') if d.strip()]
            # Processa a coluna ‘disponibilidade’ de forma similar.
            disponibilidade = [d.strip() for d in row.get('disponibilidade', '').split(',') if d.strip()]
            # Cria um objeto Professor e o adiciona à lista.
            professores.append(Professor(row.get('nome', ''), disciplinas, disponibilidade))
        return professores

    @staticmethod
    def save_professores(file_path: str, professores: List[Professor]):
        """Salva uma lista de objetos Professor em um arquivo CSV."""
        data_to_write = []
        for p in professores:
            data_to_write.append({
                'nome': p.nome,
                'disciplina': ','.join(p.disciplinas),
                'disponibilidade': ','.join(p.disponibilidade)
            })
        fieldnames = ['nome', 'disciplina', 'disponibilidade']
        DataHandler._write_csv(file_path, data_to_write, fieldnames)

    @staticmethod
    def load_turmas(file_path: str) -> List[Turma]:
        """Carrega os dados das turmas de um arquivo CSV e os converte em objetos Turma."""
        turmas = []
        raw_data = DataHandler._read_csv(file_path)
        for row in raw_data:
            # Processa a coluna ‘disciplinas’.
            disciplinas = [d.strip() for d in row.get('disciplinas', '').split(',') if d.strip()]
            # Cria um objeto Turma, convertendo ‘carga_horaria’ para inteiro.
            turmas.append(Turma(
                row.get('nome', ''),
                int(row.get('carga_horaria', 0)),
                disciplinas,
                row.get('sala', '')
            ))
        return turmas

    @staticmethod
    def save_turmas(file_path: str, turmas: List[Turma]):
        """Salva uma lista de objetos Turma em um arquivo CSV."""
        data_to_write = []
        for t in turmas:
            data_to_write.append({
                'nome': t.nome,
                'carga_horaria': t.carga_horaria,
                'disciplinas': ','.join(t.disciplinas),
                'sala': t.sala_preferencial
            })
        fieldnames = ['nome', 'carga_horaria', 'disciplinas', 'sala']
        DataHandler._write_csv(file_path, data_to_write, fieldnames)

    @staticmethod
    def load_salas(file_path: str) -> List[Sala]:
        """Carrega os dados das salas de um arquivo CSV e os converte em objetos Sala."""
        salas = []
        raw_data = DataHandler._read_csv(file_path)
        for row in raw_data:
            # Verifica se a sala é um laboratório com base em várias possíveis entradas (case-insensitive).
            is_lab = row.get('laboratorio', '').lower() in ['sim', 's', 'true', '1']
            # Cria um objeto Sala.
            salas.append(Sala(row.get('numero_sala', ''), is_lab))
        return salas

    @staticmethod
    def save_salas(file_path: str, salas: List[Sala]):
        """Salva uma lista de objetos Sala em um arquivo CSV."""
        data_to_write = []
        for s in salas:
            data_to_write.append({
                'numero_sala': s.numero,
                'laboratorio': 'Sim' if s.is_laboratorio else 'Não'
            })
        fieldnames = ['numero_sala', 'laboratorio']
        DataHandler._write_csv(file_path, data_to_write, fieldnames)

    @staticmethod
    def save_grade(file_path: str, grade: List[Aula]):
        """Salva a grade horária gerada em um arquivo CSV."""
        # Abre o arquivo CSV no modo de escrita (‘w’) com codificação UTF-8 e newline=’’ para evitar linhas em branco extras.
        with open(file_path, mode='w', encoding='utf-8', newline='') as f:
            # Define os nomes dos campos (cabeçalhos) para o arquivo CSV de saída.
            fieldnames = ['Dia', 'Horário', 'Bloco', 'Turma', 'Disciplina', 'Professor', 'Sala']
            # Cria um objeto DictWriter para escrever dicionários como linhas CSV.
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()  # Escreve a linha de cabeçalho no arquivo.
            for aula in grade:
                # Para cada objeto Aula na grade, escreve uma linha no CSV.
                writer.writerow({
                    'Dia': aula.dia,
                    'Horário': f"{aula.horario}º Horário", # Formata o horário para melhor leitura.
                    'Bloco': aula.bloco,
                    'Turma': aula.turma,
                    'Disciplina': aula.disciplina,
                    'Professor': aula.professor,
                    'Sala': aula.sala
                })
