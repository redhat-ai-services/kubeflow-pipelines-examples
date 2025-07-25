"""Example of a pipeline to demonstrate installing additional packages in the pipeline."""


import kfp.compiler
from kfp import dsl
from kfp_helper import execute_pipeline_run


@dsl.component(
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
    packages_to_install=["pandas", "scikit-learn"],
)
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


@kfp.dsl.pipeline(
    name="Additional Packages Pipeline",
)
def additional_packages_pipeline():
    get_iris_data_task = get_iris_data()  # noqa: F841


if __name__ == "__main__":
    execute_pipeline_run(pipeline=additional_packages_pipeline, experiment="additional-packages-example", arguments={})
