from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.models import CategoryCreate  
# from app.models import CategoryResponse  # Removed because it is not defined
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

category_router = APIRouter(tags=["Category Management"])
todo_router = APIRouter(tags=["Todo Management"])


@category_router.post("/category")
def create_category(
    category_data: CategoryCreate,
    db: SessionDep,
    user: AuthDep
):
    if user.id is None:
        raise HTTPException(status_code=401, detail="User ID is missing")
    category = Category(
        text=category_data.text,
        user_id=user.id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

@todo_router.post("/todo/{todo_id}/category/{cat_id}")
def add_category_to_todo(
    todo_id: int,
    cat_id: int,
    db: SessionDep,
    user: AuthDep
):
    todo = db.get(Todo, todo_id)
    category = db.get(Category, cat_id)

    if not todo or todo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Todo not found")

    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    todo.categories.append(category)

    db.add(todo)
    db.commit()

    return {"message": "Category added to todo"}

@todo_router.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category_from_todo(
    todo_id: int,
    cat_id: int,
    db: SessionDep,
    user: AuthDep
):
    todo = db.get(Todo, todo_id)
    category = db.get(Category, cat_id)

    if not todo or todo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Todo not found")

    if category not in todo.categories:
        raise HTTPException(status_code=404, detail="Category not assigned")

    todo.categories.remove(category)

    db.add(todo)
    db.commit()

    return {"message": "Category removed from todo"}

@category_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(
    cat_id: int,
    db: SessionDep,
    user: AuthDep
):
    category = db.get(Category, cat_id)

    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    return category.todos