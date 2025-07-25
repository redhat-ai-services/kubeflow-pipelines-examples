import os
import sys

import kfp.compiler
from dotenv import load_dotenv
from kfp.components import BaseComponent
from loguru import logger

load_dotenv(override=True)


def execute_pipeline_run(pipeline: BaseComponent, experiment: str, arguments: dict | None = None):
    kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]

    logger.info(f"Connecting to kfp: {kubeflow_endpoint}")

    sa_token_path = "/run/secrets/kubernetes.io/serviceaccount/token"  # noqa: S105
    if "BEARER_TOKEN" in os.environ:
        logger.debug("BEARER_TOKEN provided as environment variable")
        bearer_token = os.environ["BEARER_TOKEN"]
    elif os.path.isfile(sa_token_path):
        logger.debug("BEARER_TOKEN found as service account token")
        with open(sa_token_path) as f:
            bearer_token = f.read().rstrip()

    # Check if the script is running in a k8s pod
    # Get the CA from the service account if it is
    # Skip the CA if it is not
    sa_ca_cert = "/run/secrets/kubernetes.io/serviceaccount/service-ca.crt"
    if os.path.isfile(sa_ca_cert) and "svc" in kubeflow_endpoint:
        logger.debug("CA Cert found in container")
        ssl_ca_cert = sa_ca_cert
    else:
        ssl_ca_cert = None

    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
        ssl_ca_cert=ssl_ca_cert,
    )
    result = client.create_run_from_pipeline_func(pipeline, arguments=arguments, experiment_name=experiment)
    logger.info(f"Starting pipeline run with run_id: {result.run_id}")


def compile_pipeline(pipeline: BaseComponent):
    logger.info("Compiling pipeline")
    kfp.compiler.Compiler().compile(pipeline, package_path=sys.argv[0].replace(".py", ".yaml"))
