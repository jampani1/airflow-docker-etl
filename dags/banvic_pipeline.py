import datetime
import os
import pandas as pd
from airflow.models.dag import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

with DAG(
    dag_id='banvic_pipeline',
    start_date=datetime.datetime(2024, 1, 1),
    schedule_interval='35 4 * * *',
    catchup=False,
    tags=['ingestao', 'banvic', 'dw'],
) as dag:

    @task(task_id='extrair_csv')
    def extrair_csv():
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        data_path = '/opt/airflow/data_source/transacoes.csv'
        output_path = f'/opt/airflow/data_output/{hoje}/csv/transacoes.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df = pd.read_csv(data_path)
        df.to_csv(output_path, index=False)
        print(f"Arquivo CSV salvo em: {output_path}")

    @task(task_id='extrair_sql')
    def extrair_sql():
        hook = PostgresHook(postgres_conn_id='banvic_db_conn')
        conn = hook.get_conn()
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        output_path_base = f'/opt/airflow/data_output/{hoje}/sql/'
        os.makedirs(output_path_base, exist_ok=True)
        tabelas = [
            'agencias', 'clientes', 'colaborador_agencia',
            'colaboradores', 'contas', 'propostas_credito'
        ]
        for tabela in tabelas:
            df = pd.read_sql(f'SELECT * FROM public.{tabela}', conn)
            output_path = f'{output_path_base}{tabela}.csv'
            df.to_csv(output_path, index=False)
            print(f"Tabela {tabela} salva em: {output_path}")
        conn.close()

    @task(task_id='carregar_dw')
    def carregar_dw():
        hook = PostgresHook(postgres_conn_id='banvic_db_conn')
        conn = hook.get_conn()
        db_uri = hook.get_uri() # Forma necessária para o Pandas

        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS dw;")
        conn.commit()
        conn.close()
        
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        input_path_base = f'/opt/airflow/data_output/{hoje}/'
        
        print(f"Lendo arquivos de {input_path_base} para carregar no DW.")
        for root, dirs, files in os.walk(input_path_base):
            for file in files:
                if file.endswith('.csv'):
                    filepath = os.path.join(root, file)
                    df = pd.read_csv(filepath)
                    table_name = file.replace('.csv', '')
                    df.to_sql(
                        name=table_name,
                        con=db_uri, # Utilização de URI
                        schema='dw',
                        if_exists='replace',
                        index=False
                    )
                    print(f"Arquivo {file} carregado para a tabela dw.{table_name}")

    tarefa_extracao_csv = extrair_csv()
    tarefa_extracao_sql = extrair_sql()
    tarefa_carregamento = carregar_dw()
    [tarefa_extracao_csv, tarefa_extracao_sql] >> tarefa_carregamento