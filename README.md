# Desafio de Engenharia de Dados: Pipeline ETL para o Banco BanVic

## Introdução

Este projeto é a minha solução para o desafio de engenharia de dados proposto, que simula a criação de um pipeline de extração, transformação e carga (ETL) para o banco fictício BanVic. O objetivo é extrair dados de múltiplas fontes (um banco de dados SQL e um arquivo CSV), centralizá-los e carregá-los em um Data Warehouse para futuras análises.

Todo o ambiente foi desenvolvido utilizando Docker e Docker Compose para garantir a **reprodutibilidade**, um requisito fundamental do desafio.

## Arquitetura da Solução

O fluxo de dados segue a arquitetura abaixo, onde o Apache Airflow orquestra todo o processo de extração dos dados das fontes, o armazenamento temporário em um FileSystem local e o carregamento final no Data Warehouse em PostgreSQL.

```mermaid
graph TD;
    subgraph "Fontes de Dados"
        A(fa:fa-file-csv CSV);
        B(fa:fa-database SQL - PostgreSQL);
    end

    subgraph "Pipeline Orquestrado por Apache Airflow"
        C{Extração};
        D[FileSystem Local<br><i>(Área de Stage)</i>];
        E{Carregamento};
        F(fa:fa-warehouse Data Warehouse<br><i>PostgreSQL</i>);
    end

    A -- "transacoes.csv" --> C;
    B -- "Tabelas do ERP" --> C;
    C -- "Dados extraídos em CSV" --> D;
    D -- "Arquivos diários" --> E;
    E -- "Carga idempotente" --> F;
```

## 🛠️ Tecnologias Utilizadas

* **Orquestração:** Apache Airflow
* **Containerização:** Docker & Docker Compose
* **Bancos de Dados:** PostgreSQL
* **Linguagem:** Python
* **Bibliotecas Principais:** Pandas (para manipulação de dados), Psycopg2, SQLAlchemy

## 🚀 Como Executar o Projeto

Para executar este projeto em sua máquina local, siga os passos abaixo.

### Pré-requisitos

* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Passos para a Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jampani1/airflow-docker-etl]
    cd [EG_desafio]
    ```

2.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto, copiando o conteúdo do arquivo 

    Conteúdo do seu `.env` deve ser:
    ```
    AIRFLOW_UID=50000

    POSTGRES_AIRFLOW_USER=airflow
    POSTGRES_AIRFLOW_PASSWORD=airflow
    POSTGRES_AIRFLOW_DB=airflow_db

    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres_airflow_db:5432/airflow_db
    AIRFLOW__WEBSERVER__ALLOW_CONN_TEST=True
    ```

3.  **Suba o Ambiente Docker:**
    Execute o seguinte comando. Na primeira vez, ele irá construir a imagem customizada do Airflow, o que pode levar alguns minutos.
    ```bash
    docker-compose up -d --build
    ```

4.  **Acesse a Interface do Airflow:**
    Após a conclusão do comando, aguarde cerca de 1 a 2 minutos para que os serviços iniciem. Depois, acesse a interface no seu navegador:
    * **URL:** `http://localhost:8080`
    * **Usuário:** `admin`
    * **Senha:** `admin`

5.  **Execute a DAG:**
    * Na interface, encontre a DAG `banvic_pipeline`.
    * Ative-a no botão à esquerda.
    * Clique no ícone de "Play" (▶️) à direita e selecione "Trigger DAG" para iniciar a execução.

6.  **Verifique os Resultados:**
    Após a DAG rodar com sucesso, você pode verificar os dados carregados no Data Warehouse:
    ```bash
    docker-compose exec banvic_db psql -U data_engineer -d banvic
    ```
    Dentro do psql, execute:
    ```sql
    \dt dw.*;
    SELECT * FROM dw.clientes LIMIT 5;
    ```

## 📈 Estrutura do Pipeline (DAG)

A DAG `banvic_pipeline` foi implementada utilizando a TaskFlow API do Airflow e segue a lógica abaixo:

![Grafo da DAG](image_05b51e.png)

* **Extração em Paralelo:** As tarefas `extrair_csv` e `extrair_sql` rodam simultaneamente para otimizar o tempo de execução.
* **Carregamento Condicional:** A tarefa `carregar_dw` só é iniciada após a conclusão bem-sucedida de **ambas** as tarefas de extração, garantindo a consistência dos dados.
* **Idempotência:** A tarefa de carregamento utiliza a estratégia `if_exists='replace'`, o que torna o pipeline idempotente. Cada execução apaga os dados antigos e insere a nova carga completa.

## 🧠 Desafios e Aprendizados

A construção deste projeto foi uma jornada prática de aprendizado, especialmente na configuração do ambiente. Os principais desafios superados foram:

* **Conflitos de Versão:** O principal obstáculo foi diagnosticar e resolver um conflito de versão entre a biblioteca `pandas` e a versão do `Python` contida na imagem Docker oficial do Airflow. A solução envolveu um processo de depuração dos logs de `build` para identificar a incompatibilidade e ajustar o arquivo `requirements.txt` para usar versões que funcionassem em harmonia.
* **Configuração do Dockerfile:** A imagem do Airflow possui regras de segurança específicas para a instalação de pacotes. Foi um desafio encontrar a combinação correta de `Dockerfile`, versão da imagem base (`2.8.4-LTS`) e método de instalação (`pip install --user`) que resultasse em uma imagem customizada estável e funcional.
* **Conectividade entre Contêineres:** Foi necessário configurar uma rede Docker para permitir que os serviços do Airflow se comunicassem com o contêiner do banco de dados `banvic_db` usando os nomes dos serviços como `hostname`.

-------- 

## Desenvolvido por

🧑‍💻 Este projeto foi desenvolvido por mim, Maurício J Souza, como uma demonstração de habilidades em Engenharia de Dados (ED) e Docker!

Para considerações, perguntas ou oportunidades, sinta-se à vontade para entrar em contato:

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mauriciojampani/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mmjampani13@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jampani1)