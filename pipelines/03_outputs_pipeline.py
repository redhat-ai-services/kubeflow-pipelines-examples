"""Example of a pipeline returning multiple values."""

import os
from typing import NamedTuple

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def return_multiple_values(a: float, b: float) -> NamedTuple("outputs", [("sum", float), ("product", float)]):
    from collections import namedtuple

    sum_result = a + b
    product_result = a * b

    outputs = namedtuple("outputs", ["sum", "product"])
    return outputs(sum_result, product_result)


@kfp.dsl.pipeline(
    name="Submitted Pipeline",
)
def multiple_values_pipeline(a: float = 1.0, b: float = 7.0):
    first_task = return_multiple_values(a=a, b=b)
    second_task = return_multiple_values(  # noqa: F841
        a=first_task.outputs["sum"], b=first_task.outputs["product"]
    )


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )

    arguments = {"a": 7.0, "b": 8.0}
    client.create_run_from_pipeline_func(
        multiple_values_pipeline,
        arguments=arguments,
        experiment_name="outputs-example",
    )
