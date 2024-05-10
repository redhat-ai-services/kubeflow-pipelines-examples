"""Example of a pipeline to demonstrate visualizations from a pipeline.

The visualization doesn't work for this.  PR's are welcome to help
get a visualization functioning.

This pipeline example is currently broken.
"""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def confusion_matrix_viz(
    mlpipeline_ui_metadata_path: dsl.OutputPath(),
    confusion_matrix_path: dsl.OutputPath(),
):
    import json

    cf = """
    16,0,0
    0,11,0
    0,0,18
    """

    with open(confusion_matrix_path, "w") as text_file:
        text_file.write(cf)

    metadata = {
        "outputs": [
            {
                "type": "confusion_matrix",
                "format": "csv",
                "schema": [
                    {"name": "target", "type": "CATEGORY"},
                    {"name": "predicted", "type": "CATEGORY"},
                    {"name": "count", "type": "NUMBER"},
                ],
                "source": cf,
                "storage": "inline",
                "labels": ["one", "two", "three"],
            }
        ]
    }

    with open(mlpipeline_ui_metadata_path, "w") as metadata_file:
        json.dump(metadata, metadata_file)

    return cf


@kfp.dsl.pipeline(
    name="Metadata Example Pipeline",
    description="A pipeline that is built from inline functions",
)
def visualization_pipeline():
    """Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    confusion_matrix_task = confusion_matrix_viz()  # noqa: F841


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(visualization_pipeline, arguments={}, experiment_name="visualization-example")
