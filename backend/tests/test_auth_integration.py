import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.models.user import User
from app.db.models.execution import Execution
from app.auth.dependencies import get_current_user
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.execution_read_repository import ExecutionReadRepository

# Use a dedicated Postgres test database; falls back to the main dev DB
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://localhost:5432/orchestrator_db",
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_repository_user_isolation():
    db = TestingSessionLocal()
    try:
        # Create users
        alice = User(google_id="g-alice", email="alice@test.com", name="Alice")
        bob = User(google_id="g-bob", email="bob@test.com", name="Bob")
        db.add(alice)
        db.add(bob)
        db.commit()
        db.refresh(alice)
        db.refresh(bob)

        # Create executions using ExecutionRepository
        repo = ExecutionRepository(db)
        exec_alice = repo.create(
            requirement="alice's requirement",
            workspace_path="/tmp/alice",
            started_at=None,
            user_id=alice.id,
        )
        exec_bob = repo.create(
            requirement="bob's requirement",
            workspace_path="/tmp/bob",
            started_at=None,
            user_id=bob.id,
        )

        # Read executions using ExecutionReadRepository
        read_repo = ExecutionReadRepository(db)

        # Alice listing
        alice_execs = read_repo.get_all_executions_for_user(alice.id)
        assert len(alice_execs) == 1
        assert alice_execs[0].id == exec_alice.id

        # Bob listing
        bob_execs = read_repo.get_all_executions_for_user(bob.id)
        assert len(bob_execs) == 1
        assert bob_execs[0].id == exec_bob.id

        # Alice get_execution check
        alice_single = read_repo.get_execution_for_user(exec_alice.id, alice.id)
        assert alice_single is not None
        assert alice_single.requirement == "alice's requirement"

        # Bob cannot fetch Alice's execution
        bob_get_alice = read_repo.get_execution_for_user(exec_alice.id, bob.id)
        assert bob_get_alice is None

    finally:
        db.close()


def test_secured_endpoints_require_auth():
    client = TestClient(app)

    # 1. /generate post should reject unauthenticated requests with 401
    response = client.post("/generate", json={"requirement": "something"})
    assert response.status_code == 401

    # 2. /executions list should reject unauthenticated requests with 401
    response = client.get("/executions/")
    assert response.status_code == 401


def test_executions_endpoint_filters_by_user(monkeypatch):
    import uuid
    fake_id = uuid.uuid4()
    fake_user = User(id=fake_id, google_id="g-alice", email="alice@test.com", name="Alice")
    app.dependency_overrides[get_current_user] = lambda: fake_user

    class FakeExecution:
        id = fake_id
        requirement = "Requirement Alice"
        status = "success"
        tries_used = 1
        created_at = None

    class MockReadRepo:
        def __init__(self, db):
            pass
        def get_all_executions_for_user(self, user_id):
            assert user_id == fake_id
            return [FakeExecution()]
        def get_execution_for_user(self, execution_id, user_id):
            assert user_id == fake_id
            if str(execution_id) == str(fake_id):
                return FakeExecution()
            return None
        def get_iterations(self, execution_id):
            return []

    monkeypatch.setattr(
        "app.routers.executions.ExecutionReadRepository",
        MockReadRepo
    )

    client = TestClient(app)

    # Test List Executions
    response = client.get("/executions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["execution_id"] == str(fake_id)

    # Test Get Single Execution Success
    response = client.get(f"/executions/{fake_id}")
    assert response.status_code == 200
    assert response.json()["execution_id"] == str(fake_id)

    # Test Get Single Execution Not Found / Unauthorized
    response = client.get(f"/executions/{uuid.uuid4()}")
    assert response.status_code == 404

    app.dependency_overrides.clear()
