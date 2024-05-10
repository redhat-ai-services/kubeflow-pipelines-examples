"""Example of a pipeline to demonstrate saving metrics from a pipeline.

runMetrics appear to be depreciated in kfp v2 api so implement
this feature at your own risk.
"""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest")
def produce_metrics(
    mlpipeline_metrics_path: dsl.OutputPath("Metrics"),
):
    import json

    accuracy = 0.9
    mse = 0.1
    metrics = {
        "metrics": [
            {
                # The name of the metric. Visualized as the column name in the runs table.
                "name": "accuracy-score",
                # The value of the metric. Must be a numeric value.
                "numberValue": accuracy,
                # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and
                #  "PERCENTAGE" (displayed in percentage format).
                "format": "PERCENTAGE",
            },
            {
                # The name of the metric. Visualized as the column name in the runs table.
                "name": "mse-score",
                # The value of the metric. Must be a numeric value.
                "numberValue": mse,
                # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and
                #  "PERCENTAGE" (displayed in percentage format).
                "format": "RAW",
            },
        ]
    }

    with open(mlpipeline_metrics_path, "w") as f:
        json.dump(metrics, f)


@kfp.dsl.pipeline(
    name="metrics pipeline",
)
def metrics_pipeline():
    produce_metrics_task = produce_metrics()  # noqa: F841


if __name__ == "__main__":
    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
    )
    arguments = {}
    client.create_run_from_pipeline_func(metrics_pipeline, arguments=arguments, experiment_name="metrics-example")
