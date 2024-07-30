"""Example of a pipeline to demonstrate a simple real world data science workflow."""

import os

import kfp.compiler
from dotenv import load_dotenv
from kfp import dsl

load_dotenv(override=True)

kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
base_image = os.getenv("BASE_IMAGE", "image-registry.openshift-image-registry.svc:5000/openshift/python:latest")


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "scikit-learn"],
)
def data_prep(
    x_train_file: dsl.Output[dsl.Dataset],
    x_test_file: dsl.Output[dsl.Dataset],
    y_train_file: dsl.Output[dsl.Dataset],
    y_test_file: dsl.Output[dsl.Dataset],
):
    import pickle

    import pandas as pd
    from sklearn import datasets
    from sklearn.model_selection import train_test_split

    def get_iris_data() -> pd.DataFrame:
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

        print("Initial Dataset:")
        print(data.head())

        return data

    def create_training_set(dataset: pd.DataFrame, test_size: float = 0.3):
        # Features
        x = dataset[["sepalLength", "sepalWidth", "petalLength", "petalWidth"]]
        # Labels
        y = dataset["species"]

        # Split dataset into training set and test set
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=11)

        return x_train, x_test, y_train, y_test

    def save_pickle(object_file, target_object):
        with open(object_file, "wb") as f:
            pickle.dump(target_object, f)

    dataset = get_iris_data()
    x_train, x_test, y_train, y_test = create_training_set(dataset)

    save_pickle(x_train_file.path, x_train)
    save_pickle(x_test_file.path, x_test)
    save_pickle(y_train_file.path, y_train)
    save_pickle(y_test_file.path, y_test)


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "scikit-learn"],
)
def validate_data():
    pass


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "scikit-learn"],
)
def train_model(
    x_train_file: dsl.Input[dsl.Dataset],
    y_train_file: dsl.Input[dsl.Dataset],
    model_file: dsl.Output[dsl.Model],
):
    import pickle

    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier

    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            target_object = pickle.load(f)  # noqa: S301

        return target_object

    def save_pickle(object_file, target_object):
        with open(object_file, "wb") as f:
            pickle.dump(target_object, f)

    def train_iris(x_train: pd.DataFrame, y_train: pd.DataFrame):
        model = RandomForestClassifier(n_estimators=100)
        model.fit(x_train, y_train)

        return model

    x_train = load_pickle(x_train_file.path)
    y_train = load_pickle(y_train_file.path)

    model = train_iris(x_train, y_train)

    save_pickle(model_file.path, model)


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "scikit-learn"],
)
def evaluate_model(
    x_test_file: dsl.Input[dsl.Dataset],
    y_test_file: dsl.Input[dsl.Dataset],
    model_file: dsl.Input[dsl.Model],
    mlpipeline_metrics_file: dsl.Output[dsl.Metrics],
):
    import json
    import pickle

    from sklearn.metrics import accuracy_score

    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            target_object = pickle.load(f)  # noqa: S301

        return target_object

    x_test = load_pickle(x_test_file.path)
    y_test = load_pickle(y_test_file.path)
    model = load_pickle(model_file.path)

    y_pred = model.predict(x_test)

    accuracy_score_metric = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy_score_metric}")

    metrics = {
        "metrics": [
            {
                "name": "accuracy-score",
                "numberValue": accuracy_score_metric,
                "format": "PERCENTAGE",
            },
        ]
    }

    with open(mlpipeline_metrics_file.path, "w") as f:
        json.dump(metrics, f)


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "skl2onnx"],
)
def model_to_onnx(model_file: dsl.Input[dsl.Model], onnx_model_file: dsl.Output[dsl.Model]):
    import pickle

    from skl2onnx import to_onnx
    from skl2onnx.common.data_types import FloatTensorType

    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            target_object = pickle.load(f)  # noqa: S301

        return target_object

    model = load_pickle(model_file.path)

    initial_type = [("float_input", FloatTensorType([None, 4]))]
    onnx_model = to_onnx(model, initial_types=initial_type)

    with open(onnx_model_file.path, "wb") as f:
        f.write(onnx_model.SerializeToString())


@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "onnxruntime"],
)
def validate_model(onnx_model_file: dsl.Input[dsl.Model]):
    import onnxruntime

    session = onnxruntime.InferenceSession(onnx_model_file.path)

    input_name = session.get_inputs()[0].name
    label_name = session.get_outputs()[0].name

    input_values = [[5, 3, 1.6, 0.2]]

    print(f"Performing test prediction on {input_values}")
    result = session.run([label_name], {input_name: input_values})[0]

    print(f"Response: {result}")


@kfp.dsl.pipeline(
    name="Iris Pipeline",
)
def iris_pipeline(model_obc: str = "iris-model"):
    data_prep_task = data_prep()

    train_model_task = train_model(
        x_train_file=data_prep_task.outputs["x_train_file"],
        y_train_file=data_prep_task.outputs["y_train_file"],
    )

    evaluate_model_task = evaluate_model(  # noqa: F841
        x_test_file=data_prep_task.outputs["x_test_file"],
        y_test_file=data_prep_task.outputs["y_test_file"],
        model_file=train_model_task.output,
    )

    model_to_onnx_task = model_to_onnx(  # noqa: F841
        model_file=train_model_task.output,
    )

    validate_model_task = validate_model(onnx_model_file=model_to_onnx_task.output)  # noqa: F841


if __name__ == "__main__":
    print(f"Connecting to kfp: {kubeflow_endpoint}")

    sa_token_path = "/run/secrets/kubernetes.io/serviceaccount/token"  # noqa: S105
    if "BEARER_TOKEN" in os.environ:
        bearer_token = os.environ["BEARER_TOKEN"]
    elif os.path.isfile(sa_token_path):
        with open(sa_token_path) as f:
            bearer_token = f.read().rstrip()

    # Check if the script is running in a k8s pod
    # Get the CA from the service account if it is
    # Skip the CA if it is not
    sa_ca_cert = "/run/secrets/kubernetes.io/serviceaccount/service-ca.crt"
    if os.path.isfile(sa_ca_cert) and "svc" in kubeflow_endpoint:
        ssl_ca_cert = sa_ca_cert
    else:
        ssl_ca_cert = None

    client = kfp.Client(
        host=kubeflow_endpoint,
        existing_token=bearer_token,
        ssl_ca_cert=ssl_ca_cert,
    )
    result = client.create_run_from_pipeline_func(iris_pipeline, arguments={}, experiment_name="iris")
    print(f"Starting pipeline run with run_id: {result.run_id}")
