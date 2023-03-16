# kubeflow-examples

This repo is intended to provide examples for

## Quick Start

1. Install the ODH operator via operator hub
2. Deploy the odh kfdef:
    ```
    oc apply -f manifests/opendatahub.yaml
    ```
3. Deploy any additional resources required for specific examples in the manifests folder.
4. Create the .env file
    a. Copy the example.env file to .env
    b. Update the `KUBEFLOW_ENDPOINT` url with the URL for your instance of the kubeflow-ui
    c. Get your token by logging into ocp via oc and running the following command:
        ```
        oc whoami --show-token
        ```
5. Create and activate a virtual environment:
    a. If not already installed, install pipenv:
        ```
        pip install pipenv
        ```
    b. Install packages in a venv
        ```
        pipenv install --dev
        ```
    c. Activate the venv
        ```
        pipenv shell
        ```

Your environment should be all ready to go.  Try out the first pipeline by running:

```
python pipelines/0_compiled_pipeline.py
```
