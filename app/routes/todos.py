from fastapi import APIRouter, Body, Query, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from ..models.todos import Todo, TodoUpdate, TodoComplete, TodoResponse
from ..models.response import IResponse, PaginatedResponse
from app.db import db
from .. import oauth2
from datetime import datetime, timedelta,date
from ..utils import CustomEncoder
import json

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TodoResponse])
async def get_all_todo(page: int = Query(default=1, ge=1),
                       limit: int = Query(default=10, le=50),
                       is_completed: bool = Query(None),
                       current_date: str = Query(None), current_user=Depends(oauth2.get_current_user)):
    try:

        if current_date is None:
            # If current_date is not provided, default to today's date
            current_date = datetime.now().date()
        else:
            # Parse the received string back into a date object
            current_date = date.fromisoformat(current_date)

        # Calculate start and end of the current day
        start_of_day = datetime.combine(current_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1) - timedelta.resolution

        filters = {"created_at": {"$gte": start_of_day, "$lte": end_of_day}, "author": ObjectId(current_user['_id'])}
        if is_completed is not None:
            filters["is_completed"] = is_completed
        skip = (page - 1) * limit

        print(filters)
        # Fetch todos based on filter and pagination
        todos = db['todos'].find(filters).sort("created_at", -1).skip(skip).limit(limit)

        todos_list = list(todos)
        todos_list = json.dumps(todos_list, default=str)
        todos_list = json.loads(todos_list)
        if not todos_list:
            raise HTTPException(status_code=404, detail="No todos found")
        # Retrieve total count based on the date range
        total_count = db['todos'].count_documents(filters)
        return {"message": 'Todos retrieved successfully', "items": todos_list, "count": total_count}
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.post("/", response_model=IResponse)
async def create_todo(todo: Todo, current_user=Depends(oauth2.get_current_user)):
    try:
        todo = jsonable_encoder(todo)
        todo["author"] = ObjectId(current_user["_id"])
        todo["created_at"] = datetime.utcnow()
        # create todo collection
        new_todo_content = db["todos"].insert_one(todo)

        # get created post content
        created_todo = db["todos"].find_one({"_id": new_todo_content.inserted_id})

        return {"message": "Todo created successfully", "data": {"title": created_todo['title'],
                                                                 "description": created_todo['description'],
                                                                 "author": str(created_todo['author']),
                                                                 "_id": str(created_todo['_id'])}}

    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.get("/{todo_id}", response_model=IResponse)
async def get_todo(todo_id: str, current_user=Depends(oauth2.get_current_user)):
    try:

        if not todo_id:
            raise HTTPException(status_code=400, detail="Missing id parameter")

        todo = db["todos"].find_one({"_id": ObjectId(todo_id)})

        if not todo:
            raise HTTPException(status_code=404, detail="Not Found")

        return {"message": "todo retrieved successfully",
                "data": {"title": todo['title'], "description": todo['description'], "author": str(todo['author']),
                         "is_completed": todo['is_completed'],
                         "_id": str(todo['_id'])}}

    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.put("/{todo_id}", response_model=IResponse)
async def update_todo(todo_id: str, todo: TodoUpdate, current_user=Depends(oauth2.get_current_user)):
    try:
        if not todo_id:
            raise HTTPException(status_code=400, detail="Missing id parameter")
        todo = jsonable_encoder(todo)
        todo_data = {k: v for k, v in todo.items() if v is not None}
        if len(todo_data) >= 1:
            update_result = db["todos"].update_one(
                {"_id": ObjectId(todo_id)}, {"$set": todo_data}
            )

            if update_result.modified_count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found")
        if (
                todo := db["todos"].find_one({"_id": ObjectId(todo_id)})
        ) is not None:
            return {"message": "todo updated successfully",
                    "data": {"title": todo['title'], "description": todo['description'], "author": str(todo['author']),
                             "is_completed": todo['is_completed'],
                             "_id": str(todo['_id'])}}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {todo_id} not found")
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.patch("/{todoId}/complete", response_model=IResponse)
async def complete_todo(todoId: str, todo: TodoComplete, current_user=Depends(oauth2.get_current_user)):
    try:
        if not todoId:
            raise HTTPException(status_code=400, detail="Missing id parameter")
        todo = jsonable_encoder(todo)
        todo_data = {k: v for k, v in todo.items() if v is not None}
        if len(todo_data) >= 1:
            update_result = db["todos"].update_one(
                {"_id": ObjectId(todoId)}, {"$set": todo_data}
            )

            if update_result.modified_count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found")
        if (
                todo := db["todos"].find_one({"_id": ObjectId(todoId)})
        ) is not None:
            return {"message": "todo completed successfully",
                    "data": {"title": todo['title'], "description": todo['description'], "author": str(todo['author']),
                             "is_completed": todo['is_completed'],
                             "_id": str(todo['_id'])}}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {todoId} not found")
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")


@router.delete("/{todo_id}", response_model=IResponse, status_code=status.HTTP_200_OK)
async def complete_todo(todo_id: str, current_user=Depends(oauth2.get_current_user)):
    try:
        delete_result = db["todos"].delete_one({"_id": ObjectId(todo_id)})

        if delete_result.deleted_count == 1:
            return {"message": "Todo deleted successfully", "data": {}}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found")
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"{e.detail}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Something went wrong")
