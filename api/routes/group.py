from fastapi import APIRouter
from api.config.database import db_dependency


router = APIRouter(
    prefix="/group",
)

@router.delete("/delete", tags=["group"])
async def delete(id: int, db: db_dependency):
    return

@router.get("/get", tags=["group"])
async def get(id: int, db: db_dependency):
    return    