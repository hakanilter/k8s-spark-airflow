from airflow.operators.bash_operator import BashOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator


def get_spark_task(app_name, dag, ns="airflow"):

    submit = SparkKubernetesOperator(
        task_id=f"{app_name}_submit",
        namespace=ns,
        application_file=f"{app_name}.yaml",
        do_xcom_push=True,
        dag=dag,
    )

    monitor = SparkKubernetesSensor(
        task_id=f"{app_name}_monitor",
        namespace=ns,
        application_name="{{ task_instance.xcom_pull(task_ids='" + app_name + "_submit')['metadata']['name'] }}",
        dag=dag,
    )

    success = BashOperator(
        task_id=f"{app_name}_logs",
        bash_command=f"kubectl logs {app_name}-driver -n {ns}; " + 
            "kubectl delete SparkApplication {app_name} -n {ns}",
        dag=dag,
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    failure = BashOperator(
        task_id=f"{app_name}_logs",
        bash_command=f"kubectl logs {app_name}-driver -n {ns}; exit 1",
        dag=dag,
        trigger_rule=TriggerRule.ONE_FAILED
    )

    return [submit, monitor, (success, failure)]
