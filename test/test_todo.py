from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app
from ..routers.todos import get_current_user, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()


def override_get_current_user():
	return {"id": 1, 'username': 'test_user', 'user_role': 'user'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_read_all_authenticated():
	response = client.get("/todos/")

	assert response.status_code == status.HTTP_200_OK
	assert response.json() == []
