from datetime import datetime

from pydantic import BaseModel, EmailStr  # schema validator

# below is the pydantic model defines the data structure used in request.


# Base Class
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# inheritance of PostBase Class.
class CreatePost(PostBase):
    pass


# below is the pydantic model defines the data structure used in response.

# inheritance of PostBase Class.

"""
output:
{
    "id": 12, # from Post class
    "title: "sample_title", # from base class
    "content": "sample content", # from base class
    "published": True, # from base class
    "created_at": <timestamp> # from Post class
}
"""


class Post(PostBase):
    id: int
    created_at: datetime

    """
    To ensure that the return type is not ORM object
    rather its a dict, the response expects only of type dict.
    """

    class Config:
        ORM = True


class UserCreate(BaseModel):
    email: EmailStr  # EmailStr is used to valid the input email format.
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

    class Config:
        ORM = True
