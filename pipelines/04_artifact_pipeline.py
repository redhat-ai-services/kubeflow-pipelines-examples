"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def create_artifact(my_artifact: dsl.Output[dsl.Artifact]):
    import pickle

    artifact = "1, 2, 3, 4"

    with open(my_artifact.path, "bw") as f:
        pickle.dump(artifact, f)


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def consume_artifact(my_artifact: dsl.Input[dsl.Artifact]):
    import pickle

    with open(my_artifact.path, "br") as f:
        artifact = pickle.load(f)  # noqa: S301

    print(artifact)


@kfp.dsl.pipeline(
    name="Artifact Pipeline",
)
def artifact_pipeline():
    create_artifact_task = create_artifact()
    consume_artifact_task = consume_artifact(  # noqa: F841
        my_artifact=create_artifact_task.outputs["my_artifact"]
    )


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(artifact_pipeline, arguments={}, experiment_name="artifact-example")
