# OrbitSchedule - Documentação de Funcionamento e Estrutura de Código

## Visão Geral

`OrbitSchedule` é uma aplicação desktop em Python usando Tkinter para gerenciar e gerar uma grade horária escolar.

A aplicação permite:
- cadastrar professores, turmas e salas
- salvar e carregar os dados em arquivos CSV
- gerar uma grade horária automática
- exibir resultados em uma interface moderna com animações suaves
- exportar grade gerada para CSV
- zerar a grade exibida

## Principais Arquivos e Módulos

### `main.py`
Responsável pela interface principal da aplicação.

Funções principais:
- `SchedulerApp`: classe que monta a UI e controla a execução.
- `configure_style()`: configura tema, cores e estilo dos widgets.
- `create_main_tab()`: cria a aba principal com painel de métricas, botões e Treeview da grade.
- `create_professor_tab()`, `create_sala_tab()`, `create_turma_tab()`: criam as abas de gerenciamento.
- `gerar_grade()`: executa o algoritmo de geração de grade usando o `Scheduler`.
- `exportar_grade()`: abre diálogo para salvar a grade gerada em CSV.
- `clear_grade()`: limpa a grade gerada da interface e reseta o contador de aulas.
- `update_dashboard_summary()`: atualiza os números exibidos no painel (professores, turmas, salas e aulas).
- `start_ui_animation()` e `animate_ui()`: adicionam efeitos visuais dinâmicos ao layout.

Widgets principais:
- `ttk.Notebook` com abas: `Gerar Grade Horária`, `Gerenciar Professores`, `Gerenciar Salas`, `Gerenciar Turmas`
- `Treeview` para grade gerada
- indicadores de métricas de resumo
- área de alertas e status

### `data_handler.py`
Responsável pela leitura e escrita de arquivos CSV.

Classe `DataHandler` com métodos estáticos:
- `_read_csv(file_path)`: lê CSV e retorna lista de `dict`.
- `_write_csv(file_path, data, fieldnames)`: grava dados em CSV.
- `load_professores(file_path)`: carrega professores e transforma em objetos `Professor`.
- `save_professores(file_path, professores)`: salva objetos `Professor` em CSV.
- `load_turmas(file_path)`: carrega turmas e transforma em objetos `Turma`.
- `save_turmas(file_path, turmas)`: salva objetos `Turma` em CSV.
- `load_salas(file_path)`: carrega salas e transforma em objetos `Sala`.
- `save_salas(file_path, salas)`: salva objetos `Sala` em CSV.
- `save_grade(file_path, grade)`: exporta a grade gerada para CSV.

### `scheduler.py`
Implementa a lógica de geração da grade horária.

Classe `Scheduler`:
- define constantes: `DIAS`, `HORARIOS`, `BLOCOS`
- `gerar_grade()`: monta a grade usando turmas, professores e salas.
  - para cada turma, decide bloco de dia com base no nome
  - cria 20 aulas por turma com 5 disciplinas, 4 horários cada
  - busca professores disponíveis por disciplina, dia/bloco/horário
  - prioriza professor com menos aulas atribuídas
  - registra alertas quando não há alocação possível
- `_get_professores_disponiveis()`: retorna lista de professores habilitados e livres
- `_professor_ocupado()`: verifica conflito de horário para um professor
- `get_alertas()`: retorna alertas sem duplicados

### `models.py`
Define os modelos de dados usados na aplicação.

Classes dataclass:
- `Professor`:
  - `nome: str`
  - `disciplinas: List[str]`
  - `disponibilidade: List[str]`
  - `aulas_atribuidas: int`
- `Turma`:
  - `nome: str`
  - `carga_horaria: int`
  - `disciplinas: List[str]`
  - `sala_preferencial: str`
- `Sala`:
  - `numero: str`
  - `is_laboratorio: bool`
- `Aula`:
  - `dia: str`
  - `horario: int`
  - `bloco: str`
  - `turma: str`
  - `disciplina: str`
  - `professor: str`
  - `sala: str`

### `professor_manager.py`
Gerencia cadastro de professores e interação com o CSV.

Funcionalidades:
- leitura e escrita em `data/professores.csv`
- exibição em `Treeview`
- adicionar, atualizar e deletar professores
- preencher campos ao selecionar uma linha
- validações de campos obrigatórios e duplicidade de nome

### `sala_manager.py`
Gerencia cadastro de salas.

Funcionalidades:
- leitura e escrita em `data/salas.csv`
- exibição em `Treeview`
- adicionar, atualizar e deletar salas
- marca se a sala é laboratório
- atualiza opções de salas no `TurmaManager` quando salva mudanças

### `turma_manager.py`
Gerencia cadastro de turmas.

Funcionalidades:
- leitura e escrita em `data/turmas.csv`
- exibição em `Treeview`
- adicionar, atualizar e deletar turmas
- usa `Combobox` para selecionar sala preferencial
- validações para nome duplicado e sala válida
- regra de ocupação: máximo 2 turmas por sala, e se houver 2 turmas, disciplinas devem ser iguais

### `rounded_frame.py`
Implementa um `Canvas` customizado para componentes com bordas arredondadas.

Funcionalidades:
- `RoundedFrame` oferece layout com canto arredondado
- suporta `bg_color`, `border_color`, `corner_radius` e `padding`
- `set_border_color(color)`: permite alterar bordas dinamicamente para animação

## Estrutura de Dados e CSV

A pasta `data/` contém os arquivos:
- `professores.csv`
- `turmas.csv`
- `salas.csv`

Formato esperado:

### `professores.csv`
Campos:
- `nome`
- `disciplina` (valores separados por vírgula)
- `disponibilidade` (valores separados por vírgula, ex: `Segunda-Manhã, Terça-Noite`)

### `turmas.csv`
Campos:
- `nome`
- `carga_horaria` (inteiro)
- `disciplinas` (lista separada por vírgula)
- `sala` (sala preferencial)

### `salas.csv`
Campos:
- `numero_sala`
- `laboratorio` (`Sim`/`Não` ou valores aceitos em `load_salas` como `s`, `true`, `1`)

## Fluxo de Uso

1. Execute `python main.py`.
2. Cadastre `Professores`, `Salas` e `Turmas` nas abas correspondentes.
3. Clique em `Gerar Grade` na aba principal.
4. Verifique os alertas e a lista de aulas geradas.
5. Use `Exportar Grade CSV` para salvar o resultado.
6. Use `Zerar Aulas` para limpar a grade exibida.

## Comportamento do Gerador de Grade

- O algoritmo assume até 4 horários por dia e 5 dias por semana.
- Para cada turma são consideradas até 5 disciplinas.
- Cada disciplina recebe 4 aulas por semana, totalizando 20 slots por turma.
- Professores são escolhidos apenas se:
  - podem lecionar a disciplina
  - possuem disponibilidade no `dia-bloco`
  - não estão ocupados no mesmo horário
- Alocação prioriza o professor com menos aulas atribuídas.
- Se falhar a alocação, um alerta é registrado.

## Observações e Pontos Importantes

- O bloco (`Manhã`/`Noite`) da turma é inferido pelo nome da turma na implementação atual.
- A `carga_horaria` das turmas não é usada no algoritmo de forma completa, mas está registrada para ampliação futura.
- A interface foi atualizada para um visual mais moderno usando paleta escura e animações suaves.
- O gerenciamento de salas atualiza automaticamente o `Combobox` de `TurmaManager`.

## Como Estender o Projeto

Possíveis melhorias:
- adicionar campo `bloco` diretamente em `turmas.csv`
- refinar o algoritmo para respeitar `carga_horaria` real
- permitir múltiplas salas por turma
- implementar histórico de grades geradas
- adicionar filtros e pesquisa nas `Treeview`
- criar testes automatizados para `Scheduler`, `DataHandler` e managers

## Execução

Use o terminal no diretório do projeto:
```bash
python main.py
```

Se quiser rodar apenas uma verificação de sintaxe:
```bash
python -m py_compile main.py
```
