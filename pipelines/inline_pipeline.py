"""Example of a pipeline built from inline functions with kfp."""
import kfp


def add(a: float, b: float) -> float:
    """Calculate the sum of the two arguments."""
    return a + b


add_op = kfp.components.create_component_from_func(
    add,
    base_image="image-registry.openshift-image-registry.svc:5000/openshift/python:latest",
)


@kfp.dsl.pipeline(
    name="Inline Function Pipeline",
    description="A pipeline that is built from inline functions",
)
def add_pipeline(a="1", b="7"):
    """
    Pipeline to add values.

    Pipeline to take the value of a, add 4 to it and then
    perform a second task to take the put of the first task and add b.
    """
    first_add_task = add_op(a, 4)
    second_add_task = add_op(first_add_task.output, b)  # noqa: F841


if __name__ == "__main__":
    kf_endpoint = ""
    ocp_token = ""
