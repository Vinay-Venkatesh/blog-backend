import models
import schema
import utils
from database import engine, get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/users",
    tags=["Users"],  # to group the API's in Openapi doc at (http://127.0.0.1:8000/docs)
)

load_dotenv()


# /users/ -> /posts is coming from router prefix
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.UserResponse
)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    """
    SQL ops using sqlachemy..
    """

    # password hashing.
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())

    db.add(new_user)
    db.commit()  # commits the data to database
    db.refresh(new_user)  # returns the new user that gets added in the above commit.

    return new_user


# /users/{id} -> /posts is coming from router prefix
@router.get("/{id}", response_model=schema.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id :{id} does not exists",
        )

    return user
