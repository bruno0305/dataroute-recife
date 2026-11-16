# Regras do Pipeline · DataRoute Recife

Definidas pelo **F1 (Tech Lead)**. Todo código que entra na `main` segue estas regras. Elas valem pontos na rubrica (critério 2: *pipeline reprodutível com caminhos relativos*, 3,0 pts).

## 1. Caminhos: só relativos, sempre via `src/config.py`

```python
# ✅ CERTO
from src.config import BRONZE_DIR, SILVER_SINISTROS, FIGURAS_DIR
df = ler_csv_robusto(BRONZE_DIR / "sinistros_2023.csv")
fig.savefig(FIGURAS_DIR / "fig02_top10_bairros.png", dpi=DPI_FIGURAS)

# ❌ PROIBIDO
pd.read_csv("C:/Users/joao/Downloads/sinistros.csv")
pd.read_csv("/content/drive/MyDrive/bigdata/sinistros.csv")
```

O código não monta Google Drive nem usa `os.chdir` para pastas pessoais. Se o professor clonar o repositório e rodar `python -m src.pipeline`, tudo tem que funcionar.

## 2. Fluxo das camadas (Medalhão)

| Regra | Detalhe |
|---|---|
| Bronze é **somente leitura** | CSV baixado do portal vai para `data/raw/` como veio. Nunca editar à mão nem sobrescrever. |
| Cada camada lê **só a anterior** | Silver lê Bronze. Gold lê `sinistros_silver.csv`. Dataviz lê só as tabelas Gold. |
| Contrato é lei | A Silver precisa passar em `validar_silver` (colunas, tipos, zero duplicatas, turnos válidos). |
| Interface estável | Cada módulo mantém a função `run(...)`. Pode mudar o miolo, mas não a assinatura. |
| Toda limpeza é contabilizada | Cada regra nova da Silver registra quantas linhas afetou em `relatorio` (alimenta a tabela "Antes vs. Depois"). |

## 3. Padrões de dados

- **Arquivos:** `snake_case`, sem acento. Bronze: `<base>_<ano>.csv` (ex.: `sinistros_2022.csv`).
- **Colunas:** `snake_case`, sem acento (`natureza_acidente`, `vitimasfatais`).
- **Categorias** (bairro, clima, via): MAIÚSCULO, sem acento, espaço simples. Ausente vira `NAO INFORMADO`.
- **Saída:** CSV UTF-8, separador `,`, sem índice. Usar `salvar_csv()`.
- **Datas:** `datetime` na memória, ISO `AAAA-MM-DD` no disco.
- **Horário de pico (definição única):** 06h–08h59 e 17h–19h59 (`config.PICO_MANHA/PICO_TARDE`).
- **Severidade:** UPS — Unidade Padrão de Severidade (Programa PARE, Ministério dos Transportes, 2002): sem vítima = 1, com feridos = 4, feridos envolvendo pedestre = 6, com óbito = 13.
- **Figuras:** PNG em `docs/figuras/`, `dpi=300`, nome `figNN_descricao.png`.

## 4. Git

- `main` é protegida: sempre funcional. Ninguém faz *push* direto, a não ser o F1.
- Uma branch por função: `f2/ingestao`, `f3/silver`, `f4/eda`, `f5/dataviz`, `f6/docs`.
- Commits no padrão `tipo(camada): descrição`:
  - `feat(silver): padroniza grafia de bairros`
  - `fix(bronze): corrige leitura latin-1 de 2019`
  - `docs: atualiza dicionário de dados`
- Abra um Pull Request para a `main`. O F1 revisa e faz o merge (papel **A** da matriz RACI).
- Antes do PR, rode `python -m src.pipeline` sem erro.
- Notebooks: **Kernel → Restart & Run All** antes do commit, para as saídas ficarem na ordem certa.
- Não versionar arquivos acima de 100 MB (limite do GitHub). Bases de velocidade ficam no `.gitignore` e são baixadas pelo notebook 01.

## 5. Definição de Pronto (DoD) por camada

- [ ] **Bronze (F2):** CSVs em `data/raw/`, links em `bronze.FONTES`, volumetria (`df.info`, linhas, colunas, memória) e Dicionário de Dados no notebook 01.
- [ ] **Silver (F3):** `sinistros_silver.csv` gerado, `validar_silver` passando, tabela "Antes vs. Depois" pronta.
- [ ] **Gold (F4):** as 5 tabelas de `config.GOLD_ARQUIVOS` geradas e com estatística descritiva no notebook 03.
- [ ] **Dataviz (F5):** 5 a 6 figuras de 300 DPI em `docs/figuras/`, geradas a partir das tabelas Gold.
- [ ] **Pipeline (F1):** `python -m src.pipeline` roda do zero num clone limpo, local e no Colab.
