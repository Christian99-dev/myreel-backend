from fastapi import APIRouter
from api.config.database import db_dependency


router = APIRouter(
    prefix="/group",
)

@router.delete("/delete")
def delete(id: int, db: db_dependency):
    return

@router.get("/get")
def get(id: int, db: db_dependency):
    return    