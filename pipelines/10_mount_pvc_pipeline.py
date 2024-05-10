"""
Example of a pipeline to demonstrate mounting a pvc to a task in a pipeline.

This pipeline example is currently broken.
"""

import os

from dotenv import load_dotenv

from kfp import dsl
import kfp.compiler

import kubernetes

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest"
)
def add(a: float, b: float) -> float:
    """Calculate the sum of the two arguments."""
    return a + b


@kfp.dsl.pipeline(
    name="PVC Pipeline",
)
def add_pipeline(a: float = 1.0, b: float = 7.0):
    """
    Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    first_add_task = add(a=a, b=4.0)

    vol = kubernetes.client.V1Volume(
        name="my-data",
        persistent_volume_claim=kubernetes.client.V1PersistentVolumeClaimVolumeSource(
            claim_name="my-data"
        ),
    )

    first_add_task.add_pvolumes({"/opt/data": vol})

    second_add_task = add(a=first_add_task.output, b=b)  # noqa: F841


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    arguments = {"a": 7.0, "b": 8.0}
    client.create_run_from_pipeline_func(
        add_pipeline, arguments=arguments, experiment_name="pvc-example"
    )
