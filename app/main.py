from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel # schema validator
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

# class Post extends BaeModel of pydantic
class Post(BaseModel): 
    # schema definition for new posts.
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg.connect(dbname='fastapi', user=os.getenv('postgres_username'), password=os.getenv('postgres_password'), row_factory=dict_row) # row_factory=dict_row gives the column name along with the values.
        cursor = conn.cursor()
        print("database connection was successful")
        break
    except Exception as error:
        print("database connection failed.")
        print("Error: ", error)
        time.sleep(2)



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

@app.get("/posts")
def get_all_posts():
    cursor.execute("""SELECT * FROM POSTS""")
    posts = cursor.fetchall()
    return {"data": posts} # fastapi will serailise the json automatically and returns it

@app.post("/posts", status_code=status.HTTP_201_CREATED)
# status_code=status.HTTP_201_CREATED In the decorator - to override the default status code on success.
def create_posts(new_post: Post): 
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    data = cursor.fetchone() # this will get the returning data from previous line
    conn.commit()

    return {"data": data}

@app.get("/posts/{id}")
def get_posts(id: int, response: Response): # id gets converted to int here, so we don't have to explictly convert it in find_post(int(id))
    
    # converting to string because the query executing here needs a string.
    # execute() expects a tuple hence comma is mandatory at the end [ (str(id),) ] if not it will considered as string and will cause error

    cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),)) 
    data = cursor.fetchone()
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
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts where id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")    
    
    return {'data': deleted_post}

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s where id = %s returning *""", (post.title, post.content, post.published, (str(id))))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")    
    
    return {'data': updated_post}