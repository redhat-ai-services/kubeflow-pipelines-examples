"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""


import kfp.compiler
from kfp import dsl, kubernetes
from kfp_helper import execute_pipeline_run


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
        secret_print_task,
        secret_name="my-secret", # noqa: S106
        secret_key_to_env={"my-secret-data": "my-secret-env-var"},  
    )

    cm_print_task = print_envvar(env_var="my-cm-env-var")
    cm_print_task.set_caching_options(False)
    kubernetes.use_config_map_as_env(
        cm_print_task, config_map_name="my-configmap", config_map_key_to_env={"my-configmap-data": "my-cm-env-var"}
    )


if __name__ == "__main__":
    execute_pipeline_run(pipeline=env_vars_pipeline, experiment="secrets-configmap-example", arguments={})
