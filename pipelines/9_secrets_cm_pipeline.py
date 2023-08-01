"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""
import os

from dotenv import load_dotenv

import kfp

import kfp_tekton

import kubernetes

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


def print_envvar(env_var: str):
    import os

    var_value = os.environ[env_var]
    print(f"my var value: {var_value}")


print_envvar_op = kfp.components.create_component_from_func(
    print_envvar,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="Env Vars Pipeline",
)
def env_vars_pipeline():
    """
    Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    secret_print_task = print_envvar_op("my-env-var")

    secret_print_task.add_env_variable(
        kubernetes.client.V1EnvVar(
            name="my-env-var",
            value_from=kubernetes.client.V1EnvVarSource(
                secret_key_ref=kubernetes.client.V1SecretKeySelector(
                    name="my-secret", key="my-secret-data"
                )
            ),
        )
    )

    cm_print_task = print_envvar_op("my-env-var")

    cm_print_task.add_env_variable(
        kubernetes.client.V1EnvVar(
            name="my-env-var",
            value_from=kubernetes.client.V1EnvVarSource(
                config_map_key_ref=kubernetes.client.V1ConfigMapKeySelector(
                    name="my-configmap", key="my-configmap-data"
                )
            ),
        )
    )


if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(
        env_vars_pipeline, arguments={}, experiment_name="secrets-configmap-example"
    )
