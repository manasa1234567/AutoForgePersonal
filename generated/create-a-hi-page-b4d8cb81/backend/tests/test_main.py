from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# We'll override the dependency to use a fresh in-memory DB for tests
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock the authorization header with the valid-token
headers = {"Authorization": "Bearer valid-token"}


def test_create_hi_page_success():
    response = client.post("/pages/hi", headers=headers)
    assert response.status_code == 201
    assert response.json() == {"message": "The 'hi' page was created successfully."}


def test_create_hi_page_duplicate():
    # First create
    resp1 = client.post("/pages/hi", headers=headers)
    assert resp1.status_code == 201
    # Attempt duplicate
    resp2 = client.post("/pages/hi", headers=headers)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"]


def test_create_hi_page_unauthorized():
    response = client.post("/pages/hi")  # No auth
    assert response.status_code == 401


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
