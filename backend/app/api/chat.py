from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def chat_skeleton_status():
    return {"module": "chat", "status": "skeleton_ready", "sprint": 6}
