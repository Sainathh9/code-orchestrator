import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.user import User
from app.db.models.execution import Execution
from app.orchestrator.orchestrator import Orchestrator
from app.services.llm.llm_service import LLMService
from app.repositories.execution_read_repository import ExecutionReadRepository

# Use dedicated test DB (SQLite for simple testing or Postgres as fallback)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_non_code.db"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    # Override the database session creation in nodes to use testing DB
    from app.orchestrator.graph import nodes
    monkeypatch.setattr(nodes, "SessionLocal", TestingSessionLocal)

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_non_code_requirement_returns_specific_text(monkeypatch):
    # Create a user in the test database
    db = TestingSessionLocal()
    user = User(google_id="g-test-user", email="test@test.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = str(user.id)
    user_db_id = user.id
    db.close()

    # Mock LLMService.generate to classify as NO (not code)
    generated_calls = []

    def mock_generate(self, prompt: str) -> str:
        generated_calls.append(prompt)
        # Classify as non-code
        return "NO"

    monkeypatch.setattr(LLMService, "generate", mock_generate)

    orchestrator = Orchestrator()
    result = orchestrator.run("tell me a joke", user_id=user_id)

    # Verify that ONLY the classification prompt was called (1 call)
    assert len(generated_calls) == 1
    assert "You are a classifier" in generated_calls[0]

    # Verify result
    assert result.passed is True
    assert result.tries_used == 1
    assert "Non-code requirement detected" in result.stdout

    # Verify solution.py contains the specific message
    solution_path = os.path.join(result.workspace, "solution.py")
    assert os.path.exists(solution_path)
    with open(solution_path, "r") as f:
        content = f.read()
    assert content == "I can only help with writing code. Please ask a coding-related question."

    # Verify execution DB status and iterations
    db = TestingSessionLocal()
    read_repo = ExecutionReadRepository(db)
    # Get all executions
    executions = read_repo.get_all_executions_for_user(user_db_id)
    assert len(executions) == 1
    exec_row = executions[0]
    assert exec_row.status == "success"
    assert exec_row.tries_used == 1

    # Get iterations
    iterations = read_repo.get_iterations(exec_row.id)
    assert len(iterations) == 1
    iter_row = iterations[0]
    assert iter_row.iteration_number == 1
    assert iter_row.generated_code == "I can only help with writing code. Please ask a coding-related question."
    assert iter_row.passed is True
    db.close()


def test_code_requirement_runs_normal_flow(monkeypatch):
    # Create a user in the test database
    db = TestingSessionLocal()
    user = User(google_id="g-test-user2", email="test2@test.com", name="Test User 2")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = str(user.id)
    user_db_id = user.id
    db.close()

    # Mock LLMService.generate
    generated_calls = []

    def mock_generate(self, prompt: str) -> str:
        generated_calls.append(prompt)
        if "You are a classifier" in prompt:
            # Classify as code request
            return "YES"
        elif "You are an expert Python software engineer" in prompt:
            # Generate code
            return "def add(a, b):\n    return a + b\n"
        elif "specializing in writing high-quality pytest test suites" in prompt:
            # Generate tests
            return "from solution import add\ndef test_add():\n    assert add(1, 2) == 3\n"
        return "YES"

    monkeypatch.setattr(LLMService, "generate", mock_generate)

    # Mock runner to return success
    from app.runner.runner import Runner
    class FakeRunnerResult:
        passed = True
        stdout = "test stdout"
        stderr = ""
        exit_code = 0

    monkeypatch.setattr(Runner, "run", lambda self, ws: FakeRunnerResult())

    orchestrator = Orchestrator()
    result = orchestrator.run("write a function to add two numbers", user_id=user_id)

    # Verify multiple LLM calls were made (classification, code generation, test generation)
    assert len(generated_calls) >= 3

    # Verify result
    assert result.passed is True
    assert result.tries_used == 1

    # Verify solution.py contains the generated code, not the error text
    solution_path = os.path.join(result.workspace, "solution.py")
    assert os.path.exists(solution_path)
    with open(solution_path, "r") as f:
        content = f.read()
    assert "def add" in content

    # Verify DB contains the normal iteration code
    db = TestingSessionLocal()
    read_repo = ExecutionReadRepository(db)
    executions = read_repo.get_all_executions_for_user(user_db_id)
    assert len(executions) == 1
    iterations = read_repo.get_iterations(executions[0].id)
    assert len(iterations) == 1
    assert "def add" in iterations[0].generated_code
    db.close()
