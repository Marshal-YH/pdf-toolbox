import os
import subprocess
import platform
from datetime import datetime

TASK_NAMES = {
    "merge": "合并",
    "split": "拆分",
    "word": "Word转PDF",
    "batch": "批量",
    "Word": "Word转PDF",
    "PDF合并": "PDF合并",
    "PDF拆分": "PDF拆分",
    "PDF 合并": "PDF合并",
    "PDF 拆分": "PDF拆分",
    "Excel": "Excel转PDF",
}

BASE_DIR = os.path.expanduser("~/Documents/PDF_输出/")


def make_task_dir(task_type: str, source_name: str = "") -> str:
    """自动生成带时间戳的任务输出目录
    
    Args:
        task_type: 任务类型 (merge/split/word)
        source_name: 源文件名（可选）
    
    Returns:
        创建的目录路径
    """
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = TASK_NAMES.get(task_type, task_type)
    name_part = f"_{os.path.splitext(source_name)[0]}" if source_name else ""
    dir_name = f"{label}{name_part}_{now}"
    out_dir = os.path.join(BASE_DIR, dir_name)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def open_in_finder(path: str):
    """在 Finder 中打开指定路径"""
    if platform.system() == "Darwin":
        folder = os.path.dirname(path) if os.path.isfile(path) else path
        subprocess.Popen(["open", folder])


def get_file_info(path: str) -> dict:
    """获取文件基本信息"""
    stat = os.stat(path)
    size = stat.st_size
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    return {
        "name": name,
        "path": path,
        "size": size,
        "size_str": format_size(size),
        "ext": ext,
    }

def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / 1024 / 1024:.1f} MB"

def safe_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    import re
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def open_file(path: str):
    """系统默认方式打开文件"""
    if platform.system() == "Darwin":
        subprocess.run(["open", path])
    elif platform.system() == "Windows":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path])
