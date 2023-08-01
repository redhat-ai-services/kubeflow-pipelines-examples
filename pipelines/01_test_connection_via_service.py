"""Test showing a connection to kfp server using a service."""
import os

from dotenv import load_dotenv

import kfp_tekton

load_dotenv(override=True)

kubeflow_endpoint = "https://ds-pipeline-pipeline-defenition:9000"
bearer_token = os.environ["BEARER_TOKEN"]

if __name__ == "__main__":
    # Check if the script is running in a k8s pod
    # Read the service account token if it is
    # Get the bearer token from an env var if it is not
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
    print(client.list_experiments())
