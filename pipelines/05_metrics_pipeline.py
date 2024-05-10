"""
Example of a pipeline to demonstrate saving metrics from a pipeline.

runMetrics appear to be depreciated in kfp v2 api so implement
this feature at your own risk.
"""

import os

from dotenv import load_dotenv

from kfp import dsl
import kfp.compiler

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


@dsl.component(
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest"
)
def produce_metrics(
    mlpipeline_metrics_path: dsl.OutputPath("Metrics"),
):
    import json

    accuracy = 0.9
    mse = 0.1
    metrics = {
        "metrics": [
            {
                "name": "accuracy-score",  # The name of the metric. Visualized as the column name in the runs table.
                "numberValue": accuracy,  # The value of the metric. Must be a numeric value.
                "format": "PERCENTAGE",  # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
            },
            {
                "name": "mse-score",  # The name of the metric. Visualized as the column name in the runs table.
                "numberValue": mse,  # The value of the metric. Must be a numeric value.
                "format": "RAW",  # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
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
    client.create_run_from_pipeline_func(
        metrics_pipeline, arguments=arguments, experiment_name="metrics-example"
    )
