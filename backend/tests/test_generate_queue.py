from types import SimpleNamespace
from fastapi.testclient import TestClient

from app.main import app
from app.auth.dependencies import get_current_user
from app.db.models.user import User


def test_generate_enqueues_job_and_returns_job_id(monkeypatch):
    fake_user = User(id="user-123", email="user@example.com")

    # Override get_current_user dependency to authenticate automatically
    app.dependency_overrides[get_current_user] = lambda: fake_user

    # Mock the Redis queue
    class FakeQueue:
        name = "test_code_generation"

        def enqueue(self, func, requirement, user_id, **kwargs):
            assert requirement == "build me a service"
            assert user_id == "user-123"
            # Return a mock job object
            class FakeJob:
                id = "job-123"
                meta = {}
                def save_meta(self):
                    pass
            return FakeJob()

    monkeypatch.setattr("app.routers.generate.task_queue", FakeQueue())

    client = TestClient(app)
    response = client.post("/generate", json={"requirement": "build me a service"})

    # Clean up overrides
    app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json() == {
        "job_id": "job-123",
        "status": "queued",
        "queue": "test_code_generation",
    }
