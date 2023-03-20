"""
Example of a pipeline to demonstrate saving metrics from a pipeline.

runMetrics appear to be depreciated in kfp v2 api so implement
this feature at your own risk.
"""
import os
import urllib

from dotenv import load_dotenv

import kfp

import kfp_tekton

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


def produce_metrics(
    mlpipeline_metrics_path: kfp.components.OutputPath("Metrics"),
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


produce_metrics_op = kfp.components.create_component_from_func(
    produce_metrics,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="metrics pipeline",
)
def metrics_pipeline():
    produce_metrics_task = produce_metrics_op()  # noqa: F841


if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=urllib.parse.urljoin(kubeflow_endpoint, "/pipeline"),
        existing_token=bearer_token,
    )
    arguments = {}
    client.create_run_from_pipeline_func(
        metrics_pipeline, arguments=arguments, experiment_name="metrics-example"
    )
