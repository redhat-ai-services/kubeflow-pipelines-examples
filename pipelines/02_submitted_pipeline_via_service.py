"""Example of a pipeline submitted directly to kfp."""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = "https://ds-pipeline-dspa:8443"


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
    # Check if the script is running in a k8s pod
    # Read the service account token if it is
    # Get the bearer token from an env var if it is not
    # Note: The service account needs permission to access DSP instance in RBAC.
    sa_token_path = "/run/secrets/kubernetes.io/serviceaccount/token"  # noqa: S105
    if os.path.isfile(sa_token_path):
        with open(sa_token_path) as f:
            bearer_token = f.read().rstrip()
    else:
        bearer_token = os.environ["BEARER_TOKEN"]

    # Check if the script is running in a k8s pod
    # Get the CA from the service account if it is
    # Skip the CA if it is not
    sa_ca_cert = "/run/secrets/kubernetes.io/serviceaccount/service-ca.crt"
    if os.path.isfile(sa_ca_cert):
        ssl_ca_cert = sa_ca_cert
    else:
        ssl_ca_cert = None

    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
        ssl_ca_cert=ssl_ca_cert,
    )

    arguments = {"a": 7.0, "b": 8.0}
    client.create_run_from_pipeline_func(add_pipeline, arguments=arguments, experiment_name="submitted-example")
