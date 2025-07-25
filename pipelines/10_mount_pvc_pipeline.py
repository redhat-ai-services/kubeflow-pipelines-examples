"""Example of a pipeline to demonstrate mounting a pvc to a task in a pipeline."""


import kfp.compiler
from kfp import dsl, kubernetes
from kfp_helper import execute_pipeline_run


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def add(a: float, b: float) -> float:
    """Calculate the sum of the two arguments."""
    return a + b


@kfp.dsl.pipeline(
    name="PVC Pipeline",
)
def add_pipeline(a: float = 1.0, b: float = 7.0):
    """Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    first_add_task = add(a=a, b=4.0)
    kubernetes.mount_pvc(first_add_task, pvc_name="my-data", mount_path="/opt/data")

    second_add_task = add(a=first_add_task.output, b=b)  # noqa: F841


if __name__ == "__main__":
    arguments = {"a": 7.0, "b": 8.0}
    execute_pipeline_run(pipeline=add_pipeline, experiment="pvc-example", arguments=arguments)
