"""Example of a pipeline using a GPU."""

import os

import kfp.compiler
from kfp import dsl, kubernetes

from dotenv import load_dotenv

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


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

    # Set the accelerator type and set the request/limit to 1
    # Note: You cannot request different values for the request/limit
    first_add_task.set_accelerator_type("nvidia.com/gpu").set_accelerator_limit(1)

    # Set the toleration for the GPU node
    kubernetes.add_toleration(first_add_task, key="nvidia.com/gpu", operator="Exists", effect="NoSchedule")

    second_add_task = add(a=first_add_task.output, b=b)  # noqa: F841


if __name__ == "__main__":
    print(f"Connecting to kfp: {kubeflow_endpoint}")

    sa_token_path = "/run/secrets/kubernetes.io/serviceaccount/token"  # noqa: S105
    if "BEARER_TOKEN" in os.environ:
        bearer_token = os.environ["BEARER_TOKEN"]
    elif os.path.isfile(sa_token_path):
        with open(sa_token_path) as f:
            bearer_token = f.read().rstrip()

    # Check if the script is running in a k8s pod
    # Get the CA from the service account if it is
    # Skip the CA if it is not
    sa_ca_cert = "/run/secrets/kubernetes.io/serviceaccount/service-ca.crt"
    if os.path.isfile(sa_ca_cert) and "svc" in kubeflow_endpoint:
        ssl_ca_cert = sa_ca_cert
    else:
        ssl_ca_cert = None

    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
        ssl_ca_cert=ssl_ca_cert,
    )
    result = client.create_run_from_pipeline_func(add_pipeline, arguments={}, experiment_name="iris")
    print(f"Starting pipeline run with run_id: {result.run_id}")
