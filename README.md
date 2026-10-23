## 🏗️ Arquitetura e Configurações Técnicas

Para integrar o dbt a um projeto Python (gerenciado pelo `uv`) e orquestrado pelo Airflow, o projeto foi desenhado separando as responsabilidades em duas camadas: o **Ambiente Python** e o **Ambiente dbt**.

### 🏛️ 1. Decisões de Arquitetura (Os "Dois Mundos")
*   **Ambiente Python:** A pasta foi nomeada como `source/` (em vez de `src/`) para isolar os scripts de extração, carga e limpeza e a comunicação com APIs. O padrão `src/` é uma convenção estrita para bibliotecas Python, que não é o caso deste pipeline.
*   **Ambiente dbt:** Toda a estrutura do dbt para modelagem dimensional foi isolada na subpasta `/dbt`. Essa separação evita que arquivos `.yml` e `.sql` se misturem com os scripts `.py` do projeto principal, mantendo a raiz limpa.
*   **Otimização do `pyproject.toml`:** As diretivas `[build-system]` e `[project.scripts]` foram removidas. Como o `uv` atua exclusivamente no gerenciamento de dependências de um pipeline (e não no empacotamento de uma biblioteca), o arquivo foi simplificado.
uso de dbt utils para surrougate keys

### ⚙️ 2. Configurações Técnicas Necessárias

**Gerenciamento de Credenciais (`.env` e `.env.example`)**

A comunicação segura com os serviços externos (API e Amazon S3) é feita via arquivo `.env` na raiz do projeto (devidamente ignorado pelo Git). Para documentar quais variáveis são necessárias, o projeto inclui um **`.env.example`** como template:

```env
API_KEY=''
S3_BUCKET_NAME=''
AWS_ACCESS_KEY_ID=''
AWS_SECRET_ACCESS_KEY=''
```

**Acesso ao S3 e Execução do dbt**

*   **DuckDB como Motor (`profiles.yml`):** O projeto utiliza o DuckDB como engine de execução, configurado com dois ambientes (`dev` e `prod`) para separar o desenvolvimento local e a execução em produção. O ambiente `prod` foi configurado com um número maior de `threads` (4) para otimizar o processamento de dados.
*   **Extensões Nativas:** Para viabilizar a leitura e gravação de arquivos Parquet diretamente no S3, o perfil carrega as extensões `httpfs` (comunicação com o S3) e `parquet` (otimização do formato).
*   **Segurança e Região:** As credenciais da AWS são injetadas dinamicamente via `env_var()`, puxando as variáveis do `.env`. A região foi fixada em `sa-east-1` (São Paulo), garantindo a conformidade com a localização geográfica dos dados e reduzindo a latência nas requisições.
*   **Execução via Airflow com `--project-dir`:** Como o dbt está isolado na subpasta, o Airflow invoca os comandos a partir da raiz passando a flag `--project-dir dbt`. Isso garante que o dbt encontre a estrutura correta e carregue o `.env` da raiz sem erros de caminho.

<details>
<summary>Ver trecho do <code>profiles.yml</code> (clique para expandir)</summary>

```yaml
ValueMetrics:
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 1

    prod:
      type: duckdb
      path: prod.duckdb
      threads: 4

    extensions:
        - httpfs
        - parquet
        
    secrets:
      - type: s3
        region: "sa-east-1"
        key_id: "{{ env_var('AWS_ACCESS_KEY_ID') }}"
        secret: "{{ env_var('AWS_SECRET_ACCESS_KEY') }}"

  target: dev
```