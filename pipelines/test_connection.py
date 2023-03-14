"""Example pipeline showing a basic connection to kfp server."""
import os
import urllib

from dotenv import load_dotenv

import kfp_tekton

load_dotenv()

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]

if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=urllib.parse.urljoin(kubeflow_endpoint, "/pipeline"),
        existing_token=bearer_token,
    )
    print(client.list_experiments())
