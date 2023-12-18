# library imports
from typing import Dict
import jwt
from jwt import DecodeError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from bson import ObjectId

from app.db import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# get config values
SECRET_KEY = settings.JWT_PRIVATE_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRES_IN


def create_access_token(payload: Dict):
    to_encode = payload.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration_time})

    jw_token = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    print(jw_token)
    return jw_token


def verify_access_token(token: str, credential_exception: HTTPException):
    try:
        print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("id")

        if not id:
            raise credential_exception

        return {"id": id}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify token, token expired",
        headers={"WWW-AUTHENTICATE": "Bearer"},
    )

    token_data = verify_access_token(token=token, credential_exception=credential_exception)

    current_user_id = token_data.get("id")
    if not current_user_id:
        raise credential_exception

    current_user = db["users"].find_one({"_id": ObjectId(current_user_id)})
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"email": current_user["email"], "name": current_user["name"], "_id": current_user_id}
