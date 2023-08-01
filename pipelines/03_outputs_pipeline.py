"""Example of a pipeline returning multiple values."""
import os
from typing import NamedTuple

from dotenv import load_dotenv

import kfp

import kfp_tekton

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


def return_multiple_values(
    a: float, b: float
) -> NamedTuple("outputs", [("sum", float), ("product", float)]):
    from collections import namedtuple

    sum = a + b
    product = a * b

    outputs = namedtuple("outputs", ["sum", "product"])
    return outputs(sum, product)


return_multiple_values_op = kfp.components.create_component_from_func(
    return_multiple_values,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="Submitted Pipeline",
)
def multiple_values_pipeline(a="1", b="7"):
    first_task = return_multiple_values_op(a, b)
    second_task = return_multiple_values_op(  # noqa: F841
        first_task.outputs["sum"], first_task.outputs["product"]
    )


if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    arguments = {"a": "7", "b": "8"}
    client.create_run_from_pipeline_func(
        multiple_values_pipeline,
        arguments=arguments,
        experiment_name="outputs-example",
    )
