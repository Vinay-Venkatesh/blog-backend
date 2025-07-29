import database
import models
import oauth
import utils
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])

"""
OAuth2PasswordRequestForm input fields
{
    "username": "email_id",
    "password: "password"
}
"""


@router.post("/login")
def login(
    user_credentails: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(
            models.User.email == user_credentails.username
        )  # username field from OAuth2PasswordRequestForm
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    if not utils.verify(user_credentails.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = oauth.create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
