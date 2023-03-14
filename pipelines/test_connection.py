import os

import urllib

import kfp

from dotenv import load_dotenv

load_dotenv()

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]

if __name__ == "__main__":
    client = kfp.Client(
        host=urllib.parse.urljoin(kubeflow_endpoint, "/pipeline"),
        existing_token=bearer_token,
    )
    print(client.list_experiments())
