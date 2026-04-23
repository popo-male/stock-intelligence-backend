from fastapi import APIRouter
from src.api.v1.endpoints.stock import router as stock_router

router = APIRouter(
    prefix="/v1",
)

router.include_router(
    stock_router,
    prefix="/stocks",
    tags=["stocks"],
)
