# Verba na Minha Cidade

**Sistema de Transparencia de Emendas Parlamentares**

Um aplicativo web que permite ao cidadao consultar quanto seu municipio
recebeu em emendas parlamentares, de quais parlamentares, e para quais areas.

---

## Indice

1. [Visao Geral](#visao-geral)
2. [Arquitetura](#arquitetura)
3. [Fontes de Dados](#fontes-de-dados)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Documentacao dos Modulos](#documentacao-dos-modulos)
6. [Calculos e Metricas](#calculos-e-metricas)
7. [Como Executar](#como-executar)
8. [Glossario](#glossario)

---

## Visao Geral

### O que e este projeto?

Este e um MVP que democratiza o acesso a informacoes sobre emendas parlamentares no Brasil.

O cidadao digita o nome do seu municipio e recebe:

- Dados populacionais do IBGE
- Total de emendas recebidas pelo municipio
- Parlamentares que destinaram recursos
- Areas beneficiadas (saude, educacao, etc)
- Analise em linguagem natural gerada por IA

### Por que isso importa?

Emendas parlamentares sao recursos do orcamento federal que deputados e senadores destinam para estados e municipios. Em 2024, o Brasil destinou mais de R$ 50 bilhoes em emendas.

### Publico-alvo

- Cidadaos que querem saber sobre seu municipio
- Jornalistas investigativos
- Pesquisadores e academicos
- Organizacoes de transparencia
- Gestores publicos municipais

---

## Arquitetura

### Framework A.G.E.N.T.

| Componente | Arquivo | Funcao |
|------------|---------|--------|
| A - Identity | agent_identity.py | Define papel e limites do agente |
| G - Gear | llm.py + config.py | Motor IA Gemini |
| E - Execution | app.py | Orquestra todos os modulos |
| N - Navigation | guardrails.py | Seguranca e filtros |
| T - Testing | testes em cada modulo | Validacao |

### Framework SPAR

| Etapa | Arquivo | Descricao |
|-------|---------|-----------|
| Sensing | utils.py | Busca dados no BigQuery e IBGE |
| Planning | llm.py | Processa com Gemini |
| Acting | charts.py | Gera graficos |
| Reflecting | memory.py | Mantem contexto |

### Fluxo de Dados

| Passo | Acao | Modulo | Fonte |
|-------|------|--------|-------|
| 1 | Usuario digita municipio | app.py | Input |
| 2 | Valida entrada | guardrails.py | Filtros |
| 3 | Busca municipio | utils.py | BigQuery |
| 4 | Busca dados IBGE | utils.py | API IBGE |
| 5 | Busca populacao | utils.py | BigQuery |
| 6 | Busca emendas | utils.py | BigQuery CGU |
| 7 | Gera graficos | charts.py | Plotly |
| 8 | Gera narrativa | llm.py | Gemini |
| 9 | Exibe interface | app.py | Streamlit |

### Diagrama Visual

```mermaid
flowchart TD
A[Usuario] --> B[Validacao]
B --> C[Busca Municipio]
C --> D[API IBGE]
D --> E[Populacao]
E --> F[Emendas]
F --> G[Graficos]
G --> H[Narrativa IA]
H --> I[Interface]

Fontes de Dados
1. IBGE
Item	Valor
URL	servicodados.ibge.gov.br/api/v1/localidades
Dados	Nome, UF, microrregiao, mesorregiao
Atualizacao	Continua
2. Base dos Dados - BigQuery

Tabela Municipios

Dataset: basedosdados.br_bd_diretorios_brasil.municipio
Campos: id_municipio, nome, sigla_uf

Tabela Populacao

Dataset: basedosdados.br_ibge_populacao.municipio
Campos: id_municipio, ano, populacao

Tabela Emendas

Dataset: basedosdados.br_cgu_emendas_parlamentares.microdados
Campos: ano_emenda, nome_autor_emenda, valor_empenhado, valor_pago
Periodo: 2014 - atual
3. Google Gemini
Item	Valor
Modelo	Gemini 2.5 Flash
Uso	Geracao de narrativas
Custo	Gratuito ate 1M tokens/dia
Estrutura do Projeto
verba-na-minha-cidade/
├── .env                  # Variaveis de ambiente
├── .gitignore            # Arquivos ignorados
├── requirements.txt      # Dependencias
├── README.md             # Documentacao
├── config.py             # Configuracoes
├── agent_identity.py     # Identidade do agente
├── guardrails.py         # Seguranca
├── memory.py             # Memoria
├── utils.py              # Acesso a dados
├── llm.py                # Integracao Gemini
├── charts.py             # Graficos
└── app.py                # Interface

Documentacao dos Modulos
config.py

Proposito: Centralizar configuracoes.

Variavel	Descricao
GCP_PROJECT_ID	ID do projeto Google Cloud
GEMINI_API_KEY	Chave da API Gemini
CACHE_TTL_SECONDS	Tempo de cache (24h)
agent_identity.py

Proposito: Definir identidade do agente.

Nome: Verba - Analista de Transparencia
Papel: Jornalista de dados
Escopo: O que faz e nao faz
guardrails.py

Proposito: Seguranca contra ataques.

Funcao	Descricao
filtrar_entrada	Detecta injecao de prompt
filtrar_saida	Mascara dados sensiveis
validar_municipio	Valida caracteres
memory.py

Proposito: Manter contexto da sessao.

Metodo	Descricao
adicionar_interacao	Adiciona ao historico
definir_contexto_municipio	Define municipio atual
get_historico_formatado	Retorna historico
utils.py

Proposito: Acesso a dados.

Funcao	Fonte	Retorno
get_municipio_ibge	API IBGE	dict
get_populacao_municipio	BigQuery	dict
get_emendas_municipio	BigQuery	DataFrame
get_resumo_emendas	BigQuery	dict
get_emendas_por_ano	BigQuery	DataFrame
get_emendas_por_area	BigQuery	DataFrame
get_emendas_por_autor	BigQuery	DataFrame
llm.py

Proposito: Integracao com Gemini.

Funcao	Descricao
gerar_narrativa_municipio	Texto de 200-300 palavras
responder_pergunta	Resposta contextual
charts.py

Proposito: Visualizacoes.

Funcao	Tipo de Grafico
grafico_evolucao_anual	Linha
grafico_pizza_areas	Pizza
grafico_barras_areas	Barras horizontais
grafico_barras_autores	Barras horizontais
app.py

Proposito: Orquestrar tudo.

Fluxo:

Configuracao da pagina
Sidebar
Input do usuario
Validacoes
Busca municipio
Carrega dados
Exibe KPIs
Exibe graficos
Gera narrativa
Chat interativo
Calculos e Metricas
Per Capita
Per Capita = Total Empenhado / Populacao


Exemplo:

Empenhado: R$ 1.399.803
Populacao: 126.701
Per Capita: R$ 11,05
Taxa de Execucao
Execucao = (Total Pago / Total Empenhado) x 100


Exemplo:

Empenhado: R$ 1.000.000
Pago: R$ 750.000
Execucao: 75%
Como Executar
bash
# 1. Ative o ambiente
venv\Scripts\activate

# 2. Instale dependencias
pip install -r requirements.txt

# 3. Configure .env
GCP_PROJECT_ID=seu-projeto
GEMINI_API_KEY=sua-chave

# 4. Execute
streamlit run app.py

Glossario
Termo	Definicao
Emenda Parlamentar	Recurso destinado por deputados/senadores
Empenhado	Valor reservado no orcamento
Pago	Valor efetivamente transferido
Per Capita	Valor por habitante
IBGE	Instituto Brasileiro de Geografia e Estatistica
CGU	Controladoria-Geral da Uniao
BigQuery	Banco de dados Google
LLM	Modelo de linguagem
MVP	Produto minimo viavel
Licenca

Projeto educacional com dados publicos.


---

