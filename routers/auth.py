from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SESSION_LOCAL
from models import Users

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "02cdd9145dcef59b98d017944d33825d89ea7b561060838adf73afd6447370ac"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
	db = SESSION_LOCAL()
	try:
		yield db
	finally:
		db.close()


DB_DEPENDENCY = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session):
	user = db.query(Users).filter(Users.username.__eq__(username)).one_or_none()

	if not user or not bcrypt_context.verify(password, str(user.hashed_password)):
		return False

	return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
	encode = {"sub": username, "id": user_id, "role": role}
	expires = datetime.now(timezone.utc) + expires_delta
	encode.update({"exp": expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

		username = payload.get("sub")
		user_id = payload.get("id")
		user_role = payload.get("role")

		if user_id is None or username is None:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Could not validate credentials",
			)

		return {"username": username, "id": user_id, "user_role": user_role}
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
		)


class CreateUserRequest(BaseModel):
	username: str
	email: str
	first_name: str
	last_name: str
	password: str
	phone_number: str
	role: str


class Token(BaseModel):
	access_token: str
	token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: DB_DEPENDENCY, create_user_request: CreateUserRequest):
	# Check if user with email already exists
	existing_user = db.query(Users).filter(Users.email == create_user_request.email).first()
	if existing_user:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

	# Check if username is taken
	existing_username = db.query(Users).filter(Users.username == create_user_request.username).first()
	if existing_username:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

	try:
		hashed_password = bcrypt_context.hash(create_user_request.password)

		create_user_model = Users(
			email=create_user_request.email,
			username=create_user_request.username,
			first_name=create_user_request.first_name,
			last_name=create_user_request.last_name,
			role=create_user_request.role,
			hashed_password=hashed_password,
			is_active=True,
			phone_number=create_user_request.phone_number,
		)

		db.add(create_user_model)
		db.commit()

		return {"message": "User created successfully"}

	except Exception as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"An error occurred while creating the user: {str(e)}",
		)


@router.post("/token", response_model=Token)
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: DB_DEPENDENCY,
):
	user = authenticate_user(form_data.username, form_data.password, db)

	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
		)

	token = create_access_token(
		username=str(user.username),
		user_id=int(user.id),  # type: ignore
		expires_delta=timedelta(minutes=20),
		role=str(user.role),
	)

	return {"success": True, "access_token": token, "token_type": "bearer"}
