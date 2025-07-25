"""Example of a pipeline submitted directly to kfp using a shared function."""


from kfp import dsl
from kfp_helper import execute_pipeline_run


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def add(a: float, b: float) -> float:
    """Calculate the sum of the two arguments."""
    return a + b


@dsl.pipeline()
def add_pipeline(a: float = 1.0, b: float = 7.0):
    """Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    first_add_task = add(a=a, b=4.0)
    second_add_task = add(a=first_add_task.output, b=b)  # noqa: F841


if __name__ == "__main__":
    arguments = {"a": 7.0, "b": 8.0}
    execute_pipeline_run(pipeline=add_pipeline, experiment="submitted-example", arguments=arguments)
