import kfp
import urllib

KUBEFLOW_ENDPOINT = (
    "https://ds-pipeline-ui-odh-test.apps.cluster-mh667.mh667.sandbox2373.opentlc.com/"
)
BEARER_TOKEN = "sha256~"  # oc whoami --show-token

client = kfp.Client(
    host=urllib.parse.urljoin(KUBEFLOW_ENDPOINT, "/pipeline"),
    existing_token=BEARER_TOKEN,
)
print(client.list_experiments())
