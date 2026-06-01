import fitz
import os
import re

def parse_page_ranges(ranges_str: str, total_pages: int) -> list[list[int]]:
    """
    解析页码范围字符串
    
    支持格式:
    - "1-10, 11-20, 21-30" → [[1,10], [11,20], [21,30]]
    - "1,3,5-8,12"        → [[1,1], [3,3], [5,8], [12,12]]
    - "每 5 页一份"         → 自动按固定页数
    - "拆成 4 份"           → 自动均分
    """
    text = ranges_str.strip()
    
    # 检测中文模式
    if "每" in text and "页" in text:
        nums = re.findall(r'\d+', text)
        if nums:
            pages_per = int(nums[0])
            return _fixed_pages_to_ranges(total_pages, pages_per)
    
    if "拆成" in text and "份" in text:
        nums = re.findall(r'\d+', text)
        if nums:
            n = int(nums[0])
            return _evenly_to_ranges(total_pages, n)
    
    # 标准格式解析: "1-10, 11-20" 或 "1,3,5"
    # 支持中文逗号（，）和英文逗号（,）
    text = text.replace("，", ",")
    parts = [p.strip() for p in text.split(",") if p.strip()]
    ranges = []
    for part in parts:
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                ranges.append([int(a.strip()), int(b.strip())])
            except ValueError:
                continue
        else:
            try:
                n = int(part)
                ranges.append([n, n])
            except ValueError:
                continue
    
    return _validate_ranges(ranges, total_pages)


def _fixed_pages_to_ranges(total_pages: int, pages_per: int) -> list[list[int]]:
    """按固定页数拆分"""
    ranges = []
    for start in range(1, total_pages + 1, pages_per):
        end = min(start + pages_per - 1, total_pages)
        ranges.append([start, end])
    return ranges


def _evenly_to_ranges(total_pages: int, num_parts: int) -> list[list[int]]:
    """均分为 N 份"""
    if num_parts <= 0:
        num_parts = 1
    pages_per_file = max(1, total_pages // num_parts)
    extra = total_pages % num_parts
    
    ranges = []
    current = 1
    for i in range(num_parts):
        end = current + pages_per_file - 1
        if i < extra:
            end += 1
        if current <= total_pages:
            ranges.append([current, min(end, total_pages)])
        current = end + 1
    return ranges


def _validate_ranges(ranges: list[list[int]], total_pages: int) -> list[list[int]]:
    """验证并修正页码范围"""
    valid = []
    for s, e in ranges:
        s = max(1, min(s, total_pages))
        e = max(s, min(e, total_pages))
        valid.append([s, e])
    return valid


def split_by_ranges(
    input_path: str, output_dir: str, ranges: list[list[int]],
    name_template: str = "{name}_p{start}-{end}.pdf"
) -> list[str]:
    """
    按页码范围拆分 PDF
    
    Args:
        input_path: 输入 PDF 路径
        output_dir: 输出目录
        ranges: [[1,10], [11,20], ...] (页码从 1 开始)
        name_template: 命名模板 {name}{start}{end}{index}
    
    Returns:
        输出文件路径列表
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_files = []
    
    for i, (start, end) in enumerate(ranges):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
        
        filename = name_template.format(
            name=base_name, start=start, end=end, index=i+1
        )
        out_path = os.path.join(output_dir, safe_filename(filename))
        new_doc.save(out_path, deflate=True)
        new_doc.close()
        output_files.append(out_path)
    
    doc.close()
    return output_files


def safe_filename(name: str) -> str:
    import re
    return re.sub(r'[\\/:*?"<>|]', '_', name)


# 便捷方法
def split_by_fixed_pages(input_path: str, output_dir: str, pages_per_file: int,
                         name_template: str = "{name}_p{start}-{end}.pdf") -> list[str]:
    doc = fitz.open(input_path)
    total = doc.page_count
    doc.close()
    ranges = _fixed_pages_to_ranges(total, pages_per_file)
    return split_by_ranges(input_path, output_dir, ranges, name_template)


def split_evenly(input_path: str, output_dir: str, num_parts: int,
                 name_template: str = "{name}_p{start}-{end}.pdf") -> list[str]:
    doc = fitz.open(input_path)
    total = doc.page_count
    doc.close()
    ranges = _evenly_to_ranges(total, num_parts)
    return split_by_ranges(input_path, output_dir, ranges, name_template)
