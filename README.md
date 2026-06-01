# 📄 PDF 工具箱

> 免费、不限页数的 PDF 桌面工具箱 — 合并、拆分、Word 转 PDF

基于 PySide6 构建的跨平台桌面应用，提供 WPS 级别的 PDF 核心功能，**完全免费，不限页数，不限文件数量**。

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| **📄 PDF 合并** | 将多个 PDF 合并为一个。拖拽添加、自由排序、支持无限文件 |
| **✂️ 拆分文档** | 按页码范围 / 固定页数 / 提取指定页面 / 自动均分，四种拆分模式 |
| **📝 Word 转 PDF** | 高保真转换，保留表格、图片、排版，支持批量转换 |

### 更多特性

- **批量处理** — 一次添加多个文件，批量输出
- **拖拽交互** — 拖拽添加文件、列表内拖拽排序
- **自动命名** — 自动生成有序的输出文件名
- **任务目录** — 每次操作自动创建独立文件夹，按时间命名
- **自动弹出** — 完成后自动在 Finder 中打开输出目录
- **深色/浅色主题** — 跟随系统（WPS 风格配色）
- **零费用** — 所有功能免费，无水印，无页数限制

---

## 🖥 截图

| PDF 合并 | 拆分文档 | Word 转 PDF |
|---------|---------|------------|
| ![合并](screenshots/merge.png) | ![拆分](screenshots/split.png) | ![Word](screenshots/word.png) |

---

## 🔧 安装

### 系统要求

- Python 3.10+
- macOS / Windows / Linux
- macOS 需安装 **Homebrew**（用于 WeasyPrint 系统依赖）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/pdf-toolbox.git
cd pdf-toolbox
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. macOS 额外依赖（WeasyPrint）

```bash
brew install pango libffi
```

### 4. 运行

```bash
python3 main.py
```

> **macOS 快速启动**：双击 `启动PDF工具箱.command`（需先修改文件内的路径）

---

## 📂 项目结构

```
pdf-toolbox/
├── main.py                  # 程序入口
├── core/                    # 核心处理引擎
│   ├── pdf_merge.py         # PDF 合并逻辑
│   ├── pdf_split.py         # PDF 拆分 + 页码范围解析
│   ├── word_to_pdf.py       # Word → HTML → PDF 转换
│   └── html_renderer.py     # WeasyPrint 渲染封装
├── ui/                      # 界面层
│   ├── main_window.py       # 主窗口（侧边栏 + 页面切换）
│   ├── page_merge.py        # PDF 合并页面
│   ├── page_split.py        # 拆分文档页面
│   ├── page_word2pdf.py     # Word 转 PDF 页面
│   └── widgets.py           # 共享组件（拖拽区、文件列表、弹窗等）
├── utils/                   # 工具模块
│   ├── file_utils.py        # 文件操作（输出目录、Finder 打开等）
│   └── settings.py          # 设置持久化
├── requirements.txt         # Python 依赖
└── README.md
```

---

## 🏗 技术栈

| 技术 | 用途 |
|------|------|
| **PySide6** | 桌面 GUI 框架（Qt6） |
| **PyMuPDF (fitz)** | PDF 核心处理（合并、拆分、页面操作） |
| **WeasyPrint** | HTML→PDF 高保真渲染 |
| **python-docx** | Word 文档解析 |

### 架构设计

```
用户操作 → GUI (PySide6) → 核心引擎 (Python)
                ↕                    ↕
         文件拖拽/进度条        PyMuPDF/WeasyPrint
                ↕                    ↕
          输出目录 ←── 自动命名 ──→ PDF 文件
```

---

## 🚀 打包为独立 App

### macOS (.app)

```bash
pip install py2app
python3 setup.py py2app
```

### Windows (.exe)

```bash
pip install pyinstaller
pyinstaller --windowed --name "PDF工具箱" main.py
```

---

## 🧪 测试

```bash
python3 -m pytest tests/
```

或运行内置测试脚本：

```bash
python3 /path/to/test_all.py
```

---

## 📝 开发说明

- **配色方案**：主色 `#365EFF` → `#7C3AED`（渐变），绿色 `#10B981`，背景 `#F5F6F8`
- **编码规范**：遵循 PEP 8
- **中文字体**：macOS 内置 PingFang SC / Hiragino Sans GB
- **输出目录**：`~/Documents/PDF_输出/`

---

## 📄 许可

[MIT](LICENSE)

---

## 🙏 致谢

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) — 高性能 PDF 处理库
- [WeasyPrint](https://github.com/Kozea/WeasyPrint) — HTML/CSS 转 PDF 引擎
- [WPS PDF](https://www.wps.cn/) — 产品设计参考（功能流程、配色方案）

---

## 🚀 打包为独立 App（macOS）

```bash
pip install py2app
python3 setup.py py2app --dist-dir dist
```

构建完成后，`dist/PDF工具箱.app` 可直接拖到「应用程序」中使用。

> 首次打开如果提示「未识别的开发者」，前往 **系统设置 → 隐私与安全性**，点击「仍要打开」即可。
