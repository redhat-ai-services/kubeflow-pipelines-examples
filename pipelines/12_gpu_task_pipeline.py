"""Example of a pipeline using a GPU."""

import os

import kfp.compiler
from kfp import dsl, kubernetes

from dotenv import load_dotenv

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="quay.io/modh/cuda-notebooks:cuda-jupyter-minimal-ubi9-python-3.11-20250326")
def nvidia_smi():
    """Use the nvidia-smi command to """
    import os

    os.system("nvidia-smi")


@dsl.pipeline()
def nvidia_smi_pipeline():
    """Pipeline to execute a task using GPUs
    """
    nvidia_smi_task = nvidia_smi()

    # Set the accelerator type and set the request/limit to 1
    # Note: You cannot request different values for the request/limit
    nvidia_smi_task.set_accelerator_type("nvidia.com/gpu").set_accelerator_limit(1)

    # Set the toleration for the GPU node
    kubernetes.add_toleration(nvidia_smi_task, key="nvidia.com/gpu", operator="Exists", effect="NoSchedule")


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
    result = client.create_run_from_pipeline_func(nvidia_smi_pipeline, arguments={}, experiment_name="iris")
    print(f"Starting pipeline run with run_id: {result.run_id}")
