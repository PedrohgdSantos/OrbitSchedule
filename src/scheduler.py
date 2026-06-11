from typing import List, Dict, Optional
from .models import Professor, Turma, Sala, Aula

# A classe Scheduler é responsável por gerar a grade horária, aplicando as regras de negócio.
class Scheduler:
    # Constantes que definem os dias da semana, horários e blocos disponíveis.
    DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    HORARIOS = [1, 2, 3, 4] # Representa os 4 horários de aula por bloco.
    BLOCOS = ["Manhã", "Noite"]

    def __init__(self, professores: List[Professor], turmas: List[Turma], salas: List[Sala]):
        """Inicializa o Scheduler com as listas de professores, turmas e salas."""
        self.professores = professores
        self.turmas = turmas
        self.salas = salas
        self.grade: List[Aula] = []  # Lista para armazenar as aulas geradas.
        self.alertas = []  # Lista para armazenar mensagens de alerta sobre a geração da grade.

    def gerar_grade(self) -> List[Aula]:
        """Gera a grade horária completa, alocando aulas para todas as turmas.
        
        Retorna uma lista de objetos Aula que compõem a grade horária gerada.
        """
        self.grade = []  # Limpa a grade anterior a cada nova geração.
        self.alertas = [] # Limpa os alertas anteriores.
        
        # Reinicia a contagem de aulas atribuídas a cada professor.
        for p in self.professores:
            p.aulas_atribuidas = 0

        # Itera sobre cada turma para preencher seus horários.
        for turma in self.turmas:
            # Determina o bloco da turma (Manhã ou Noite) com base no nome da turma.
            # Esta é uma simplificação; em um sistema real, o bloco viria do CSV da turma.
            bloco = "Noite" if "Noite" in turma.nome else "Manhã"
            
            # Seleciona as primeiras 5 disciplinas da turma, conforme o requisito de 5 disciplinas por turma.
            disciplinas_da_turma = turma.disciplinas[:5]
            
            # Prepara a lista de disciplinas intercalando-as por dia: [D1,D2,D3,D4,D5, D1,D2,...]
            # Distribuição determinística — sem random — garante que a grade é idêntica
            # a cada geração, tornando relatórios e gráficos estáveis e reproduzíveis.
            disciplinas_para_alocar = []
            for i in range(4):           # 4 aulas por disciplina
                for d in disciplinas_da_turma:
                    disciplinas_para_alocar.append(d)
            
            # Itera sobre cada dia da semana e cada horário para tentar alocar uma aula.
            for dia in self.DIAS:
                for h in self.HORARIOS:
                    # Se não houver mais disciplinas para alocar, sai do loop.
                    if not disciplinas_para_alocar:
                        break
                    
                    sucesso = False # Flag para indicar se uma aula foi alocada neste slot.
                    # Tenta encontrar um professor disponível para uma das disciplinas restantes.
                    for i, disciplina in enumerate(disciplinas_para_alocar):
                        # Busca professores que podem lecionar a disciplina e estão disponíveis no dia/bloco/horário.
                        prof_disponiveis = self._get_professores_disponiveis(disciplina, dia, bloco, h)
                        
                        if prof_disponiveis:
                            # Regra de negócio: O professor com menos aulas atribuídas tem prioridade.
                            prof_disponiveis.sort(key=lambda p: p.aulas_atribuidas)
                            professor = prof_disponiveis[0] # Seleciona o professor com maior prioridade.
                            
                            # Cria um objeto Aula com os detalhes da aula agendada.
                            aula = Aula(
                                dia=dia,
                                horario=h,
                                bloco=bloco,
                                turma=turma.nome,
                                disciplina=disciplina,
                                professor=professor.nome,
                                sala=turma.sala_preferencial # Usa a sala preferencial da turma.
                            )
                            
                            self.grade.append(aula) # Adiciona a aula à grade.
                            professor.aulas_atribuidas += 1 # Incrementa o contador de aulas do professor.
                            disciplinas_para_alocar.pop(i) # Remove a disciplina da lista de pendentes.
                            sucesso = True
                            break # Sai do loop de disciplinas e vai para o próximo horário.
                    
                    if not sucesso:
                        # Se nenhuma disciplina pôde ser alocada neste horário (falta de professor, etc.).
                        # Adiciona um alerta informando sobre a impossibilidade de alocação.
                        self.alertas.append(f"Falta de professor disponível para as aulas de {disciplina} da {turma.nome} na {dia} ({bloco}) às {h}º horário.")
                        # Remove uma disciplina da lista de pendentes para evitar loops infinitos, mesmo que não tenha sido alocada.
                        if disciplinas_para_alocar:
                            disciplinas_para_alocar.pop(0)

        return self.grade

    def _get_professores_disponiveis(self, disciplina: str, dia: str, bloco: str, horario: int) -> List[Professor]:
        """Retorna uma lista de professores disponíveis para uma dada disciplina, dia, bloco e horário."""
        disponiveis = []
        disp_str = f"{dia}-{bloco}" # Formato da string de disponibilidade (ex: "Segunda-Manhã").
        
        for p in self.professores:
            # Verifica se o professor pode lecionar a disciplina.
            if disciplina in p.disciplinas:
                # Verifica se o professor está disponível no bloco do dia.
                if disp_str in p.disponibilidade:
                    # Verifica se o professor já não está ocupado em outra aula neste exato horário.
                    if not self._professor_ocupado(p.nome, dia, bloco, horario):
                        disponiveis.append(p) # Adiciona o professor à lista de disponíveis.
        return disponiveis

    def _professor_ocupado(self, nome_prof: str, dia: str, bloco: str, horario: int) -> bool:
        """Verifica se um professor já está ocupado em uma aula agendada no mesmo dia, bloco e horário."""
        for aula in self.grade:
            # Compara o nome do professor, dia, bloco e horário da aula existente com os parâmetros fornecidos.
            if aula.professor == nome_prof and aula.dia == dia and aula.bloco == bloco and aula.horario == horario:
                return True # O professor está ocupado.
        return False # O professor não está ocupado.

    def get_alertas(self) -> List[str]:
        """Retorna a lista de alertas gerados durante a criação da grade, removendo duplicatas."""
        # Usa um conjunto (set) para armazenar alertas já vistos e garantir que não haja duplicatas.
        seen = set()
        # Retorna uma nova lista com alertas únicos, mantendo a ordem de descoberta.
        return [x for x in self.alertas if not (x in seen or seen.add(x))]
