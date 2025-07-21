from typing import List

import models
import schema
import utils
from database import engine, get_db
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()


@app.get("/")
def root():
    return {"message": "Hello World"}


"""
    what the heck is db: Session = Depends(get_db)
    db - variable name
    get_db - func() from database model

    List[schema.Post] = List is used to return all the posts as list
"""


@app.get("/posts", response_model=List[schema.Post])
def get_all_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return posts  # fastapi will serailise the json automatically and returns it


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_posts(new_post: schema.CreatePost, db: Session = Depends(get_db)):
    """
    SQL ops using sqlachemy..
    """

    # new_post = models.Post(
    #     title=new_post.title, content=new_post.content, published=new_post.published
    # )

    new_post = models.Post(**new_post.model_dump())

    db.add(new_post)
    db.commit()  # commits the data to database
    db.refresh(new_post)  # returns the new post that gets added in the above commit.

    return new_post


@app.get("/posts/{id}", response_model=schema.Post)
def get_posts(id: int, db: Session = Depends(get_db)):

    # using sqlachemy for database operation.
    data = db.query(models.Post).filter(models.Post.id == id).first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found..",
        )
    return data


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    # using sqlachemy
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exists",
        )

    post.delete(synchronize_session=False)
    db.commit()


@app.put("/posts/{id}", response_model=schema.Post)
def update_post(id: int, post: schema.PostBase, db: Session = Depends(get_db)):

    # sqlachemy method
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exists",
        )

    # passing the whole post.dict instead of individual data as above.
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=schema.UserResponse
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
