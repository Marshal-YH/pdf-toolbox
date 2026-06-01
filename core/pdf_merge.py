import fitz
import os

def merge_pdfs(input_paths: list[str], output_path: str) -> int:
    """
    合并多个 PDF 文件
    
    Args:
        input_paths: 输入文件路径列表
        output_path: 输出文件路径
    
    Returns:
        总页数
    """
    if len(input_paths) < 2:
        raise ValueError("合并至少需要 2 个 PDF 文件")
    merger = fitz.open()
    total_pages = 0
    
    for path in input_paths:
        src = fitz.open(path)
        merger.insert_pdf(src)
        total_pages += src.page_count
        src.close()
    
    merger.save(output_path, deflate=True)
    merger.close()
    return total_pages


def get_pdf_page_count(path: str) -> int:
    """获取 PDF 页数"""
    doc = fitz.open(path)
    count = doc.page_count
    doc.close()
    return count


def get_pdf_info(path: str) -> dict:
    """获取 PDF 详细信息"""
    doc = fitz.open(path)
    info = {
        "page_count": doc.page_count,
        "file_size": os.path.getsize(path),
        "has_annotations": len(list(doc.pages(0, doc.page_count))) > 0,
    }
    # 检查是否有注释/书签
    try:
        info["toc"] = doc.get_toc()
    except:
        info["toc"] = []
    doc.close()
    return info
