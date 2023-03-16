"""Example of a pipeline to demonstrate installing additional packages in the pipeline."""
import os
import urllib

from dotenv import load_dotenv

import kfp

import kfp_tekton

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
bearer_token = os.environ["BEARER_TOKEN"]


def get_iris_data():
    import pandas as pd

    from sklearn import datasets

    iris = datasets.load_iris()
    data = pd.DataFrame(
        {
            "sepalLength": iris.data[:, 0],
            "sepalWidth": iris.data[:, 1],
            "petalLength": iris.data[:, 2],
            "petalWidth": iris.data[:, 3],
            "species": iris.target,
        }
    )

    print(data.head())


get_iris_data_op = kfp.components.create_component_from_func(
    get_iris_data,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
    packages_to_install=["pandas", "scikit-learn"],
)


@kfp.dsl.pipeline(
    name="Additional Packages Pipeline",
)
def additional_packages_pipeline():
    get_iris_data_task = get_iris_data_op()


if __name__ == "__main__":
    client = kfp_tekton.TektonClient(
        host=urllib.parse.urljoin(kubeflow_endpoint, "/pipeline"),
        existing_token=bearer_token,
    )
    client.create_run_from_pipeline_func(
        additional_packages_pipeline,
        arguments={},
        experiment_name="additional-packages-example",
    )
