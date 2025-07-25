"""Example of a pipeline to demonstrate running code built into the container image.

This pipeline uses the kfp.dsl.ContainerOp() function which throws some warnings.
Would be nice to find a better way to run code build into the container image.

This pipeline example is currently broken.
"""


import kfp.compiler
from kfp_helper import execute_pipeline_run


@kfp.dsl.pipeline(
    name="container-pipeline",
)
def add_pipeline(a: float = 1.0, b: float = 7.0):
    """Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    add_op = kfp.dsl.ContainerOp(  # noqa: F841
        name="add",
        image="quay.io/rhiap/kubeflow-example:latest",
        command=["sh", "-c"],
        arguments=["python components/add.py"],
    )


if __name__ == "__main__":
    arguments = {"a": 7.0, "b": 8.0}
    execute_pipeline_run(pipeline=add_pipeline, experiment="container-components-example", arguments=arguments)
