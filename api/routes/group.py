from fastapi import APIRouter, Depends
from api.config.database import Session, get_db


router = APIRouter(
    prefix="/group",
)

@router.delete("/delete", tags=["group"])
async def delete(id: int, db: Session = Depends(get_db)):
    return

@router.get("/get", tags=["group"])
async def get(id: int, db: Session = Depends(get_db)):
    return    