import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Assuming your chats router is defined in src.controller.chats
# We will import it inside the fixture to ensure it's potentially affected by patches if needed.

# It's good practice to define DEFAULT_USER_ID if your controller uses it globally
# and it's not imported from elsewhere, or ensure it's mocked/available.
# For this example, let's assume it's defined in your controller or you'll handle it.


@pytest.fixture
def mock_chat_dependencies():
    """Mocks dependencies for the chats controller."""
    mock_stream_query_results = [
        {"content": {"parts": [{"text": "Response part 1 for query"}]}},
        {"content": {"parts": [{"text": "Response part 2 for query"}]}},
    ]
    mock_remote_agent = MagicMock()
    mock_remote_agent.stream_query.return_value = iter(mock_stream_query_results)
    # Ensure create_session returns a dictionary with 'id'
    mock_remote_agent.create_session.return_value = {
        "id": "test_session_123",
        "user_id": "test_user",
    }

    mock_agent_engines_get = MagicMock(return_value=mock_remote_agent)

    mock_intent = MagicMock()
    mock_intent.remote_agent_resource_id = "mock_agent_id"
    mock_intent.name = "default_intent"
    mock_get_default_intent = MagicMock(return_value=mock_intent)

    mock_log_response = MagicMock()

    # Define the paths to patch based on where they are *used* in src.controller.chats
    patches = [
        patch("src.controller.chats.agent_engines.get", mock_agent_engines_get),
        patch("src.controller.chats.get_default_intent", mock_get_default_intent),
        patch("src.controller.chats.log_response", mock_log_response),
    ]

    for p in patches:
        p.start()

    yield {
        "mock_agent_engines_get": mock_agent_engines_get,
        "mock_get_default_intent": mock_get_default_intent,
        "mock_log_response": mock_log_response,
        "mock_remote_agent": mock_remote_agent,
    }  # Yield the mocks if tests need to assert calls on them

    for p in patches:
        p.stop()


@pytest.fixture
def client(mock_chat_dependencies):  # Ensure this fixture depends on the mock setup
    """Provides a TestClient instance with mocked dependencies for the chats router."""
    from src.controller.chats import router as chats_router  # Import here

    app = FastAPI()
    # Ensure the prefix matches how your main application includes this router
    app.include_router(chats_router)

    with TestClient(app) as test_client:
        with test_client.websocket_connect("/api/chats") as websocket:
            data = websocket.receive_json()
            print(data)
        yield test_client


# --- Test Cases ---
# Your test functions will now take 'client' as an argument.


def test_websocket_connection_and_start(client: TestClient):  # Modified
    """
    Test if the WebSocket connection is accepted and the initial 'start' message is received.
    """
    with client.websocket_connect("/api/chats") as websocket:
        data = websocket.receive_json()
        assert data == {"operation": "start"}
        websocket.close()


def test_websocket_send_message_receive_response_and_end_of_turn(
    client: TestClient, mock_chat_dependencies: dict
):  # Modified
    """
    Test sending a message and receiving streamed responses followed by 'end_of_turn'.
    """
    mock_remote_agent = mock_chat_dependencies["mock_remote_agent"]
    # Reset mock results for this specific test if needed, or ensure it's fresh
    mock_stream_query_results = [
        {"content": {"parts": [{"text": "Response part 1 for query"}]}},
        {"content": {"parts": [{"text": "Response part 2 for query"}]}},
    ]
    mock_remote_agent.stream_query.return_value = iter(mock_stream_query_results)

    with client.websocket_connect("/api/chats") as websocket:
        start_data = websocket.receive_json()
        assert start_data == {"operation": "start"}

        test_query = "Hello bot"
        websocket.send_json({"text": test_query})

        response1 = websocket.receive_json()
        # The structure of your "answer" part might be just the part itself, not nested under "parts"
        # Based on your controller: answer_part = {"answer": part}
        assert "answer" in response1
        assert (
            response1["answer"]["text"] == "Response part 1 for query"
        )  # Adjusted assertion

        response2 = websocket.receive_json()
        assert "answer" in response2
        assert (
            response2["answer"]["text"] == "Response part 2 for query"
        )  # Adjusted assertion

        end_data = websocket.receive_json()
        assert end_data == {"operation": "end_of_turn"}

        websocket.close()

    # Assert that stream_query was called with the correct message
    mock_remote_agent.stream_query.assert_called_once_with(
        user_id="traveler0115",  # Assuming DEFAULT_USER_ID from your controller
        session_id="test_session_123",
        message=test_query,
    )


def test_websocket_multiple_messages_in_session(
    client: TestClient, mock_chat_dependencies: dict
):  # Modified
    """
    Test sending multiple messages over the same WebSocket connection.
    """
    mock_remote_agent = mock_chat_dependencies["mock_remote_agent"]

    with client.websocket_connect("/api/chats") as websocket:
        assert websocket.receive_json() == {"operation": "start"}

        # First message
        mock_stream_query_results_1 = [
            {"content": {"parts": [{"text": "Response for first"}]}}
        ]
        mock_remote_agent.stream_query.return_value = iter(mock_stream_query_results_1)
        websocket.send_json({"text": "First query"})
        assert websocket.receive_json()["answer"]["text"] == "Response for first"
        assert websocket.receive_json() == {"operation": "end_of_turn"}
        mock_remote_agent.stream_query.assert_called_with(
            user_id="traveler0115", session_id="test_session_123", message="First query"
        )

        # Second message
        mock_stream_query_results_2 = [
            {"content": {"parts": [{"text": "Response for second"}]}}
        ]
        mock_remote_agent.stream_query.return_value = iter(mock_stream_query_results_2)
        websocket.send_json({"text": "Second query"})
        assert websocket.receive_json()["answer"]["text"] == "Response for second"
        assert websocket.receive_json() == {"operation": "end_of_turn"}
        mock_remote_agent.stream_query.assert_called_with(
            user_id="traveler0115",
            session_id="test_session_123",
            message="Second query",
        )

        websocket.close()


def test_websocket_invalid_json_from_client(
    client: TestClient, mock_chat_dependencies: dict
):  # Modified
    """
    Test how the server handles malformed JSON sent by the client.
    """
    mock_remote_agent = mock_chat_dependencies["mock_remote_agent"]
    mock_stream_query_results = [{"content": {"parts": [{"text": "Valid response"}]}}]

    with client.websocket_connect("/api/chats") as websocket:
        assert websocket.receive_json() == {"operation": "start"}

        websocket.send_text("this is not json")

        error_response = websocket.receive_json()
        assert "error" in error_response
        assert error_response["error"] == "Invalid JSON format received."

        mock_remote_agent.stream_query.return_value = iter(mock_stream_query_results)
        websocket.send_json({"text": "Valid query after error"})
        assert websocket.receive_json()["answer"]["text"] == "Valid response"
        assert websocket.receive_json() == {"operation": "end_of_turn"}

        websocket.close()


def test_websocket_client_disconnects_abruptly(client: TestClient):  # Modified
    """
    Test server behavior when client disconnects.
    """
    with client.websocket_connect("/api/chats") as websocket:
        assert websocket.receive_json() == {"operation": "start"}
        websocket.send_json({"text": "A message before disconnecting"})
        # Abrupt disconnect by exiting 'with' block
    # No specific assertion other than test completion without server error.
    # Check server logs for WebSocketDisconnect handling if detailed logging exists.
