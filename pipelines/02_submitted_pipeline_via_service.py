"""Example of a pipeline submitted directly to kfp."""
import os

from dotenv import load_dotenv

import kfp

import kfp_tekton

load_dotenv(override=True)

kubeflow_endpoint = "https://ds-pipeline-pipeline-defenition:9000"
bearer_token = os.environ["BEARER_TOKEN"]


def add(a: float, b: float) -> float:
    """Calculate the sum of the two arguments."""
    return a + b


add_op = kfp.components.create_component_from_func(
    add,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="Submitted Pipeline",
)
def add_pipeline(a="1", b="7"):
    """
    Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    first_add_task = add_op(a, 4)
    second_add_task = add_op(first_add_task.output, b)  # noqa: F841


if __name__ == "__main__":
    # Check if the script is running in a k8s pod
    # Read the service account token if it is
    # Get the bearer token from an env var if it is not
    # Note: The service account needs permission to access DSP instance in RBAC.
    sa_token_path = "/run/secrets/kubernetes.io/serviceaccount/token"
    if os.path.isfile(sa_token_path):
        with open(sa_token_path, "r") as f:
            token = f.read().rstrip()
    else:
        token = os.environ["BEARER_TOKEN"]

    # Check if the script is running in a k8s pod
    # Get the CA from the service account if it is
    # Skip the CA if it is not
    sa_ca_cert = "/run/secrets/kubernetes.io/serviceaccount/service-ca.crt"
    if os.path.isfile(sa_ca_cert):
        ssl_ca_cert = sa_ca_cert
    else:
        ssl_ca_cert = None

    client = kfp_tekton.TektonClient(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
        ssl_ca_cert=ssl_ca_cert,
    )

    arguments = {"a": "7", "b": "8"}
    client.create_run_from_pipeline_func(
        add_pipeline, arguments=arguments, experiment_name="submitted-example"
    )
