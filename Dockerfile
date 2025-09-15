# Versão do airflow que não deu conflito de versão
FROM apache/airflow:2.8.4

# Usuário padrão do airflow
USER airflow

# Cópia dos requisitos para a pasta home
COPY requirements.txt /home/airflow/requirements.txt

# Instalação dos pacotes
RUN pip install --user --no-cache-dir -r /home/airflow/requirements.txt