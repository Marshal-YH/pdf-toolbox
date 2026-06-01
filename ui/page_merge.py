"""PDF 合并 — 稳定版"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from ui.widgets import *
from utils.file_utils import make_task_dir, open_in_finder
from core.pdf_merge import merge_pdfs, get_pdf_page_count
import os, traceback

class MergePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self.setup_ui()
    
    def setup_ui(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        ml = QVBoxLayout(self); ml.setContentsMargins(0,0,0,0); ml.addWidget(scroll)
        c = QWidget(); scroll.setWidget(c)
        
        lo = QVBoxLayout(c)
        lo.setContentsMargins(36, 28, 36, 28)
        lo.setSpacing(16)
        
        h = QHBoxLayout()
        t = QLabel("📄 PDF 合并"); t.setStyleSheet("font-size:22px;font-weight:700;color:#1F2937;"); h.addWidget(t)
        tag = QLabel("无限页数"); tag.setStyleSheet("font-size:12px;background:#ECFDF5;color:#10B981;padding:4px 12px;border-radius:10px;font-weight:600;border:none;"); h.addWidget(tag)
        h.addStretch()
        self.step_lbl = QLabel("步骤 1/2 · 添加文件  ♾️ 不限文件数量"); self.step_lbl.setStyleSheet("font-size:13px;color:#9CA3AF;"); h.addWidget(self.step_lbl)
        lo.addLayout(h)
        
        bar = QWidget(); bar.setStyleSheet("background:white;border:1px solid #E5E7EB;border-radius:10px;")
        bl = QHBoxLayout(bar); bl.setContentsMargins(20,12,20,12)
        bl.addWidget(QLabel("📦 批量模式")); bl.addWidget(QLabel("添加多个文件合并为一个 PDF，不限数量"))
        bl.addStretch()
        self.stats = QLabel("已选 0 个文件 · 共 0 页"); self.stats.setStyleSheet("font-size:13px;color:#6B7280;"); bl.addWidget(self.stats)
        lo.addWidget(bar)
        
        self.drop = DropZone("拖拽 PDF 文件到此处", "或点击下方按钮选择文件 · 不限文件数 · 不限总页数")
        self.drop.files_dropped.connect(self.add_files)
        lo.addWidget(self.drop)
        
        bl2 = QHBoxLayout(); bl2.addStretch()
        btn = QPushButton("📁 选择文件"); btn.setStyleSheet(BTN_PRIMARY_STYLE); btn.setFixedWidth(160)
        btn.clicked.connect(self.select_files); bl2.addWidget(btn); bl2.addStretch()
        lo.addLayout(bl2)
        
        self.file_list = DraggableFileList()
        self.file_list.order_changed.connect(self.update_stats)
        lo.addWidget(self.file_list, 1)
        
        ab = QWidget(); ab.setStyleSheet("border-top:1px solid #E5E7EB;")
        abl = QHBoxLayout(ab); abl.setContentsMargins(0,20,0,20)
        abl.addWidget(QLabel("保存到"))
        self.out_dir = QLineEdit(os.path.expanduser("~/Documents/PDF_输出/"))
        self.out_dir.setStyleSheet("border:1px solid #E5E7EB;border-radius:6px;padding:8px;font-size:13px;")
        abl.addWidget(self.out_dir, 1)
        
        btn_browse = QPushButton("📂 浏览")
        btn_browse.setStyleSheet("QPushButton{background:white;color:#6B7280;border:1px solid #E5E7EB;border-radius:6px;padding:8px 16px;font-size:13px;}QPushButton:hover{background:#F9FAFB;}")
        btn_browse.clicked.connect(lambda: self.out_dir.setText(
            QFileDialog.getExistingDirectory(self) or self.out_dir.text()))
        abl.addWidget(btn_browse)
        
        lbl_name = QLabel("文件名"); lbl_name.setFixedWidth(80); abl.addWidget(lbl_name)
        self.out_name = QLineEdit("合并文档.pdf"); self.out_name.setFixedWidth(160)
        self.out_name.setStyleSheet("border:1px solid #E5E7EB;border-radius:6px;padding:8px;font-size:13px;")
        abl.addWidget(self.out_name)
        
        reset_btn = QPushButton("重置"); reset_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        reset_btn.clicked.connect(self.reset_all); abl.addWidget(reset_btn)
        
        self.go_btn = QPushButton("🚀 开始合并"); self.go_btn.setStyleSheet(BTN_PRIMARY_STYLE)
        self.go_btn.setEnabled(False); self.go_btn.clicked.connect(self.start_merge)
        abl.addWidget(self.go_btn)
        lo.addWidget(ab)
    
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择 PDF", "", "PDF (*.pdf)")
        if files: self.add_files(files)
    
    def add_files(self, files):
        existing = self.file_list.get_file_paths()
        for f in files:
            if f.lower().endswith(".pdf") and f not in existing:
                try: pages = get_pdf_page_count(f)
                except: pages = 0
                self.file_list.add_file_item(f, page_count=pages)
                existing.append(f)
        self.update_stats()
    
    def update_stats(self):
        paths = self.file_list.get_file_paths()
        total = 0
        for p in paths:
            try: total += get_pdf_page_count(p)
            except: pass
        self.stats.setText(f"已选 {len(paths)} 个文件 · 共 {total} 页")
        self.go_btn.setEnabled(len(paths) >= 2)
    
    def reset_all(self):
        self.file_list.clear_all(); self.update_stats()
    
    def start_merge(self):
        paths = self.file_list.get_file_paths()
        if len(paths) < 2: return
        out_dir = make_task_dir("merge")
        out_path = os.path.join(out_dir, self.out_name.text() or "合并文档.pdf")
        
        # 用 QProgressDialog 替代自定义 ProgressDialog（更稳定）
        self.prog = QProgressDialog("正在合并 PDF...", "取消", 0, 100, self.window())
        self.prog.setWindowTitle(""); self.prog.setMinimumDuration(0)
        self.prog.setValue(0); self.prog.show()
        
        # 使用 QThread 的简单模式
        class MergeWorker(QThread):
            done = Signal(bool, str, str)  # success, msg, output_path
            
            def __init__(self, paths, output_path):
                super().__init__()
                self.paths = paths
                self.output_path = output_path
            
            def run(self):
                try:
                    pages = merge_pdfs(self.paths, self.output_path)
                    self.done.emit(True, str(pages), self.output_path)
                except Exception as e:
                    self.done.emit(False, str(e), self.output_path)
        
        self._worker = MergeWorker(paths, out_path)
        self._worker.done.connect(self._on_done)
        self._worker.start()
    
    def _on_done(self, ok, msg, path):
        if self.prog:
            self.prog.close()
        
        if ok:
            open_in_finder(path)
            QMessageBox.information(self, "合并完成",
                f"✅ PDF 合并成功！共 {msg} 页\n\n保存位置：{path}")
        else:
            QMessageBox.critical(self, "合并失败", f"处理出错：\n{msg}")
