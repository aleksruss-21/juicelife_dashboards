FROM apache/airflow:2.5.1-python3.10
WORKDIR /app

ENV AIRFLOW_HOME=/app

ENV AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags
ENV AIRFLOW__CORE__PLUGINS_FOLDER=$AIRFLOW_HOME/plugins
ENV AIRFLOW__CORE__LOGS_FOLDER=$AIRFLOW_HOME/logs

#ENV AIRFLOW__CORE__LOGGING_DAG_PROCESSOR_MANAGER_LOG_FILE=$AIRFLOW_HOME/logs/dag_processor_manager.log
COPY ../requirements.txt .
COPY ../.env .
RUN pip install -r requirements.txt
COPY ./jl_airflow/dags dags
COPY ./jl_airflow/logs logs
COPY ./jl_airflow/plugins plugins
COPY ./cfg cfg
COPY ./telegram_bot telegram_bot
COPY ./service service
COPY ./storage storage
