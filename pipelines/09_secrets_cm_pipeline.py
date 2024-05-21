"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl
from kfp import kubernetes

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def print_envvar(env_var: str):
    import os

    var_value = os.environ[env_var]
    print(f"my var value: {var_value}")


@kfp.dsl.pipeline(
    name="Env Vars Pipeline",
)
def env_vars_pipeline():
    """Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    secret_print_task = print_envvar(env_var="my-secret-env-var")
    secret_print_task.set_caching_options(False)
    kubernetes.use_secret_as_env(
        secret_print_task, secret_name="my-secret", secret_key_to_env={"my-secret-data": "my-secret-env-var"}
    )

    cm_print_task = print_envvar(env_var="my-cm-env-var")
    cm_print_task.set_caching_options(False)
    kubernetes.use_config_map_as_env(
        cm_print_task, config_map_name="my-configmap", config_map_key_to_env={"my-configmap-data": "my-cm-env-var"}
    )


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(env_vars_pipeline, arguments={}, experiment_name="secrets-configmap-example")
