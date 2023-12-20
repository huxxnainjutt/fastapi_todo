from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes import users, todos


app = FastAPI()

# print(db)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}


app.include_router(users.router, tags=['Auth'], prefix='/api/auth')
app.include_router(todos.router, tags=['Todo'], prefix='/api/todos')

if __name__ == '__main__':  # this indicates that this a script to be run
    uvicorn.run("main:app", port=8002, log_level="info", reload=True)
