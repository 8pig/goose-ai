from fastapi import APIRouter, UploadFile, File, Path  # 添加 Path 导入
import PyPDF2  # 需要安装: pip install pypdf2

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
    filename = file.filename
    # 保存文件到 static/pdf 目录
    file_path = f"static/pdf/{chatId}_{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(contents)
    # 读取PDF内容
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            content = ""

            # 遍历每一页提取文本
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text() + "\n"

        return {"filename": filename, "content": content, "pages": len(pdf_reader.pages)}

    except Exception as e:
        return {"error": f"读取PDF失败: {str(e)}"}

# @router.get("/upload/{chatId}")
# async def read_pdf_content(
#     chatId: str = Path(..., description="聊天ID"),
#     filename: str = Path(..., description="PDF文件名")
# ):
#     # 构建文件路径
#     file_path = f"static/pdf/{chatId}_{filename}"

#     # 检查文件是否存在
#     if not os.path.exists(file_path):
#         return {"error": "文件不存在"}

#     # 读取PDF内容
#     try:
#         with open(file_path, "rb") as pdf_file:
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
#             content = ""

#             # 遍历每一页提取文本
#             for page_num in range(len(pdf_reader.pages)):
#                 page = pdf_reader.pages[page_num]
#                 content += page.extract_text() + "\n"

#         return {"filename": filename, "content": content, "pages": len(pdf_reader.pages)}

#     except Exception as e:
#         return {"error": f"读取PDF失败: {str(e)}"}

