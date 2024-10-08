"""Test showing a basic connection to kfp server."""

import os

import kfp
from dotenv import load_dotenv

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]

if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    print(f"""The experiment list is as follows: 
          {client.list_experiments()}
            """)
    print(f""" The pipelines list is as follows:
          {client.list_pipelines()}""")
