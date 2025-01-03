from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SESSION_LOCAL
from models import Users
from routers.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


def get_db():
	db = SESSION_LOCAL()

	try:
		yield db
	finally:
		db.close()


DB_DEPENDENCY = Annotated[Session, Depends(get_db)]
USER_DEPENDENCY = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
	password: str
	new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: USER_DEPENDENCY, db: DB_DEPENDENCY):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	# Correctly fetch the user model
	user_model = db.query(Users).filter(Users.id == user["id"]).first()

	if not user_model:
		raise HTTPException(status_code=404, detail="User not found")

	return user_model


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: USER_DEPENDENCY, db: DB_DEPENDENCY, user_verification: UserVerification):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	user_model = db.query(Users).filter(Users.id == user["id"]).first()

	if not user_model:
		raise HTTPException(status_code=404, detail="User not found")

	if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
		raise HTTPException(status_code=401, detail="Password incorrect")

	user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

	db.add(user_model)
	db.commit()


@router.put("/phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def edit_phone_number(user: USER_DEPENDENCY, db: DB_DEPENDENCY, phone_number: str):
	if user is None:
		raise HTTPException(status_code=401, detail="Unauthorized")

	user_id = user.get('id')
	if not user_id:
		raise HTTPException(status_code=400, detail="Invalid user ID")

	user_model = db.query(Users).filter(Users.id == user_id).first()

	user_model.phone_number = phone_number

	db.add(user_model)
	db.commit()
