"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""
import os
import urllib

from dotenv import load_dotenv

import kfp

import kfp_tekton


load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


def create_artifact(my_artifact: kfp.components.OutputPath()):
    import pickle

    artifact = "1, 2, 3, 4"

    with open(my_artifact, "bw") as f:
        pickle.dump(artifact, f)


def consume_artifact(my_artifact: kfp.components.InputPath()):
    import pickle

    with open(my_artifact, "br") as f:
        artifact = pickle.load(f)

    print(artifact)


create_artifact_op = kfp.components.create_component_from_func(
    create_artifact,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)

consume_artifact_op = kfp.components.create_component_from_func(
    consume_artifact,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="Artifact Pipeline",
)
def artifact_pipeline():
    create_artifact_task = create_artifact_op()
    consume_artifact_task = consume_artifact_op(  # noqa: F841
        create_artifact_task.outputs["my_artifact"]
    )


if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=urllib.parse.urljoin(kubeflow_endpoint, "/pipeline"),
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(
        artifact_pipeline, arguments={}, experiment_name="artifact-example"
    )
