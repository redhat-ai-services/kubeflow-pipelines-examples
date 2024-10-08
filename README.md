# kubeflow-examples

This repo is intended to provide examples for different features of kubeflow pipelines on OpenShift.

## Quick Start

1. Install the RHOAI operator via Operator Hub
1. Create a data science project
1. Create a DSPA instance in your project with the following command:
    ```
    oc apply -f manifests/dataSciencePipelineApplication.yaml
    ```
1. Create the .env file
    * Create a new file named .env and copy the contents of the file example.env into it
    * Update the storage class if you are not utilizing ODF
    * Update the `KUBEFLOW_ENDPOINT` url with the URL for your instance of the data science pipeline instance:
        ```sh
        route=$(oc get route ds-pipeline-pipelines-definition -o=jsonpath='{.spec.host}')
        echo "https://${route}"
        ```
    * Get your token by logging into ocp via oc and running the following command and setting the result as the `BEARER_TOKEN`:
        ```sh
        oc whoami --show-token
        ```
1. Create and activate a virtual environment:
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

Your environment should be all ready to go. Now we can start running the pipeline examples.

All the pipeline examples are in the `pipelines` folder

## Python Examples

1. `00_compiled_pipeline.py`

    * This is a very basic example of how to create a kfp pipeline. It is adding 4 to the value of parameter `a` that we pass, and then adding this result to the value of parameter `b`. 
    * The first step is to compile the pipeline into a yaml file. To run this execute the following command. This will generate a yaml file named '00_compiled_pipeline.yaml'
    ```
    python pipelines/00_compiled_pipeline.py
    ```
    * Now go to RHOAI and into the Data Science Pipelines section. Click on `Import pipeline` and upload the generated yaml file.
    * To run this pipeline click on the Create Run option.
    * To check the run, go to the Experiments section in RHOAI.

2. `01_test_connection_via_route.py`

    * This pipeline just checks if we can connect to kfp with the route that we entered in the .env file. If we can connect to it, it also displays the list of experiements and the list of the pipelines.
    * To run this example use the following command. You will be able to see the output in the terminal.
    ```
    python pipelines/01_test_connection_via_route.py
    ```