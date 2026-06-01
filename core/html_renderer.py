import os
import sys

# WeasyPrint 需要系统库路径（必须在 import weasyprint 之前设置）
os.environ.setdefault(
    "DYLD_FALLBACK_LIBRARY_PATH",
    "/opt/homebrew/lib"
)

# 现在导入 weasyprint
import weasyprint

def render_html_to_pdf(html_content: str, output_path: str, quality: str = "标准") -> int:
    """
    将 HTML 渲染为 PDF

    Args:
        html_content: HTML 字符串
        output_path: 输出 PDF 路径
        quality: 质量选项（标准/高清/最小体积）

    Returns:
        总页数
    """
    # 根据质量调整 CSS
    quality_css = _get_quality_css(quality)

    # 注入质量 CSS 到 HTML head 中
    modified_html = html_content.replace(
        "</head>",
        f"<style>{quality_css}</style></head>"
    )

    doc = weasyprint.HTML(string=modified_html).render()
    doc.write_pdf(output_path)

    return len(doc.pages)


def _get_quality_css(quality: str) -> str:
    """根据质量设置生成不同的 CSS"""
    if quality == "高清":
        return """
            @page { size: A4; margin: 30mm 32mm; }
            body { font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", serif;
                   font-size: 14pt; line-height: 2.0; color: #1F2937; }
            h1 { font-size: 24pt; font-weight: 700; color: #111827; margin-top: 28pt; margin-bottom: 14pt; }
            h2 { font-size: 20pt; font-weight: 600; color: #1F2937; margin-top: 20pt; margin-bottom: 10pt; }
            h3 { font-size: 16pt; font-weight: 600; color: #374151; margin-top: 16pt; margin-bottom: 8pt; }
            p { margin: 8pt 0; text-indent: 0; }
            table { border-collapse: collapse; width: 100%; margin: 12pt 0; }
            th, td { border: 1px solid #D1D5DB; padding: 10pt 12pt; font-size: 12pt; }
            img { max-width: 100%; height: auto; margin: 12pt 0; }
        """
    elif quality == "最小体积":
        return """
            @page { size: A4; margin: 12mm 15mm; }
            body { font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", serif;
                   font-size: 9pt; line-height: 1.4; color: #1F2937; }
            h1 { font-size: 14pt; font-weight: 700; color: #111827; margin-top: 10pt; margin-bottom: 4pt; }
            h2 { font-size: 11pt; font-weight: 600; color: #1F2937; margin-top: 8pt; margin-bottom: 3pt; }
            h3 { font-size: 10pt; font-weight: 600; color: #374151; margin-top: 6pt; margin-bottom: 2pt; }
            p { margin: 1pt 0; text-indent: 0; }
            table { border-collapse: collapse; width: 100%; margin: 2pt 0; }
            th, td { border: 1px solid #D1D5DB; padding: 2pt 4pt; font-size: 8pt; }
            img { max-width: 70%; height: auto; margin: 2pt 0; }
        """
    else:  # 标准
        return """
            @page { size: A4; margin: 20mm 25mm; }
            body { font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", serif;
                   font-size: 11pt; line-height: 1.6; color: #1F2937; }
            h1 { font-size: 18pt; font-weight: 700; color: #111827; margin-top: 18pt; margin-bottom: 8pt; }
            h2 { font-size: 14pt; font-weight: 600; color: #1F2937; margin-top: 14pt; margin-bottom: 6pt; }
            h3 { font-size: 12pt; font-weight: 600; color: #374151; margin-top: 10pt; margin-bottom: 4pt; }
            p { margin: 3pt 0; text-indent: 0; }
            table { border-collapse: collapse; width: 100%; margin: 6pt 0; }
            th, td { border: 1px solid #D1D5DB; padding: 5pt 7pt; font-size: 9pt; }
            img { max-width: 100%; height: auto; margin: 6pt 0; }
        """
