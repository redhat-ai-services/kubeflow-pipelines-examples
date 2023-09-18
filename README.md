# kubeflow-examples

This repo is intended to provide examples for different features of kubeflow pipelines on OpenShift.

## Quick Start

1. Install the OpenShift Pipelines operator via Operator Hub
2. Install the RHODS operator via Operator Hub
3. Create a data science project
4. Create a DSPA instance in your project:
    ```
    oc apply -f manifests/dataSciencePipelineApplication.yaml
    ```
5. Deploy any additional resources required for specific examples in the manifests folder.
6. Create the .env file
    * Copy the example.env file to .env
    * Update the storage class if you are not utilizing ODF
    * Update the `KUBEFLOW_ENDPOINT` url with the URL for your instance of the data science pipeline instance:
        ```sh
        route=$(oc get route ds-pipeline-pipelines-definition -o=jsonpath='{.spec.host}')
        echo "https://${route}"
        ```
    * Get your token by logging into ocp via oc and running the following command and setting the result as `BEARER_TOKEN`:
        ```sh
        oc whoami --show-token
        ```
7. Create and activate a virtual environment:
    * If not already installed, install pipenv:
        ```
        pip install pipenv
        ```
    * Install packages in a venv
        ```
        pipenv install --dev
        ```
    * Activate the venv
        ```
        pipenv shell
        ```

Your environment should be all ready to go.  Try out the first pipeline by running:

```
python pipelines/00_compiled_pipeline.py
```
