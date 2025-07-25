"""Example of a pipeline using a GPU."""


from kfp import dsl, kubernetes
from kfp_helper import execute_pipeline_run


@dsl.component(base_image="quay.io/modh/cuda-notebooks:cuda-jupyter-minimal-ubi9-python-3.11-20250326")
def nvidia_smi():
    """Use the nvidia-smi command to check the GPU status."""
    import os

    command = "nvidia-smi"
    os.system(command)  # noqa: S605


@dsl.pipeline()
def nvidia_smi_pipeline():
    """Pipeline to execute a task using GPUs"""
    nvidia_smi_task = nvidia_smi()

    # Set the accelerator type and set the request/limit to 1
    # Note: You cannot request different values for the request/limit
    nvidia_smi_task.set_accelerator_type("nvidia.com/gpu").set_accelerator_limit(1)

    # Set the toleration for the GPU node
    kubernetes.add_toleration(nvidia_smi_task, key="nvidia.com/gpu", operator="Exists", effect="NoSchedule")


if __name__ == "__main__":
    execute_pipeline_run(pipeline=nvidia_smi_pipeline, experiment="gpu-example", arguments={})
