"""共用 UI 组件 - v2 优化版"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import os

# ========== 设计系统 ==========
COLORS = {
    "primary": "#365EFF",
    "primary_hover": "#2952E8",
    "primary_light": "#EEF2FF",
    "green": "#10B981",
    "green_light": "#ECFDF5",
    "green_hover": "#059669",
    "bg": "#F5F6F8",
    "card": "#FFFFFF",
    "text": "#1F2937",
    "text_secondary": "#6B7280",
    "text_muted": "#9CA3AF",
    "border": "#E5E7EB",
    "border_light": "#F3F4F6",
    "danger": "#EF4444",
    "danger_light": "#FEF2F2",
}

FONT = "Helvetica Neue, PingFang SC, Microsoft YaHei, sans-serif"
RADIUS = 10
RADIUS_SM = 6
SHADOW = "0 1px 3px rgba(0,0,0,.04)"

# ========== 全局样式表 ==========
APP_STYLE = f"""
QWidget {{ font-family: "{FONT}"; }}
QMainWindow {{ background: {COLORS['bg']}; }}
QStackedWidget {{ background: {COLORS['bg']}; }}
"""

SIDEBAR_STYLE = """
QListWidget {
    background: white;
    border: none;
    border-right: 1px solid #E5E7EB;
    padding: 16px 8px;
    font-size: 14px;
    color: #6B7280;
    outline: none;
}
QListWidget::item {
    padding: 10px 14px;
    border-radius: 6px;
    margin: 1px 6px;
}
QListWidget::item:selected {
    background: #EEF2FF;
    color: #365EFF;
    font-weight: 600;
    border-left: 3px solid #365EFF;
}
QListWidget::item:hover:!selected {
    background: #F3F4F6;
    color: #365EFF;
}
"""

BTN_PRIMARY_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #365EFF, stop:1 #7C3AED);
    color: white; border: none; border-radius: 6px;
    padding: 10px 32px; font-size: 14px; font-weight: 600;
}
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #2952E8, stop:1 #6D28D9); }
QPushButton:disabled { background: #B0C4F8; }
"""

BTN_SECONDARY_STYLE = """
QPushButton {
    background: white; color: #6B7280;
    border: 1px solid #E5E7EB; border-radius: 6px;
    padding: 10px 32px; font-size: 14px;
}
QPushButton:hover { background: #F9FAFB; border-color: #D1D5DB; }
"""

BTN_GREEN_STYLE = """
QPushButton {
    background: #10B981; color: white;
    border: none; border-radius: 6px;
    padding: 10px 32px; font-size: 14px; font-weight: 600;
}
QPushButton:hover { background: #059669; }
"""

INPUT_STYLE = """
QLineEdit, QComboBox {
    border: 1px solid #E5E7EB; border-radius: 6px;
    padding: 8px 12px; font-size: 13px; background: white;
}
QLineEdit:focus, QComboBox:focus { border-color: #365EFF; }
"""

COMBO_STYLE = """
QComboBox {
    border: 1px solid #E5E7EB; border-radius: 6px;
    padding: 6px 12px; font-size: 13px; background: white;
}
"""


class ComboDelegate(QStyledItemDelegate):
    """下拉选项代理 - 52px 高，悬停/选中醒目"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_height = 52
    
    def sizeHint(self, option, index):
        return QSize(0, self._item_height)
    
    def paint(self, painter, option, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = option.rect
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, QColor("#EEF2FF"))
            bar = QRect(rect.x() + 2, rect.y() + 6, 3, rect.height() - 12)
            painter.fillRect(bar, QColor("#365EFF"))
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, QColor("#F3F4F6"))
        else:
            painter.fillRect(rect, QColor("#FFFFFF"))
        
        painter.setPen(QPen(QColor("#F3F4F6"), 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
        font = QFont()
        font.setPointSize(13)
        painter.setFont(font)
        painter.setPen(QColor("#1F2937"))
        painter.drawText(QRect(rect.x() + 16, rect.y(), rect.width() - 48, rect.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setPen(QColor("#365EFF"))
            painter.drawText(QRect(rect.right() - 36, rect.y(), 24, rect.height()),
                             Qt.AlignmentFlag.AlignCenter, chr(10003))


def create_styled_combo(items, min_width=240, height=42):
    """创建统一风格的 QComboBox，带自定义代理和现代样式"""
    cb = QComboBox()
    cb.addItems(items)
    cb.setMinimumWidth(min_width)
    cb.setFixedHeight(height)
    cb.setStyleSheet("""
        QComboBox {
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 0 14px 0 16px;
            font-size: 14px;
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
    cb.setItemDelegate(ComboDelegate(cb))
    view = cb.view()
    view.setStyleSheet("""
        QListView {
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 4px 0;
            background: white;
            outline: none;
        }
    """)
    view.setMinimumWidth(min_width + 40)
    return cb



PROGRESS_STYLE = """
QProgressBar {
    border: none; border-radius: 3px;
    background: #F3F4F6; height: 6px; text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #365EFF, stop:1 #7C3AED);
    border-radius: 3px;
}
"""

CARD_STYLE = f"""
    background: white;
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
"""


# ========== 拖拽放置区 ==========
class DropZone(QFrame):
    files_dropped = Signal(list)
    
    def __init__(self, text="", sub_text="", hint="", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(150)
        self._set_style_default()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        
        icon = QLabel("📥"); icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 34px; background: transparent; border: none;")
        layout.addWidget(icon)
        
        if text:
            t = QLabel(text); t.setAlignment(Qt.AlignCenter)
            t.setStyleSheet("font-size: 15px; color: #6B7280; background: transparent; border: none;")
            layout.addWidget(t)
        
        if sub_text:
            s = QLabel(sub_text); s.setAlignment(Qt.AlignCenter)
            s.setStyleSheet("font-size: 12px; color: #9CA3AF; background: transparent; border: none;")
            layout.addWidget(s)
        
        if hint:
            h = QLabel(hint); h.setAlignment(Qt.AlignCenter)
            h.setStyleSheet("font-size: 11px; color: #BBB; background: transparent; border: none;")
            layout.addWidget(h)
    
    def _set_style_default(self):
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #D1D5DB;
                border-radius: 14px;
                background: #FAFBFC;
            }
            QFrame:hover {
                border-color: #365EFF;
                background: #EEF2FF;
            }
        """)
    
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #365EFF;
                    border-radius: 14px;
                    background: #EEF2FF;
                }
            """)
    
    def dragLeaveEvent(self, e):
        self._set_style_default()
    
    def dropEvent(self, e):
        self._set_style_default()
        files = []
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p):
                files.append(p)
        if files:
            self.files_dropped.emit(files)


# ========== 可拖拽文件列表 ==========
class DraggableFileList(QListWidget):
    order_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSpacing(4)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            QListWidget {
                border: none; background: transparent; outline: none;
            }
            QListWidget::item {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                margin: 2px 0;
            }
            QListWidget::item:hover { border-color: #365EFF; }
            QListWidget::item:selected {
                border-color: #365EFF;
                background: #FAFBFC;
            }
        """)
    
    def add_file_item(self, path, page_count=None, order=None, meta=""):
        widget = FileItemWidget(path, page_count, order, meta)
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(0, 66))
        self.addItem(item)
        self.setItemWidget(item, widget)
        widget.remove_clicked.connect(lambda p: self._remove(item, p))
    
    def _remove(self, item, path):
        self.takeItem(self.row(item))
        self._update_orders()
    
    def get_file_paths(self):
        paths = []
        for i in range(self.count()):
            w = self.itemWidget(self.item(i))
            if w: paths.append(w.file_path)
        return paths
    
    def clear_all(self):
        while self.count(): self.takeItem(0)
    
    def _update_orders(self):
        for i in range(self.count()):
            w = self.itemWidget(self.item(i))
            if w and hasattr(w, 'update_order'):
                w.update_order(i + 1)
        self.order_changed.emit()
    
    def dropEvent(self, e):
        super().dropEvent(e)
        self._update_orders()


# ========== 文件卡片 ==========
class FileItemWidget(QFrame):
    remove_clicked = Signal(str)
    
    def __init__(self, path, page_count=None, order=None, meta="", parent=None):
        super().__init__(parent)
        self.file_path = path
        self.setFixedHeight(66)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)
        
        # 拖拽手柄
        h = QLabel("⠿"); h.setFixedWidth(16)
        h.setStyleSheet("color: #D1D5DB; font-size: 18px; border: none;")
        layout.addWidget(h)
        
        # 缩略图
        ext = os.path.splitext(path)[1].lower()
        icon_map = {".pdf": "📕", ".docx": "📘", ".doc": "📘", ".xlsx": "📊", ".xls": "📊"}
        thumb = QLabel(icon_map.get(ext, "📄"))
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setFixedSize(34, 44)
        thumb.setStyleSheet("background: #F3F4F6; border: 1px solid #E5E7EB; border-radius: 4px; font-size: 16px;")
        layout.addWidget(thumb)
        
        # 信息
        info = QVBoxLayout(); info.setSpacing(1)
        name = QLabel(os.path.basename(path))
        name.setStyleSheet("font-size: 13px; font-weight: 500; color: #1F2937; border: none;")
        info.addWidget(name)
        
        parts = []
        if page_count: parts.append(f"{page_count} 页")
        if meta: parts.append(meta)
        parts.append(self._fmt_size(os.path.getsize(path)))
        meta_lbl = QLabel(" · ".join(parts))
        meta_lbl.setStyleSheet("font-size: 11px; color: #9CA3AF; border: none;")
        info.addWidget(meta_lbl)
        layout.addLayout(info, 1)
        
        # 序号
        self.order_lbl = None
        if order:
            self.order_lbl = QLabel(f"#{order}")
            self.order_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #365EFF; background: #EEF2FF; padding: 2px 10px; border-radius: 8px; border: none;")
            layout.addWidget(self.order_lbl)
        
        # 删除
        rm = QPushButton("✕")
        rm.setFixedSize(24, 24)
        rm.setStyleSheet("""
            QPushButton { background: transparent; color: #D1D5DB;
                border: none; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background: #FEF2F2; color: #EF4444; }
        """)
        rm.clicked.connect(lambda: self.remove_clicked.emit(path))
        layout.addWidget(rm)
    
    def update_order(self, n):
        if self.order_lbl:
            self.order_lbl.setText(f"#{n}")
    
    @staticmethod
    def _fmt_size(s):
        if s < 1024: return f"{s} B"
        if s < 1024*1024: return f"{s/1024:.1f} KB"
        return f"{s/1024/1024:.1f} MB"


# ========== 进度弹窗 ==========
class ProgressDialog(QDialog):
    cancelled = Signal()
    
    def __init__(self, title="处理中...", max_value=100, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(400, 220)
        self.setStyleSheet("QDialog { background: white; border-radius: 16px; }")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        lo = QVBoxLayout(self)
        lo.setContentsMargins(32, 32, 32, 28)
        lo.setAlignment(Qt.AlignCenter)
        
        self.icon = QLabel("⏳"); self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("font-size: 36px; border: none;")
        lo.addWidget(self.icon)
        
        self.title = QLabel(title); self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 17px; font-weight: 600; color: #1F2937; border: none;")
        lo.addWidget(self.title)
        
        self.desc = QLabel(""); self.desc.setAlignment(Qt.AlignCenter)
        self.desc.setStyleSheet("font-size: 13px; color: #9CA3AF; border: none;")
        lo.addWidget(self.desc)
        
        self.pbar = QProgressBar()
        self.pbar.setRange(0, max_value); self.pbar.setValue(0)
        self.pbar.setFixedHeight(6)
        self.pbar.setStyleSheet(PROGRESS_STYLE)
        lo.addWidget(self.pbar)
        
        self.pct = QLabel("0%"); self.pct.setAlignment(Qt.AlignCenter)
        self.pct.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: 600; border: none;")
        lo.addWidget(self.pct)
        
        btn = QPushButton("取消")
        btn.setStyleSheet(BTN_SECONDARY_STYLE)
        btn.setFixedWidth(100)
        btn.clicked.connect(self._cancel)
        bl = QHBoxLayout(); bl.setAlignment(Qt.AlignCenter); bl.addWidget(btn)
        lo.addLayout(bl)
    
    def update(self, value, desc=""):
        self.pbar.setValue(value)
        mx = self.pbar.maximum()
        pct = int(value / mx * 100) if mx else 0
        self.pct.setText(f"{pct}%")
        if desc: self.desc.setText(desc)
        if pct >= 100:
            self.icon.setText("✅")
            self.title.setText("完成！")
    
    def _cancel(self):
        self.cancelled.emit()
        self.reject()


# ========== Toast 通知 ==========
class ToastNotification(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setStyleSheet("QFrame { background: white; border: 1px solid #E5E7EB; border-radius: 12px; }")
        
        lo = QHBoxLayout(self)
        lo.setContentsMargins(18, 12, 18, 12); lo.setSpacing(10)
        
        self.icon = QLabel("✅"); self.icon.setStyleSheet("font-size: 18px; border: none;"); lo.addWidget(self.icon)
        self.msg = QLabel(""); self.msg.setStyleSheet("font-size: 14px; color: #1F2937; border: none;"); lo.addWidget(self.msg)
        self.btn_open = QPushButton("📂 打开")
        self.btn_open.setStyleSheet("QPushButton { background: #EEF2FF; color: #365EFF; border: none; border-radius: 6px; padding: 6px 16px; font-size: 13px; font-weight: 500; } QPushButton:hover { background: #DBE4FF; }")
        lo.addWidget(self.btn_open)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setStyleSheet("QPushButton { background: transparent; color: #9CA3AF; border: none; border-radius: 11px; font-size: 12px; } QPushButton:hover { background: #F3F4F6; }")
        lo.addWidget(self.btn_close)
        
        self._timer = QTimer(self); self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
    
    def show_message(self, msg, auto_close=5000):
        self.msg.setText(msg); self.adjustSize(); self.show(); self.raise_()
        if self.parent():
            pr = self.parent().rect()
            self.move(pr.width() - self.width() - 32, pr.height() - self.height() - 32)
        if auto_close > 0: self._timer.start(auto_close)


# ========== 工作线程 ==========
class WorkerThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)
    
    def __init__(self, work_fn, *args, **kwargs):
        super().__init__()
        self.work_fn = work_fn
        self.args = args
        self.kwargs = kwargs
        self._cancelled = False
        self._prog_cb = None
    
    def set_progress_callback(self, cb):
        self._prog_cb = cb
    
    def run(self):
        try:
            if self._prog_cb:
                r = self.work_fn(*self.args, progress_callback=self._prog_cb, **self.kwargs)
            else:
                r = self.work_fn(*self.args, **self.kwargs)
            if not self._cancelled:
                self.finished.emit(True, str(r))
        except Exception as e:
            if not self._cancelled:
                self.finished.emit(False, str(e))
    
    def cancel(self):
        self._cancelled = True
