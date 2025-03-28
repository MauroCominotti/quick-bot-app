from scripts.agent_engine_setup import deploy_agent
from scripts.big_query_setup import create_dataset, create_table
from scripts.gcs_setup import BUCKET
from scripts.gcs_setup import create_bucket
from src.agents.agent import root_agent
from src.service.search_application import SEARCH_APPLICATION_TABLE
from src.model.search import SearchApplication
from os import getenv

# BIG_QUERY_DATASET=""
BIG_QUERY_DATASET = getenv("BIG_QUERY_DATASET")

print("Setting up BigQuery... \n")

create_dataset(BIG_QUERY_DATASET)
create_table(
    BIG_QUERY_DATASET, SEARCH_APPLICATION_TABLE, SearchApplication.__schema__()
)

# Create staging GCS bucket
print("Setting up GCS... \n")

bucket = create_bucket(BUCKET)

# Deploy example agent to Agent Engine
print("Deploying example agent to Agent Engine up GCS... \n")
deployed_agent = deploy_agent(root_agent)

print("\nSuccess!\n")
