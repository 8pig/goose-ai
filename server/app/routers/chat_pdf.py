from fastapi import APIRouter, UploadFile, File, Path, Query  # 添加 Path 导入
import PyPDF2  # 需要安装: pip install pypdf2
import fitz  # 注意导入名称


import os

from fastapi.params import Form

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


@router.post("/upload_with_highlight/{chatId}")
async def upload_and_highlight_pdf(
        chatId: str = Path(..., description="通过路径参数传递的chatId"),
        file: UploadFile = File(..., description="上传的PDF文件", media_type="application/pdf"),
        keywords: str = Form(default="", description="要高亮的关键字，多个关键字用逗号分隔")
):
    if file.content_type != "application/pdf":
        return {"error": "只支持PDF文件"}

    contents = await file.read()
    filename = file.filename
    file_path = f"static/pdf/{chatId}_{filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(contents)

    # 总是进行高亮处理，即使没有关键词也创建一个副本
    highlighted_path = await highlight_keywords_in_pdf(file_path, keywords, chatId, filename)
    return {
        "filename": filename,
        "highlighted_file": highlighted_path,
        "message": f"PDF已上传{'并高亮关键字: ' + keywords if keywords else ', 未指定关键字'}"
    }


async def highlight_keywords_in_pdf(original_path: str, keywords_str: str, chat_id: str, original_filename: str):
    """辅助函数：在PDF中高亮关键字"""
    doc = fitz.open(original_path)
    keyword_list = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    print("keyword_list")
    print(keyword_list)
    # 即使没有关键词也会创建新的PDF文件
    for page_num in range(doc.page_count):
        page = doc[page_num]
        for keyword in keyword_list:
            text_instances = page.search_for(keyword)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                # 设置高亮颜色，黄色带透明度
                highlight.set_colors(stroke=[1, 1, 0])
                highlight.update()

    highlighted_path = f"static/pdf/{chat_id}_highlighted_{original_filename}"
    # 保存时确保注释被嵌入
    doc.save(highlighted_path, garbage=4, deflate=True, clean=True)
    doc.close()

    return highlighted_path
