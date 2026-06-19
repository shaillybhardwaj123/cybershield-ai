import pytest
from google.adk.events import Event
from google.genai import types

@pytest.fixture(autouse=True)
def mock_adk_runner(monkeypatch):
    from google.adk.runners import Runner
    
    def mock_run(self, *args, **kwargs):
        mock_event = Event(
            content=types.Content(
                parts=[types.Part.from_text(text="Mocked ADK response for testing.")]
            )
        )
        yield mock_event

    async def mock_run_async(self, *args, **kwargs):
        mock_event = Event(
            content=types.Content(
                parts=[types.Part.from_text(text="Mocked ADK response for testing.")]
            )
        )
        yield mock_event

    monkeypatch.setattr(Runner, "run", mock_run)
    monkeypatch.setattr(Runner, "run_async", mock_run_async)
