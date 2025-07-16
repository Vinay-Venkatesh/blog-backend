from typing import Optional
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel # schema validator
from random import randrange
from psycopg.rows import dict_row
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import engine, get_db
import models

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
        {"title": "favorite foods", "content": "pizza", "id": 2}
    ]

def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post

def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post['id'] == id:
            return i
        
@app.get("/")
def root():
    return {"message": "Hello World"}

'''
    what the heck is db: Session = Depends(get_db)
    db - variable name
    get_db - func() from database model
'''
@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    return {"data": posts} # fastapi will serailise the json automatically and returns it

@app.post("/posts", status_code=status.HTTP_201_CREATED)
# status_code=status.HTTP_201_CREATED In the decorator - to override the default status code on success.
def create_posts(new_post: Post, db: Session = Depends(get_db)): 
    '''
    SQL code without using sqlachemy..
    '''
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    # data = cursor.fetchone() # this will get the returning data from previous line
    # conn.commit()

    new_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published)

    db.add(new_post)
    db.commit() # commits the data to database
    db.refresh(new_post) # returns the new post that gets added in the above commit.

    return {"data": new_post}

@app.get("/posts/{id}")
def get_posts(id: int, db: Session = Depends(get_db)): # id gets converted to int here, so we don't have to explictly convert it in find_post(int(id))
    
    # converting to string because the query executing here needs a string.
    # execute() expects a tuple hence comma is mandatory at the end [ (str(id),) ] if not it will considered as string and will cause error

    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),)) 
    # data = cursor.fetchone()
    
    # using sqlachemy for database operation.
    data = db.query(models.Post).filter(models.Post.id == id).first()
    # .first() --> returns the first instance of the post with that id.
    # .all() --> returns all the posts with the id.

    if not data:
        # 
        # wihtout using HTTPException
        #
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found.."}
        #
        #

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found..")
    return {"details": data}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" DELETE FROM posts where id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # using sqlachemy
    post = db.query(models.Post).filter(models.Post.id == id)
    

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")    
    
    post.delete(synchronize_session=False)
    db.commit()

@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s where id = %s returning *""", (post.title, post.content, post.published, (str(id))))
    # updated_post = cursor.fetchone()
    # conn.commit()

    # sqlachemy method
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")    
    
    #post_query.update({'title': post.title, 'content': post.content,'published': post.published}, synchronize_session=False)
    
    # passing the whole post.dict instead of individual data as above.
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return {'data': post_query.first()}