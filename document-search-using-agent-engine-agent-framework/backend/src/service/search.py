import logging
from typing import List
from uuid import uuid4

from google.adk import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud.discoveryengine_v1 import SearchRequest
from google.cloud.discoveryengine_v1 import SearchServiceClient
from google.genai import types

from src.model.search import SearchApplication
from src.model.search import SearchResult
from src.model.search import SearchResultsWithSummary

APP_NAME = "document-search"

CONTENT_SEARCH_SPEC = SearchRequest.ContentSearchSpec(
    snippet_spec=SearchRequest.ContentSearchSpec.SnippetSpec(return_snippet=True),
    extractive_content_spec=SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
        max_extractive_answer_count=1
    ),
    summary_spec=SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5,
        include_citations=True,
        ignore_adversarial_query=True,
        ignore_non_summary_seeking_query=True,
        model_spec=SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
            version="stable",
        ),
    ),
)
QUERY_EXPANSION_SPEC = SearchRequest.QueryExpansionSpec(
    condition=SearchRequest.QueryExpansionSpec.Condition.AUTO,
)
SPELL_CORRECTION_SPEC = SearchRequest.SpellCorrectionSpec(
    mode=SearchRequest.SpellCorrectionSpec.Mode.AUTO
)


class SearchService:

    def __init__(
        self,
        search_application: SearchApplication,
        model_name: str = "gemini-2.0-flash",
    ):
        self.search_client = SearchServiceClient(
            client_options=search_application.get_client_options()
        )
        self.serving_config = search_application.get_serving_config()
        self.summarization_agent = self._get_summarization_agent(model_name)

    def search(self, term: str) -> SearchResultsWithSummary:
        request = SearchRequest(
            serving_config=self.serving_config,
            query=term,
            page_size=10,
            content_search_spec=CONTENT_SEARCH_SPEC,
            query_expansion_spec=QUERY_EXPANSION_SPEC,
            spell_correction_spec=SPELL_CORRECTION_SPEC,
        )

        data = self.search_client.search(request)
        results = []

        # Process results
        for r in data.results:
            document = r.document
            derived_data = document.derived_struct_data
            gcs_link = derived_data.get("link").replace(
                "gs://", "https://storage.cloud.google.com/"
            )

            # Extract snippet safely
            snippets = derived_data.get("snippets", [])
            snippet_text = (
                snippets[0].get("snippet", "No snippet available")
                if snippets
                else "No snippet available"
            )
            extractive_answers = derived_data.get("extractive_answers", [])
            content_text = (
                extractive_answers[0].get("content", "No content available")
                if extractive_answers
                else "No content available"
            )
            # Map to SearchResult
            mapped_result = SearchResult(
                document_id=document.id,
                title=derived_data.get("title", "Untitled"),
                snippet=snippet_text,
                link=gcs_link,
                content=content_text,
            )
            results.append(mapped_result)

        snippets = [result.snippet for result in results]
        summary_text = self.summarize_search_results(
            user_query=term,
            snippets=snippets,
        )

        response_result = SearchResultsWithSummary(
            summary=summary_text, results=results
        )

        return response_result

    def _get_summarization_agent(self, model_name: str) -> Agent:
        try:
            summarization_agent = Agent(
                name="search_result_summarizer",
                description="An agent that summarizes provided search result snippets based on an initial user query.",
                model=model_name,
                # Instructions telling the agent its specific task
                instruction=(
                    "You are an expert summarizer. Your task is to synthesize information from the provided search result snippets "
                    "to answer the original user query. Focus ONLY on the information present in the snippets. "
                    "Generate a concise and coherent summary that directly addresses the user's query. "
                    "Do not add information not present in the snippets. Do not reference the snippets directly unless necessary for clarity (e.g., 'Document X mentions...')."
                    "If the snippets do not contain relevant information to answer the query, state that."
                ),
                # No external tools needed for this agent, as data is provided directly
                tools=[],
            )
            logging.info("ADK Summarization Agent created successfully.")
            return summarization_agent
        except Exception as e:
            logging.error(f"An error occurred during agent definition: {e}")
            raise e

    def summarize_search_results(
        self,
        user_query: str,
        snippets: List[str],  # Expecting a list of pre-extracted snippet strings
    ) -> str:
        if not self.summarization_agent:
            logging.error("Summarization agent not initialized.")
            return "Error: Summarization agent not initialized."
        if not snippets:
            logging.warning("No search snippets provided to summarize.")
            raise ValueError("No search snippets provided to summarize.")

        # Combine query and snippets into a single prompt for the agent using f-string
        snippet_separator = "\n---\n"  # Define a separator for readability
        formatted_snippets = snippet_separator.join(snippets)

        combined_prompt = (
            f"Original User Query: {user_query}\n\n"
            f"Relevant Search Results:\n\n{formatted_snippets}\n\n"
            f"Based on the provided search results, please provide a summary that answers the original user query."
        )

        logging.debug(
            "\n--- Sending to Summarization Agent ---\n%s\n--- End of Agent Input ---",
            combined_prompt,
        )

        try:
            # Generate the summary
            session_service = InMemorySessionService()
            artifact_service = InMemoryArtifactService()
            user_id = str(uuid4())
            session = session_service.create_session(app_name=APP_NAME, user_id=user_id)
            runner = Runner(
                agent=self.summarization_agent,
                artifact_service=artifact_service,
                session_service=session_service,
                app_name=APP_NAME,
            )

            content = types.Content(
                role="user", parts=[types.Part(text=combined_prompt)]
            )
            events = runner.run(
                session_id=session.id, user_id=user_id, new_message=content
            )
            response = None
            for event in events:
                if event.is_final_response():
                    final_response = event.content.parts[0]
                    response = final_response

            if response and hasattr(response, "text"):
                logging.info("Summary generated successfully.")
                return response.text
            else:
                raise ValueError("Agent did not return a valid text response.")
        except Exception as e:
            logging.error(f"Error during summarization: {e}")
            raise e
