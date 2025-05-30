from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from database import SESSION_LOCAL
from models import Todos
from routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
	db = SESSION_LOCAL()

	try:
		yield db
	finally:
		db.close()


DB_DEPENDENCY = Annotated[Session, Depends(get_db)]
USER_DEPENDENCY = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: USER_DEPENDENCY, db: DB_DEPENDENCY):
	if user is None or user["user_role"] != "admin":
		raise HTTPException(status_code=401, detail="Unauthorized")

	return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: USER_DEPENDENCY, db: DB_DEPENDENCY, todo_id: int = Path(gt=0)):
	if user is None or user["user_role"] != "admin":
		raise HTTPException(status_code=401, detail="Unauthorized")

	todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

	if todo_model is None:
		raise HTTPException(status_code=404, detail="Todo not found")

	db.delete(todo_model)
	db.commit()
