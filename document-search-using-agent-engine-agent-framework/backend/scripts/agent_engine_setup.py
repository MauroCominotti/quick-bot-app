import vertexai
from vertexai import agent_engines

from scripts.big_query_setup import PROJECT_ID
from scripts.gcs_setup import BUCKET


def deploy_agent(agent):
    vertexai.init(
        project=PROJECT_ID,
        location="us-central1",
        staging_bucket=BUCKET,
    )
    deployed_agent = agent_engines.create(
        agent_engine=agent,
        requirements=[
            "google_genai_agents-0.0.2.dev20250204+723246417-py3-none-any.whl",
        ],
        extra_packages=[
            "google_genai_agents-0.0.2.dev20250204+723246417-py3-none-any.whl",
        ],
    )
    return deployed_agent
