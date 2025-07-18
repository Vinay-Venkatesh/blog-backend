import models
from database import engine, get_db
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel  # schema validator
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# pydantic model defines the data structure used in request/response.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


load_dotenv()

my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favorite foods", "content": "pizza", "id": 2},
]


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World"}


"""
    what the heck is db: Session = Depends(get_db)
    db - variable name
    get_db - func() from database model
"""


@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return {
        "data": posts
    }  # fastapi will serailise the json automatically and returns it


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(new_post: Post, db: Session = Depends(get_db)):
    """
    SQL code without using sqlachemy..
    """

    new_post = models.Post(
        title=new_post.title, content=new_post.content, published=new_post.published
    )

    db.add(new_post)
    db.commit()  # commits the data to database
    db.refresh(new_post)  # returns the new post that gets added in the above commit.

    return {"data": new_post}


@app.get("/posts/{id}")
def get_posts(id: int, db: Session = Depends(get_db)):

    # using sqlachemy for database operation.
    data = db.query(models.Post).filter(models.Post.id == id).first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found..",
        )
    return {"details": data}


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


@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):

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
    return {"data": post_query.first()}
