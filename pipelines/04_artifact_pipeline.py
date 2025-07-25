"""Example of a pipeline to demonstrate accessing secrets/config maps in a pipeline."""


import kfp.compiler
from kfp import dsl
from kfp_helper import execute_pipeline_run


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
    execute_pipeline_run(pipeline=artifact_pipeline, experiment="artifact-example", arguments={})
