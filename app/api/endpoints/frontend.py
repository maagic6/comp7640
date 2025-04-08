from fastapi import APIRouter

router = APIRouter(
    tags=["Frontend"],
    include_in_schema=False
)