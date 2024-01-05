from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from ..models.users import User, LoginUserSchema, ForgetPasswordSchema, PasswordReset
from ..models.response import IResponse
from app.db import db
from ..utils import get_password_hash, password_reset
from .. import utils
from .. import oauth2

router = APIRouter()


@router.post("/signup", response_description="Register New User", response_model=IResponse,
             status_code=status.HTTP_201_CREATED)
async def signup(user: User = Body):
    try:
        user_info = jsonable_encoder(user)
        if len(user_info.keys()) == 0:
            raise HTTPException(status_code=400, detail="Missing required fields")
        # check for duplications

        if 'name' in user_info:
            user_info['name'] = user_info['name'].lower()

        username_found = db["users"].find_one({"name": user_info["name"]})
        email_found = db["users"].find_one({"email": user_info["email"]})
        if username_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="There already is a user by that name")
        if email_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="There already is a user by that email")
        # hash the user password
        user_info["password"] = get_password_hash(user_info["password"])
        new_user = db["users"].insert_one(user_info)
        created_user = db["users"].find_one({"_id": new_user.inserted_id})
        return {"message": "Success", "data": {"name": f"{created_user['name']}", "email": f"{created_user['email']}"}}
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.post('/login', response_description="Login User", response_model=IResponse, status_code=status.HTTP_200_OK)
async def login_user(user_credentials: LoginUserSchema):
    try:
        if not user_credentials.email or not user_credentials.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Field")

        user = db["users"].find_one({"email": user_credentials.email.lower()})
        if user and utils.verify_password(user_credentials.password, user["password"]):
            # Create access token
            access_token = oauth2.create_access_token(payload={
                "id": str(user["_id"]),
            })
            return {"message": "Logged in successfully",
                    "data": {"token": access_token, "name": user["name"], "email": user["email"],
                             "_id": str(user["_id"])}}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user credentials"
            )

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.get('/profile', response_model=IResponse)
async def get_profile(current_user=Depends(oauth2.get_current_user)):
    try:
        return {"message": "Profile retrieved successfully", "data": current_user}
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.post('/forgotPassword', response_model=IResponse)
async def forgot_password(user_info: ForgetPasswordSchema):
    try:
        user_info = jsonable_encoder(user_info)
        print(user_info['email'])
        user = db["users"].find_one({"email": user_info['email']})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        token = oauth2.create_access_token(payload={
            "id": str(user["_id"]),
        })

        reset_link = f"http://localhost:3000/reset-password/{jsonable_encoder(token)}"

        print("Hello")

        await password_reset("Password Reset", user["email"],
                             {
                                 "title": "Password Reset",
                                 "name": user["name"],
                                 "reset_link": reset_link
                             }
                             )
        return {"message": "Email has been sent with instructions to reset your password.", "data": {}}

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.post('/reset-password/{token}', response_model=IResponse)
async def reset_password(token: str, new_password: PasswordReset):
    print(token)
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Token")
        new_password = jsonable_encoder(new_password)

        request_data = {k: v for k, v in new_password.items()
                        if v is not None}
        # get the hashed version of the password
        request_data["password"] = get_password_hash(request_data["password"])
        if len(request_data) >= 1:
            # use token to get the current user
            user = await oauth2.get_current_user(token)
            print(user)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Token")

            # update the password of the current user
            update_result = db["users"].update_one({"_id": ObjectId(user["_id"])}, {"$set": request_data})
            if update_result.modified_count == 1:
                # get the newly updated current user and return as a response
                updated_student =  db["users"].find_one({"_id": ObjectId(user["_id"])})
                if updated_student is not None:
                    return {'message': 'Password reset successful', 'data': {}}
            else:
                raise HTTPException(status_code=400, detail=f"Something went wrong")

    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")
