FROM apache/airflow:2.5.1-python3.10
WORKDIR /app
ENV AIRFLOW_HOME=/opt/airflow/jl_airflow
ENV AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags
ENV AIRFLOW__CORE__PLUGINS_FOLDER=$AIRFLOW_HOME/plugins
ENV AIRFLOW__CORE__LOGS_FOLDER=$AIRFLOW_HOME/logs
ENV AIRFLOW__CORE__LOGGING_DAG_PROCESSOR_MANAGER_LOG_FILE=$AIRFLOW_HOME/logs/dag_processor_manager.log
COPY ../requirements.txt .
RUN pip install -r requirements.txt
COPY . .
