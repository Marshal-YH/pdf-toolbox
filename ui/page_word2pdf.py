"""Word 转 PDF — 对标合并页面"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from ui.widgets import *
from utils.file_utils import make_task_dir, open_in_finder
from core.word_to_pdf import word_to_pdf
import os

class Word2PdfPage(QWidget):
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

        # 标题
        h = QHBoxLayout()
        h.addWidget(self._l("📝 Word 转 PDF", "22px", "700", "#1F2937"))
        tag = QLabel("高保真"); tag.setStyleSheet("font-size:12px;background:#ECFDF5;color:#10B981;padding:4px 12px;border-radius:10px;font-weight:600;border:none;"); h.addWidget(tag)
        h.addStretch()
        self.step_lbl = QLabel("步骤 1/2 · 添加文档  ♾️ 不限文档数 · 不限页数")
        self.step_lbl.setStyleSheet("font-size:13px;color:#9CA3AF;"); h.addWidget(self.step_lbl)
        lo.addLayout(h)

        # 批量条
        bar = QWidget(); bar.setStyleSheet("background:white;border:1px solid #E5E7EB;border-radius:10px;")
        bl = QHBoxLayout(bar); bl.setContentsMargins(20,12,20,12)
        bl.addWidget(QLabel("📦 批量模式")); bl.addWidget(QLabel("一次添加多个 Word 文件，批量转换为 PDF"))
        bl.addStretch()
        self.stats = QLabel("已选 0 个文档"); self.stats.setStyleSheet("font-size:13px;color:#6B7280;"); bl.addWidget(self.stats)
        lo.addWidget(bar)

        # 拖拽
        self.drop = DropZone("拖拽 Word 文档到此处", "支持 .docx · .doc · 可批量添加 · 不限数量")
        self.drop.files_dropped.connect(self.add_files)
        lo.addWidget(self.drop)

        bl2 = QHBoxLayout(); bl2.addStretch()
        btn = QPushButton("📁 选择文件"); btn.setStyleSheet(BTN_PRIMARY_STYLE); btn.setFixedWidth(160)
        btn.clicked.connect(self.select_files); bl2.addWidget(btn); bl2.addStretch()
        lo.addLayout(bl2)

        # 文件列表
        self.file_list = DraggableFileList()
        lo.addWidget(self.file_list, 1)

        # 底部 — 保存设置 + 操作（对标合并页面）
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
        self.out_name = QLineEdit("Word转PDF_输出.pdf"); self.out_name.setFixedWidth(160)
        self.out_name.setStyleSheet("border:1px solid #E5E7EB;border-radius:6px;padding:8px;font-size:13px;")
        abl.addWidget(self.out_name)

        reset_btn = QPushButton("重置"); reset_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        reset_btn.clicked.connect(self.reset_all); abl.addWidget(reset_btn)

        self.go = QPushButton("🔄 开始转换"); self.go.setStyleSheet(BTN_PRIMARY_STYLE)
        self.go.setEnabled(False); self.go.clicked.connect(self.start)
        abl.addWidget(self.go)
        lo.addWidget(ab)

    def _l(self, t, s, w, c):
        l = QLabel(t); l.setStyleSheet(f"font-size:{s};font-weight:{w};color:{c};border:none;"); return l

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择 Word 文件", "", "Word 文件 (*.docx *.doc)")
        if files: self.add_files(files)

    def add_files(self, files):
        existing = self.file_list.get_file_paths()
        for f in files:
            if os.path.splitext(f)[1].lower() in (".docx",".doc") and f not in existing:
                self.file_list.add_file_item(f, meta="Word 文档")
                existing.append(f)
        # 单文件时默认使用源文件名
        if len(existing) == 1:
            base = os.path.splitext(os.path.basename(existing[0]))[0]
            self.out_name.setText(f"{base}.pdf")
        self._upd()

    def _upd(self):
        n = self.file_list.count(); self.stats.setText(f"已选 {n} 个文档"); self.go.setEnabled(n > 0)

    def reset_all(self):
        self.file_list.clear_all(); self.out_name.setText("Word转PDF_输出.pdf"); self._upd()

    def start(self):
        paths = self.file_list.get_file_paths()
        if not paths: return

        # 使用自动生成的任务目录（对标合并页面）
        self._task_out_dir = make_task_dir("word")
        out_name = self.out_name.text().strip() or "Word转PDF_输出.pdf"
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"

        self.prog = QProgressDialog("正在转换 Word 文档...", "", 0, 0, self.window())
        self.prog.setWindowTitle(""); self.prog.setMinimumDuration(0)
        self.prog.setCancelButton(None)
        self.prog.setFixedWidth(360); self.prog.setFixedHeight(120)
        self.prog.setStyleSheet("""
            QProgressDialog { background: white; border-radius: 12px; }
            QLabel { font-size: 14px; color: #1F2937; padding: 8px; }
            QProgressBar { border: none; border-radius: 3px; background: #F3F4F6; height: 6px; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #365EFF, stop:1 #7C3AED);
                border-radius: 3px;
            }
        """)
        self.prog.show()

        class WordWorker(QThread):
            done = Signal(bool, str)  # success, msg
            def __init__(self, paths, out_dir, single_name):
                super().__init__()
                self.paths = paths; self.out_dir = out_dir; self.single_name = single_name

            def run(self):
                try:
                    rs = []
                    for i, p in enumerate(self.paths):
                        if len(self.paths) == 1:
                            out = os.path.join(self.out_dir, self.single_name)
                        else:
                            name = os.path.splitext(os.path.basename(p))[0]
                            out = os.path.join(self.out_dir, f"{name}.pdf")
                        word_to_pdf(p, out)
                        rs.append(out)
                    self.done.emit(True, str(len(rs)))
                except Exception as e:
                    import traceback; traceback.print_exc()
                    self.done.emit(False, str(e))

        self._worker = WordWorker(paths, self._task_out_dir, out_name)
        self._worker.done.connect(self._done)
        self._worker.start()

    def _done(self, ok, msg):
        if self.prog:
            self.prog.close()
        if ok:
            open_in_finder(self._task_out_dir)
            QMessageBox.information(self, "转换完成",
                f"✅ Word 转 PDF 完成！共转换 {msg} 个文件\n\n保存位置：{self._task_out_dir}")
        else:
            QMessageBox.warning(self, "转换失败", str(msg))
