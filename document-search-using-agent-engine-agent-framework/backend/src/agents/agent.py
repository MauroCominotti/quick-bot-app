# Simple agent to test the RAG tool.
from vertexai.preview import rag
from agents import Agent
from agents.tools.retrieval.vertex_rag_retrieval import VertexRagRetrieval


retrieval_config = {
    'rag_resources': [
        rag.RagResource(
            rag_corpus='projects/68813848281/locations/us-central1/ragCorpora/2305843009213693952',
        )
    ],
    'vector_distance_threshold': (
        0.8
    ),  # use bigger threshold so it's easier to return documents for initial testing
}

swiss_policy_retrieval = VertexRagRetrieval(
    name='swiss_policy_retrieval',
    description='Tools to retrieve for swiss flights',
    retrieval_config=retrieval_config,
)


def check_flights_poicy(query: str):
  return f'OK, your {query} has been checked.'


root_agent = Agent(
    model='gemini-1.5-flash',
    name='data_processing_agent',
    instruction="""
      You are an agent to check policy for flights.
      For swiss flights, you should use the swiss_policy_retrieval tool.
      For other flights, you should use the check_flights_poicy tool.
    """,
    tools=[
        swiss_policy_retrieval,
        check_flights_poicy,
    ],
    flow='single',
)
