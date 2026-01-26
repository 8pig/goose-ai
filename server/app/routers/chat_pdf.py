from fastapi import APIRouter, UploadFile, File, Path  # 添加 Path 导入
import os

router = APIRouter(
    prefix="/ai/pdf",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload/{chatId}")
async def upload_pdf(
    chatId: str = Path(..., description="通过路径参数传递的chatId"),
    file: UploadFile = File(..., description="上传的PDF文件", media_type="application/pdf")
):
    if file.content_type != "application/pdf":
        return {"error": "只支持PDF文件"}
    
    contents = await file.read()
    
    # 保存文件到 static/pdf 目录
    file_path = f"static/pdf/{chatId}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return {"filename": file.filename, "chatId": chatId, "size": len(contents)}