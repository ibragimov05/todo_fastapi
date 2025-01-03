from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SESSION_LOCAL
from models import Todos
from routers.auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])


def get_db():
	db = SESSION_LOCAL()

	try:
		yield db
	finally:
		db.close()


DB_DEPENDENCY = Annotated[Session, Depends(get_db)]
USER_DEPENDENCY = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
	title: str = Field(min_length=3)
	description: str = Field(min_length=3, max_length=100)
	priority: int = Field(gt=0, lt=6)
	complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: USER_DEPENDENCY, db: DB_DEPENDENCY):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	return db.query(Todos).filter(Todos.owner_id == user["id"]).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_single_todo(user: USER_DEPENDENCY, db: DB_DEPENDENCY, todo_id: int = Path(gt=0)):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user["id"]).first()

	if todo_id is not None:
		return todo_model

	raise HTTPException(status_code=404, detail="TODO not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: USER_DEPENDENCY, db: DB_DEPENDENCY, todo_request: TodoRequest) -> None:
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	todo_model = Todos(**todo_request.model_dump(), owner_id=user["id"])

	db.add(todo_model)
	db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
	user: USER_DEPENDENCY,
	db: DB_DEPENDENCY,
	todo_request: TodoRequest,
	todo_id: int = Path(gt=0),
) -> None:
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user["id"]).first()

	if todo_model is None:
		raise HTTPException(status_code=404, detail="TODO not found")

	for key, value in todo_request.model_dump().items():
		setattr(todo_model, key, value)

	db.add(todo_model)
	db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: USER_DEPENDENCY, db: DB_DEPENDENCY, todo_id: int = Path(gt=0)):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user["id"]).first()

	if todo_model is None:
		raise HTTPException(status_code=404, detail="Todo not found")

	db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user["id"]).delete()
	db.commit()
