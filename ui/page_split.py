"""PDF 拆分 — 下拉选项优化版"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.widgets import COLORS
from utils.file_utils import make_task_dir, open_in_finder
from core.pdf_split import parse_page_ranges, split_by_ranges
from core.pdf_merge import get_pdf_page_count
import fitz, os, re


# ============================================================
# 自定义 ComboBox 下拉选项代理 — 大间距 + 醒目选项
# ============================================================
class ModeItemDelegate(QStyledItemDelegate):
    """让下拉选项更高、更清晰"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_height = 52
    
    def sizeHint(self, option, index):
        return QSize(0, self._item_height)
    
    def paint(self, painter, option, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        
        # 背景
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, QColor("#EEF2FF"))
            # 左侧蓝色条
            bar = QRect(rect.x() + 2, rect.y() + 6, 3, rect.height() - 12)
            painter.fillRect(bar, QColor("#365EFF"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, QColor("#F3F4F6"))
        else:
            painter.fillRect(rect, QColor("#FFFFFF"))
        
        # 上下分割线
        painter.setPen(QPen(QColor("#F3F4F6"), 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
        # 解析文本: "🔢  按页码范围    —— 自定义每段范围"
        parts = text.split("——", 1)
        main_text = parts[0].strip() if parts else text
        desc_text = ("—— " + parts[1].strip()) if len(parts) > 1 else ""
        
        x = rect.x() + 16
        y = rect.y()
        
        # 主标题
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(False)
        painter.setFont(font1)
        painter.setPen(QColor("#1F2937"))
        painter.drawText(QRect(x, y + 6, rect.width() - 32, 24),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         main_text)
        
        # 描述文字
        if desc_text:
            font2 = QFont()
            font2.setPointSize(11)
            painter.setFont(font2)
            painter.setPen(QColor("#9CA3AF"))
            painter.drawText(QRect(x + 2, y + 26, rect.width() - 32, 20),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             desc_text)
        
        # 右侧 ✓ 选中标记
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setFont(font1)
            painter.setPen(QColor("#365EFF"))
            check_rect = QRect(rect.right() - 32, rect.y(), 24, rect.height())
            painter.drawText(check_rect, Qt.AlignmentFlag.AlignCenter, "✓")


# ============================================================
class SplitPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_path = ""
        self._selected_mode = 0
        self.setup_ui()

    def setup_ui(self):
        # ——— 滚动容器 ———
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        lo = QVBoxLayout(container)
        lo.setContentsMargins(48, 40, 48, 40)
        lo.setSpacing(28)

        # =========================================================
        # 标题区域
        # =========================================================
        header = QWidget()
        header.setStyleSheet("background: transparent; border: none;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)

        title_box = QWidget()
        title_box.setStyleSheet("background: transparent; border: none;")
        tl = QVBoxLayout(title_box)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        icon_lb = QLabel("✂️")
        icon_lb.setStyleSheet("font-size: 28px; border: none;")
        title_row.addWidget(icon_lb)
        title_lb = QLabel("拆分文档")
        title_lb.setStyleSheet("font-size: 24px; font-weight: 700; color: #1F2937; border: none;")
        title_row.addWidget(title_lb)

        badge = QLabel("♾️ 不限页数 · 不限份数 · 全部免费")
        badge.setStyleSheet("""
            font-size: 12px; color: #365EFF; font-weight: 500;
            background: #EEF2FF; border: 1px solid #D6E0FF;
            border-radius: 20px; padding: 4px 14px;
        """)
        badge.setFixedHeight(28)
        title_row.addSpacing(4)
        title_row.addWidget(badge)
        title_row.addStretch()
        tl.addLayout(title_row)

        sub_lb = QLabel("选择一个 PDF 文件，然后设置拆分方式，即可快速拆分成多个文档")
        sub_lb.setStyleSheet("font-size: 14px; color: #9CA3AF; border: none;")
        tl.addWidget(sub_lb)

        hl.addWidget(title_box)
        lo.addWidget(header)

        # =========================================================
        # 文件选择卡片
        # =========================================================
        file_card = QFrame()
        file_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 14px;
            }
        """)
        fl = QVBoxLayout(file_card)
        fl.setContentsMargins(24, 20, 24, 20)
        fl.setSpacing(8)

        fl.addWidget(self._label("选择 PDF 文件", "15px", "600", "#374151"))

        self.file_btn = QPushButton("📄  点击选择 PDF 文件")
        self.file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_btn.setFixedHeight(56)
        self.file_btn.setStyleSheet("""
            QPushButton {
                background: #FAFBFC;
                border: 2px dashed #D1D5DB;
                border-radius: 10px;
                padding: 0 24px;
                text-align: left;
                font-size: 15px;
                color: #6B7280;
            }
            QPushButton:hover {
                border-color: #365EFF;
                background: #EEF2FF;
                color: #365EFF;
            }
        """)
        self.file_btn.clicked.connect(self._pick)
        fl.addWidget(self.file_btn)

        lo.addWidget(file_card)

        # =========================================================
        # 拆分方式设置卡片
        # =========================================================
        mode_card = QFrame()
        mode_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 14px;
            }
        """)
        mcl = QVBoxLayout(mode_card)
        mcl.setContentsMargins(24, 24, 24, 24)
        mcl.setSpacing(20)

        # — 拆分方式标题 + 下拉 —
        mode_header = QHBoxLayout()
        mode_header.setSpacing(16)

        # 左侧："拆分方式" 标签
        label_widget = self._label("拆分方式", "15px", "600", "#374151")
        label_widget.setFixedWidth(80)
        mode_header.addWidget(label_widget)

        # ComboBox
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "🔢  按页码范围         —— 自定义每段页码范围",
            "📏  按固定页数         —— 每 N 页拆成一个文件",
            "🎯  提取指定页面       —— 提取特定页码",
            "📊  自动均分文件       —— 均分为 N 份",
        ])
        self.mode_combo.setMinimumWidth(420)
        self.mode_combo.setFixedHeight(44)
        self.mode_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 0 16px 0 18px;
                font-size: 15px;
                color: #1F2937;
                background: white;
            }
            QComboBox:hover { border-color: #365EFF; }
            QComboBox:focus { border-color: #365EFF; }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 36px;
                border: none;
            }
            QComboBox::down-arrow {
                width: 0; height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #6B7280;
                margin-right: 8px;
            }
        """)

        # 自定义代理 — 使下拉选项更高更醒目
        self.mode_combo.setItemDelegate(ModeItemDelegate(self.mode_combo))

        # 下拉弹出框整体样式
        view = self.mode_combo.view()
        view.setStyleSheet("""
            QListView {
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                padding: 4px 0;
                background: white;
                outline: none;
                font-size: 14px;
            }
        """)
        # 让下拉弹出框更宽，适应文字
        view.setMinimumWidth(460)

        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_header.addWidget(self.mode_combo)
        mode_header.addStretch()
        mcl.addLayout(mode_header)

        # — 分隔线 —
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #F3F4F6; border: none;")
        mcl.addWidget(sep)

        # — 输入区域 —
        input_area_widget = QWidget()
        input_area_widget.setStyleSheet("background: transparent; border: none;")
        ial = QVBoxLayout(input_area_widget)
        ial.setContentsMargins(0, 0, 0, 0)
        ial.setSpacing(10)

        # 标签
        self.input_label = QLabel("页码范围（用逗号分隔多个范围）")
        self.input_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151; border: none;")
        ial.addWidget(self.input_label)

        # 输入行（文本框 + 提示）
        input_row = QHBoxLayout()
        input_row.setSpacing(16)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("例：1-10, 11-20, 21-30（支持中英文逗号）")
        self.input_edit.setFixedHeight(44)
        self.input_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 15px;
                background: white;
            }
            QLineEdit:focus { border-color: #365EFF; }
        """)
        self.input_edit.textChanged.connect(self._validate_input)
        input_row.addWidget(self.input_edit, 1)

        self.input_spin = QSpinBox()
        self.input_spin.setRange(1, 10000)
        self.input_spin.setValue(10)
        self.input_spin.setSuffix(" 页一份")
        self.input_spin.setFixedHeight(44)
        self.input_spin.setMinimumWidth(200)
        self.input_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 15px;
                background: white;
            }
            QSpinBox:focus { border-color: #365EFF; }
        """)
        self.input_spin.hide()
        input_row.addWidget(self.input_spin)

        self.example_label = QLabel("示例：1-10, 11-20, 21-30")
        self.example_label.setStyleSheet("""
            font-size: 13px; color: #9CA3AF;
            padding: 8px 14px; border: none;
        """)
        input_row.addWidget(self.example_label)
        input_row.addStretch()

        ial.addLayout(input_row)

        # 错误提示
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("""
            font-size: 13px; color: #EF4444;
            padding: 6px 12px;
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 6px;
        """)
        self.error_label.setVisible(False)
        ial.addWidget(self.error_label)

        # 提示文字
        self.hint_label = QLabel("💡 请选择 PDF 文件后设置拆分规则")
        self.hint_label.setStyleSheet("""
            font-size: 13px; color: #6B7280;
            padding: 2px 0; border: none;
        """)
        ial.addWidget(self.hint_label)

        mcl.addWidget(input_area_widget)
        lo.addWidget(mode_card)

        # =========================================================
        # 输出设置卡片
        # =========================================================
        out_card = QFrame()
        out_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 14px;
            }
        """)
        ol = QVBoxLayout(out_card)
        ol.setContentsMargins(24, 24, 24, 24)
        ol.setSpacing(16)

        ol.addWidget(self._label("输出设置", "15px", "600", "#374151"))

        # 输出目录
        dir_row = QHBoxLayout()
        dir_row.setSpacing(12)
        lbl = self._label("输出文件夹", "14px", "500", "#4B5563")
        lbl.setFixedWidth(80)
        dir_row.addWidget(lbl)

        self.out_dir = QLineEdit(os.path.expanduser("~/Documents/PDF 拆分/"))
        self.out_dir.setFixedHeight(40)
        self.out_dir.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
                background: #FAFBFC;
                color: #374151;
            }
        """)
        dir_row.addWidget(self.out_dir, 1)

        browse_btn = QPushButton("📂 浏览")
        browse_btn.setFixedHeight(40)
        browse_btn.setFixedWidth(100)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet("""
            QPushButton {
                background: white; color: #6B7280;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #F9FAFB; border-color: #365EFF; color: #365EFF;
            }
        """)
        browse_btn.clicked.connect(
            lambda: self.out_dir.setText(
                QFileDialog.getExistingDirectory(self, "选择输出文件夹") or self.out_dir.text()
            )
        )
        dir_row.addWidget(browse_btn)
        ol.addLayout(dir_row)

        # 命名规则
        name_row = QHBoxLayout()
        name_row.setSpacing(12)
        lbl2 = self._label("命名规则", "14px", "500", "#4B5563")
        lbl2.setFixedWidth(80)
        name_row.addWidget(lbl2)

        self.name_tpl = QLineEdit("{name}_p{start}-{end}.pdf")
        self.name_tpl.setFixedHeight(40)
        self.name_tpl.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
                background: #FAFBFC;
                color: #374151;
                font-family: "Menlo", "SF Mono", monospace;
            }
        """)
        name_row.addWidget(self.name_tpl, 1)

        name_hint = QLabel("可用 {name} {start} {end} {index}")
        name_hint.setStyleSheet("font-size: 12px; color: #9CA3AF; border: none;")
        name_row.addWidget(name_hint)
        ol.addLayout(name_row)

        lo.addWidget(out_card)

        # ——— 弹性空间 ———
        lo.addStretch()

        # =========================================================
        # 底部操作栏
        # =========================================================
        bottom_bar = QWidget()
        bottom_bar.setStyleSheet("""
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
        """)
        bb = QHBoxLayout(bottom_bar)
        bb.setContentsMargins(24, 16, 24, 16)

        self.info_label = QLabel("📌 请先选择 PDF 文件")
        self.info_label.setStyleSheet("font-size: 14px; color: #6B7280; border: none;")
        bb.addWidget(self.info_label)
        bb.addStretch()

        self.go_btn = QPushButton("✂️  开始拆分")
        self.go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.go_btn.setFixedHeight(44)
        self.go_btn.setMinimumWidth(160)
        self.go_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #365EFF, stop:1 #7C3AED);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 0 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2952E8, stop:1 #6D28D9);
            }
        """)
        self.go_btn.clicked.connect(self._start)
        bb.addWidget(self.go_btn)
        lo.addWidget(bottom_bar)

        # 初始化
        self._on_mode_changed(0)

    # ========== 工具方法 ==========

    def _label(self, text, size="14px", weight="normal", color="#1F2937"):
        lb = QLabel(text)
        lb.setStyleSheet(f"font-size:{size}; font-weight:{weight}; color:{color}; border:none;")
        return lb

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 PDF", "", "PDF (*.pdf)")
        if path:
            self.input_path = path
            try:
                pages = get_pdf_page_count(path)
            except Exception:
                pages = 0
            self.file_btn.setText(f"📄  {os.path.basename(path)}  （共 {pages} 页）")
            self.file_btn.setStyleSheet("""
                QPushButton {
                    background: #EEF2FF;
                    border: 2px solid #365EFF;
                    border-radius: 10px;
                    padding: 0 24px;
                    text-align: left;
                    font-size: 15px;
                    color: #1F2937;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #DBE4FF;
                }
            """)
            self.info_label.setText(f"📄 {os.path.basename(path)}  ·  共 {pages} 页  ·  已就绪")
            self.hint_label.setText("💡 已选择文件，设置拆分方式后点击开始拆分")

    def _on_mode_changed(self, idx):
        self._selected_mode = idx
        self.input_edit.hide()
        self.input_spin.hide()
        self.error_label.setVisible(False)
        self.input_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 15px;
                background: white;
            }
            QLineEdit:focus { border-color: #365EFF; }
        """)

        if idx == 0:
            self.input_label.setText("页码范围（用逗号分隔多个范围）")
            self.input_edit.setPlaceholderText("例：1-10, 11-20, 21-30（支持中英文逗号）")
            self.input_edit.show()
            self.example_label.setText("示例：1-10, 11-20, 21-30（支持，、,）")
            self.hint_label.setText("💡 支持连续范围（1-10）和不连续页码（1,3,5），用逗号分隔")

        elif idx == 1:
            self.input_label.setText("每多少页拆成一个文件")
            self.input_spin.setSuffix(" 页一份")
            self.input_spin.show()
            self.example_label.setText(f"→ 每 {self.input_spin.value()} 页拆成一个文件")
            self.hint_label.setText(f"💡 当前 PDF 将按每 {self.input_spin.value()} 页拆分为多个文件")

        elif idx == 2:
            self.input_label.setText("要提取的页码（用逗号分隔）")
            self.input_edit.setPlaceholderText("例：1,3,5-8,12（支持中英文逗号）")
            self.input_edit.show()
            self.example_label.setText("示例：1,3,5-8,12（支持，、,）")
            self.hint_label.setText("💡 支持单页（1,3,5）和连续范围（5-8），用逗号分隔")

        elif idx == 3:
            self.input_label.setText("均分为多少份")
            self.input_spin.setSuffix(" 份")
            self.input_spin.show()
            self.example_label.setText(f"→ 均分为 {self.input_spin.value()} 份")
            self.hint_label.setText(f"💡 当前 PDF 将均分为 {self.input_spin.value()} 份，每份页数相近")

    def _validate_input(self, text):
        idx = self._selected_mode
        if idx in (1, 3):
            self.error_label.setVisible(False)
            return

        if not text.strip():
            self.error_label.setVisible(False)
            return

        valid = True
        error_msg = ""

        if idx == 0:
            # 支持中文逗号（，）和英文逗号（,）
            text = text.replace("，", ",")
            parts = [p.strip() for p in text.split(",") if p.strip()]
            for p in parts:
                if not p:
                    continue
                if "-" in p:
                    a, b = p.split("-", 1)
                    if not (a.strip().isdigit() and b.strip().isdigit()):
                        valid = False
                        error_msg = f'格式错误："{p}" 中的页码范围无效，正确格式如 "1-10"'
                        break
                    if int(a.strip()) > int(b.strip()):
                        valid = False
                        error_msg = f'格式错误："{p}" 起始页大于结束页'
                        break
                elif not p.strip().isdigit():
                    valid = False
                    error_msg = f'格式错误："{p}" 不是有效页码'
                    break
                elif int(p.strip()) < 1:
                    valid = False
                    error_msg = "页码不能小于 1"
                    break
        elif idx == 2:
            # 支持中文逗号（，）和英文逗号（,）
            text = text.replace("，", ",")
            parts = [p.strip() for p in text.split(",") if p.strip()]
            for p in parts:
                if not p:
                    continue
                if "-" in p:
                    a, b = p.split("-", 1)
                    if not (a.strip().isdigit() and b.strip().isdigit()):
                        valid = False
                        error_msg = f'格式错误："{p}" 中的页码范围无效'
                        break
                    if int(a.strip()) > int(b.strip()):
                        valid = False
                        error_msg = f'格式错误："{p}" 起始页大于结束页'
                        break
                elif not p.strip().isdigit():
                    valid = False
                    error_msg = f'格式错误："{p}" 不是有效页码'
                    break
                elif int(p.strip()) < 1:
                    valid = False
                    error_msg = "页码不能小于 1"
                    break

        if not valid:
            self.error_label.setText(f"⚠️  {error_msg}")
            self.error_label.setVisible(True)
            self.input_edit.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #EF4444;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 15px;
                    background: #FEF2F2;
                }
                QLineEdit:focus { border-color: #EF4444; }
            """)
        else:
            self.error_label.setVisible(False)
            self.input_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #10B981;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 15px;
                    background: white;
                }
                QLineEdit:focus { border-color: #365EFF; }
            """)

    def _start(self):
        if not self.input_path:
            QMessageBox.warning(self, "提示", "请先选择 PDF 文件")
            return

        idx = self._selected_mode

        if idx in (1, 3):
            param = self.input_spin.value()
            text = str(param)
        else:
            text = self.input_edit.text().strip()

        if not text:
            QMessageBox.warning(self, "提示", "请输入拆分规则")
            return

        if idx in (0, 2):
            self._validate_input(text)
            if self.error_label.isVisible():
                QMessageBox.warning(self, "输入错误", self.error_label.text().replace("⚠️  ", ""))
                return

        try:
            d = fitz.open(self.input_path)
            total = d.page_count
            d.close()
        except Exception:
            QMessageBox.warning(self, "错误", "无法读取 PDF 文件")
            return

        if idx == 1:
            input_str = f"每 {param} 页一份"
        elif idx == 3:
            input_str = f"拆成 {param} 份"
        else:
            input_str = text

        try:
            ranges = parse_page_ranges(input_str, total)
        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))
            return

        if not ranges:
            QMessageBox.warning(self, "输入错误",
                "无法识别拆分规则，请检查格式\n\n"
                "· 按页码范围：格式如 1-10, 11-20\n"
                "· 按固定页数：选择每 N 页一份\n"
                "· 提取页面：格式如 1,3,5-8,12\n"
                "· 自动均分：选择均分份数")
            return

        for s, e in ranges:
            if s > total or e > total:
                QMessageBox.warning(self, "输入错误",
                    f"页码范围 {s}-{e} 超出文档总页数（{total} 页）")
                return
            if s < 1 or e < 1:
                QMessageBox.warning(self, "输入错误", "页码不能小于 1")
                return

        out_dir = make_task_dir("split", os.path.basename(self.input_path))
        tmpl = self.name_tpl.text() or "{name}_p{start}-{end}.pdf"

        # 使用标准 QProgressDialog（更稳定）
        self.prog = QProgressDialog("正在拆分 PDF...", "", 0, 0, self.window())
        self.prog.setWindowTitle("")
        self.prog.setFixedWidth(360)
        self.prog.setFixedHeight(120)
        self.prog.setCancelButton(None)
        self.prog.setStyleSheet("""
            QProgressDialog {
                background: white; border-radius: 12px;
            }
            QLabel { font-size: 14px; color: #1F2937; padding: 8px; }
            QProgressBar {
                border: none; border-radius: 3px;
                background: #F3F4F6; height: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #365EFF, stop:1 #7C3AED);
                border-radius: 3px;
            }
        """)
        self.prog.show()

        # 在线程中执行拆分
        class SplitWorker(QThread):
            done = Signal(bool, str)
            def __init__(self, path, out, r, tpl):
                super().__init__()
                self.path = path; self.out = out; self.r = r; self.tpl = tpl
            def run(self):
                try:
                    split_by_ranges(self.path, self.out, self.r, self.tpl)
                    self.done.emit(True, self.out)
                except Exception as e:
                    self.done.emit(False, str(e))

        self._worker = SplitWorker(self.input_path, out_dir, ranges, tmpl)
        self._worker.done.connect(self._done)
        self._worker.start()

    def _done(self, ok, msg):
        if self.prog:
            self.prog.close()
        if ok:
            reply = QMessageBox.information(self, "拆分完成",
                f"✅ 文件已成功拆分！\n\n保存位置：{msg}",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open)
            if reply == QMessageBox.StandardButton.Open:
                import subprocess, platform
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", msg])
        else:
            QMessageBox.warning(self, "拆分失败", str(msg))
