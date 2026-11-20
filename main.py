import sys
import json
import os
import threading
import time
import winsound
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import qtawesome as qta

try:
    import gkeepapi
    HAS_GKEEP = True
except ImportError:
    HAS_GKEEP = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QFrame, QMessageBox, QInputDialog, QFileDialog,
    QCheckBox, QFontComboBox, QColorDialog, QDialog, QFormLayout, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QTextListFormat

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"


def generate_app_icon():
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (17, 24, 39, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([18, 18, 238, 238], radius=56, fill=(79, 70, 229, 255))
        draw.rounded_rectangle([64, 72, 192, 90], radius=9, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([64, 119, 192, 137], radius=9, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([64, 166, 148, 184], radius=9, fill=(199, 210, 254, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])


PAGE_THEMES = {
    "داكن أنيق": {"bg": "#141A29", "fg": "#F1F5F9", "border": "#263148"},
    "أزرق منتصف الليل": {"bg": "#0D1B2A", "fg": "#E0E1DD", "border": "#1B263B"},
    "زمردي هادئ": {"bg": "#0B2520", "fg": "#E6F4F1", "border": "#19433B"},
    "ورقة دافئة (Cream)": {"bg": "#FBF7E9", "fg": "#1E293B", "border": "#E6DEC3"},
    "أبيض ناصع": {"bg": "#FFFFFF", "fg": "#0F172A", "border": "#E2E8F0"}
}

MODERN_STYLESHEET = """
QMainWindow {
    background-color: #0B0F1A;
}
QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Tahoma', Arial;
    font-size: 13.5px;
}
#Sidebar {
    background-color: #101624;
    border-left: 1px solid #1E293B;
}
#BrandTitle {
    font-size: 19px;
    font-weight: 700;
    color: #F8FAFC;
}
#BrandSub {
    font-size: 11.5px;
    color: #818CF8;
}
#PrimaryBtn {
    background-color: #4F46E5;
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13.5px;
}
#PrimaryBtn:hover {
    background-color: #4338CA;
}
#SyncBtn {
    background-color: #162033;
    color: #E2E8F0;
    border: 1px solid #2A3A55;
    border-radius: 10px;
    padding: 9px 12px;
    font-weight: 600;
}
#SyncBtn:hover {
    background-color: #1E2D47;
    border-color: #6366F1;
}
.NavItem {
    background-color: transparent;
    text-align: right;
    padding: 9px 12px;
    border-radius: 9px;
    color: #94A3B8;
    font-weight: 600;
    border: none;
}
.NavItem:hover {
    background-color: #172033;
    color: #F8FAFC;
}
.NavItem[active="true"] {
    background-color: rgba(79, 70, 229, 0.18);
    color: #A5B4FC;
    border-right: 3px solid #6366F1;
}
#NotesListPanel {
    background-color: #0E1422;
    border-left: 1px solid #1E293B;
}
QLineEdit {
    background-color: #151E30;
    border: 1px solid #26334D;
    border-radius: 9px;
    padding: 8px 12px;
    color: #F8FAFC;
    selection-background-color: #4F46E5;
}
QLineEdit:focus {
    border-color: #6366F1;
}
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    background-color: #141C2E;
    border: 1px solid #1E293B;
    border-radius: 11px;
    padding: 11px 12px;
    margin-bottom: 8px;
}
QListWidget::item:hover {
    background-color: #19243B;
    border-color: #334155;
}
QListWidget::item:selected {
    background-color: rgba(79, 70, 229, 0.16);
    border-color: #6366F1;
}
#EditorContainer {
    background-color: #0B0F1A;
}
#NoteTitleEdit {
    background-color: transparent;
    border: none;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    padding: 4px 6px;
}
#NoteTitleEdit:focus {
    background-color: #121929;
    border-radius: 8px;
}
#ToolbarCard {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
}
.IconActionBtn {
    background-color: #172033;
    border: 1px solid #26334D;
    border-radius: 8px;
    padding: 6px 9px;
    color: #CBD5E1;
    font-weight: 600;
}
.IconActionBtn:hover {
    background-color: #22304C;
    color: #FFFFFF;
    border-color: #475569;
}
.QuickTimeBtn {
    background-color: #182236;
    border: 1px solid #2A3A55;
    border-radius: 7px;
    padding: 4px 8px;
    color: #93C5FD;
    font-size: 11.5px;
    font-weight: 600;
}
.QuickTimeBtn:hover {
    background-color: #23324E;
}
QComboBox, QFontComboBox {
    background-color: #172033;
    border: 1px solid #26334D;
    border-radius: 8px;
    padding: 5px 8px;
    color: #F1F5F9;
}
QComboBox:hover, QFontComboBox:hover {
    border-color: #6366F1;
}
QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {
    background-color: #131B2C;
    color: #F1F5F9;
    selection-background-color: #4F46E5;
    border: 1px solid #26334D;
}
#TasksPanel {
    background-color: #101624;
    border-right: 1px solid #1E293B;
}
QProgressBar {
    background-color: #1A2438;
    border: none;
    border-radius: 5px;
    height: 7px;
}
QProgressBar::chunk {
    background-color: #10B981;
    border-radius: 5px;
}
.TaskRowCard {
    background-color: #151E30;
    border: 1px solid #23304A;
    border-radius: 10px;
}
.TaskRowCard:hover {
    border-color: #334155;
}
QStatusBar {
    background-color: #0E1422;
    color: #94A3B8;
    border-top: 1px solid #1E293B;
    font-size: 12px;
}
"""


class WorkerSignaler(QObject):
    alarm_triggered = pyqtSignal(str, str)
    sync_finished = pyqtSignal(bool, str)


class KeepSettingsDialog(QDialog):
    def __init__(self, keep_cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات مزامنة Google Keep")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(440, 230)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(
            "أدخل بريد Gmail و Master Token الخاص بحساب Google Keep.\n"
            "المزامنة تعمل في الخلفية دون تعطيل عمل التطبيق محلياً."
        )
        info.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(info)

        form = QFormLayout()
        self.email_edit = QLineEdit(keep_cfg.get("email", ""))
        self.email_edit.setPlaceholderText("example@gmail.com")

        self.token_edit = QLineEdit(keep_cfg.get("master_token", ""))
        self.token_edit.setPlaceholderText("aas_et/...")
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.auto_sync_cb = QCheckBox("مزامنة تلقائية كل 5 دقائق")
        self.auto_sync_cb.setChecked(keep_cfg.get("auto_sync", False))

        form.addRow("البريد الإلكتروني:", self.email_edit)
        form.addRow("Master Token:", self.token_edit)
        form.addRow("", self.auto_sync_cb)
        layout.addLayout(form)

        btns = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setProperty("class", "IconActionBtn")
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_values(self):
        return {
            "email": self.email_edit.text().strip(),
            "master_token": self.token_edit.text().strip(),
            "auto_sync": self.auto_sync_cb.isChecked()
        }


class FloatingNoteWindow(QWidget):
    def __init__(self, note, parent_app):
        super().__init__()
        self.note = note
        self.parent_app = parent_app
        self.setWindowTitle(f"{note.get('title', 'ملاحظة عائمة')} - Notes Hamza")
        self.resize(480, 440)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        lbl = QLabel(note.get("title", "بدون عنوان"))
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #818CF8;")
        layout.addWidget(lbl)

        self.editor = QTextEdit()
        theme = PAGE_THEMES.get(note.get("theme", "داكن أنيق"), PAGE_THEMES["داكن أنيق"])
        self.editor.setStyleSheet(
            f"background-color: {theme['bg']}; color: {theme['fg']}; "
            f"border: 1px solid {theme['border']}; border-radius: 10px; padding: 12px; font-size: 14px;"
        )
        if note.get("html"):
            self.editor.setHtml(note["html"])
        else:
            self.editor.setPlainText(note.get("content", ""))

        self.editor.textChanged.connect(self.sync_back)
        layout.addWidget(self.editor)

    def sync_back(self):
        self.note["content"] = self.editor.toPlainText()
        self.note["html"] = self.editor.toHtml()
        self.note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.parent_app.save_data()
        if self.parent_app.current_note_id == self.note["id"]:
            self.parent_app.editor.blockSignals(True)
            self.parent_app.editor.setHtml(self.note["html"])
            self.parent_app.editor.blockSignals(False)
            self.parent_app.update_stats()


class NotesHamzaStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        generate_app_icon()
        self.setWindowTitle("Notes Hamza Studio")
        self.resize(1420, 860)
        if os.path.exists(ICON_FILE):
            self.setWindowIcon(QIcon(ICON_FILE))

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.data = self.load_data()
        self.current_note_id = None
        self.current_category = "All"
        self.unlocked_notes = set()
        self.nav_buttons = {}
        self.floating_windows = []
        self.is_syncing = False

        self.signaler = WorkerSignaler()
        self.signaler.alarm_triggered.connect(self.show_alarm_popup)
        self.signaler.sync_finished.connect(self.on_sync_finished)

        self.build_ui()
        self.refresh_notes_list()

        threading.Thread(target=self.reminder_worker, daemon=True).start()
        threading.Thread(target=self.auto_keep_worker, daemon=True).start()

    def set_status(self, msg, timeout=4000):
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(msg, timeout)

    def load_data(self):
        default_data = {
            "keep": {
                "email": "",
                "master_token": "",
                "auto_sync": False,
                "last_sync": "لم تتم المزامنة بعد"
            },
            "notes": [
                {
                    "id": "1",
                    "keep_id": "",
                    "title": "أهلاً بك في Notes Hamza Studio",
                    "category": "Projects",
                    "content": "واجهة أنيقة ومرتبة لإدارة الملاحظات والمهام مع دعم مزامنة Google Keep.",
                    "html": "",
                    "theme": "داكن أنيق",
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": "إعداد بيانات Google Keep", "done": False, "priority": "High", "reminder": "", "alerted": False}
                    ]
                }
            ]
        }
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and "notes" in loaded:
                        loaded.setdefault("keep", default_data["keep"])
                        return loaded
            except Exception:
                pass
        return default_data

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1) القائمة الجانبية
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(14, 18, 14, 18)
        side_lay.setSpacing(6)

        brand_box = QVBoxLayout()
        brand_box.setContentsMargins(6, 0, 6, 10)
        title_lbl = QLabel("Notes Hamza")
        title_lbl.setObjectName("BrandTitle")
        sub_lbl = QLabel("Workspace & Keep Sync")
        sub_lbl.setObjectName("BrandSub")
        brand_box.addWidget(title_lbl)
        brand_box.addWidget(sub_lbl)
        side_lay.addLayout(brand_box)

        new_note_btn = QPushButton(" ملاحظة جديدة")
        new_note_btn.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        new_note_btn.setIconSize(QSize(15, 15))
        new_note_btn.setObjectName("PrimaryBtn")
        new_note_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_note_btn.clicked.connect(self.create_note)
        side_lay.addWidget(new_note_btn)
        side_lay.addSpacing(10)

        sections = [
            ("الكل", "All", "fa5s.layer-group", "#818CF8"),
            ("المثبتة", "Pinned", "fa5s.thumbtack", "#F59E0B"),
            ("السرية", "Locked", "fa5s.lock", "#EF4444"),
            ("المشاريع", "Projects", "fa5s.rocket", "#38BDF8"),
            ("شخصي", "Personal", "fa5s.user", "#34D399"),
            ("العمل", "Work", "fa5s.briefcase", "#FBBF24"),
            ("أفكار", "Ideas", "fa5s.lightbulb", "#C084FC")
        ]
        for label, key, ic, col in sections:
            btn = QPushButton(f"  {label}")
            btn.setIcon(qta.icon(ic, color=col))
            btn.setIconSize(QSize(15, 15))
            btn.setProperty("class", "NavItem")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.set_category(k))
            side_lay.addWidget(btn)
            self.nav_buttons[key] = btn

        side_lay.addStretch()

        self.sync_btn = QPushButton(" مزامنة Google Keep")
        self.sync_btn.setIcon(qta.icon("fa5s.sync", color="#38BDF8"))
        self.sync_btn.setObjectName("SyncBtn")
        self.sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_btn.clicked.connect(self.start_keep_sync)
        side_lay.addWidget(self.sync_btn)

        cfg_btn = QPushButton(" إعدادات Keep")
        cfg_btn.setIcon(qta.icon("fa5s.cog", color="#94A3B8"))
        cfg_btn.setProperty("class", "NavItem")
        cfg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_btn.clicked.connect(self.open_keep_settings)
        side_lay.addWidget(cfg_btn)

        export_btn = QPushButton(" تصدير الملاحظة")
        export_btn.setIcon(qta.icon("fa5s.file-export", color="#94A3B8"))
        export_btn.setProperty("class", "NavItem")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self.export_note)
        side_lay.addWidget(export_btn)

        self.sync_status_lbl = QLabel(f"Keep: {self.data['keep'].get('last_sync', 'غير متصل')}")
        self.sync_status_lbl.setStyleSheet("color: #64748B; font-size: 11px; padding: 4px 6px 0 6px;")
        side_lay.addWidget(self.sync_status_lbl)

        # 2) قائمة الملاحظات (كروت مختصرة)
        notes_panel = QFrame()
        notes_panel.setObjectName("NotesListPanel")
        notes_panel.setFixedWidth(295)
        notes_lay = QVBoxLayout(notes_panel)
        notes_lay.setContentsMargins(14, 18, 14, 14)
        notes_lay.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("بحث سريع في الملاحظات...")
        self.search_box.textChanged.connect(self.refresh_notes_list)
        notes_lay.addWidget(self.search_box)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_clicked)
        notes_lay.addWidget(self.notes_list)

        # 3) منطقة المحرر
        editor_panel = QFrame()
        editor_panel.setObjectName("EditorContainer")
        editor_lay = QVBoxLayout(editor_panel)
        editor_lay.setContentsMargins(20, 16, 20, 14)
        editor_lay.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("NoteTitleEdit")
        self.title_edit.setPlaceholderText("عنوان الملاحظة...")
        self.title_edit.textEdited.connect(self.auto_save)
        top_bar.addWidget(self.title_edit, 1)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["Projects", "Personal", "Work", "Ideas"])
        self.cat_combo.setFixedWidth(115)
        self.cat_combo.currentTextChanged.connect(self.change_category)
        top_bar.addWidget(self.cat_combo)

        float_btn = QPushButton(" عائم")
        float_btn.setIcon(qta.icon("fa5s.external-link-alt", color="#38BDF8"))
        float_btn.setProperty("class", "IconActionBtn")
        float_btn.setToolTip("فتح في نافذة عائمة")
        float_btn.clicked.connect(self.open_floating_window)
        top_bar.addWidget(float_btn)

        self.lock_btn = QPushButton(" قفل")
        self.lock_btn.setIcon(qta.icon("fa5s.unlock", color="#CBD5E1"))
        self.lock_btn.setProperty("class", "IconActionBtn")
        self.lock_btn.clicked.connect(self.toggle_lock)
        top_bar.addWidget(self.lock_btn)

        self.pin_btn = QPushButton(" تثبيت")
        self.pin_btn.setIcon(qta.icon("fa5s.thumbtack", color="#CBD5E1"))
        self.pin_btn.setProperty("class", "IconActionBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        top_bar.addWidget(self.pin_btn)

        del_note_btn = QPushButton()
        del_note_btn.setIcon(qta.icon("fa5s.trash-alt", color="#F87171"))
        del_note_btn.setProperty("class", "IconActionBtn")
        del_note_btn.setToolTip("حذف الملاحظة")
        del_note_btn.clicked.connect(self.delete_note)
        top_bar.addWidget(del_note_btn)

        editor_lay.addLayout(top_bar)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("ToolbarCard")
        tb_lay = QHBoxLayout(toolbar_card)
        tb_lay.setContentsMargins(10, 7, 10, 7)
        tb_lay.setSpacing(6)

        self.font_family = QFontComboBox()
        self.font_family.setFixedWidth(135)
        self.font_family.currentFontChanged.connect(self.change_font_family)
        tb_lay.addWidget(self.font_family)

        self.font_size = QComboBox()
        self.font_size.addItems(["12", "14", "16", "18", "22", "28"])
        self.font_size.setCurrentText("14")
        self.font_size.setFixedWidth(62)
        self.font_size.currentTextChanged.connect(self.change_font_size)
        tb_lay.addWidget(self.font_size)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(PAGE_THEMES.keys()))
        self.theme_combo.setFixedWidth(135)
        self.theme_combo.currentTextChanged.connect(self.change_page_theme)
        tb_lay.addWidget(self.theme_combo)

        fmt_actions = [
            ("fa5s.bold", "عريض", self.format_bold),
            ("fa5s.italic", "مائل", self.format_italic),
            ("fa5s.underline", "تسطير", self.format_underline),
            ("fa5s.palette", "لون النص", self.pick_text_color),
            ("fa5s.highlighter", "تظليل", self.pick_highlight_color),
            ("fa5s.list-ul", "قائمة", self.insert_bullet_list),
            ("fa5s.align-right", "يمين", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight)),
            ("fa5s.align-left", "يسار", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        ]
        for ic, tip, fn in fmt_actions:
            b = QPushButton()
            b.setIcon(qta.icon(ic, color="#E2E8F0"))
            b.setToolTip(tip)
            b.setProperty("class", "IconActionBtn")
            b.clicked.connect(fn)
            tb_lay.addWidget(b)

        tb_lay.addStretch()
        editor_lay.addWidget(toolbar_card)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("اكتب ملاحظتك هنا...")
        self.editor.textChanged.connect(self.auto_save)
        editor_lay.addWidget(self.editor, 1)

        self.stats_lbl = QLabel("الكلمات: 0  |  الأحرف: 0")
        self.stats_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        editor_lay.addWidget(self.stats_lbl)

        # 4) لوحة المهام والتنبيهات
        tasks_panel = QFrame()
        tasks_panel.setObjectName("TasksPanel")
        tasks_panel.setFixedWidth(325)
        tasks_lay = QVBoxLayout(tasks_panel)
        tasks_lay.setContentsMargins(16, 18, 16, 16)
        tasks_lay.setSpacing(10)

        t_head = QLabel("المهام والتنبيهات")
        t_head.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        tasks_lay.addWidget(t_head)

        self.prog_lbl = QLabel("الإنجاز: 0%")
        self.prog_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        tasks_lay.addWidget(self.prog_lbl)

        self.prog_bar = QProgressBar()
        self.prog_bar.setTextVisible(False)
        tasks_lay.addWidget(self.prog_bar)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("مهمة جديدة ثم Enter...")
        self.task_input.returnPressed.connect(self.add_task)
        tasks_lay.addWidget(self.task_input)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(6)
        self.rem_input = QLineEdit()
        self.rem_input.setPlaceholderText("HH:MM")
        self.rem_input.setFixedWidth(76)
        sub_row.addWidget(self.rem_input)

        self.prio_combo = QComboBox()
        self.prio_combo.addItems(["High", "Medium", "Low"])
        self.prio_combo.setFixedWidth(86)
        sub_row.addWidget(self.prio_combo)

        add_t_btn = QPushButton("إضافة")
        add_t_btn.setObjectName("PrimaryBtn")
        add_t_btn.setStyleSheet("padding: 8px 10px; font-size: 12.5px;")
        add_t_btn.clicked.connect(self.add_task)
        sub_row.addWidget(add_t_btn, 1)
        tasks_lay.addLayout(sub_row)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(6)
        btn_15m = QPushButton("+15 دقيقة")
        btn_15m.setProperty("class", "QuickTimeBtn")
        btn_15m.clicked.connect(lambda: self.set_quick_reminder(15))

        btn_1h = QPushButton("+1 ساعة")
        btn_1h.setProperty("class", "QuickTimeBtn")
        btn_1h.clicked.connect(lambda: self.set_quick_reminder(60))

        quick_row.addWidget(btn_15m)
        quick_row.addWidget(btn_1h)
        quick_row.addStretch()
        tasks_lay.addLayout(quick_row)

        self.tasks_list_lay = QVBoxLayout()
        self.tasks_list_lay.setSpacing(7)
        tasks_lay.addLayout(self.tasks_list_lay)
        tasks_lay.addStretch()

        root_layout.addWidget(sidebar)
        root_layout.addWidget(notes_panel)
        root_layout.addWidget(editor_panel, 1)
        root_layout.addWidget(tasks_panel)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.set_status("جاهز للعمل", 3000)

        self.set_category("All")

    def set_quick_reminder(self, minutes):
        target_time = (datetime.now() + timedelta(minutes=minutes)).strftime("%H:%M")
        self.rem_input.setText(target_time)
        self.set_status(f"تم ضبط وقت التنبيه على {target_time}", 2500)

    # ================= Google Keep Sync =================
    def open_keep_settings(self):
        dlg = KeepSettingsDialog(self.data.get("keep", {}), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            self.data["keep"]["email"] = vals["email"]
            self.data["keep"]["master_token"] = vals["master_token"]
            self.data["keep"]["auto_sync"] = vals["auto_sync"]
            self.save_data()
            self.set_status("تم حفظ إعدادات Google Keep", 3500)

    def start_keep_sync(self):
        if self.is_syncing:
            return
        if not HAS_GKEEP:
            self.set_status("مكتبة gkeepapi غير مثبتة في هذه البيئة", 5000)
            QMessageBox.warning(
                self,
                "مكتبة مفقودة",
                "مكتبة gkeepapi غير مثبتة في بيئة التشغيل.\nثبتها عبر: pip install gkeepapi"
            )
            return

        cfg = self.data.get("keep", {})
        if not cfg.get("email") or not cfg.get("master_token"):
            self.open_keep_settings()
            cfg = self.data.get("keep", {})
            if not cfg.get("email") or not cfg.get("master_token"):
                return

        self.is_syncing = True
        self.sync_btn.setText(" جاري المزامنة...")
        self.sync_btn.setEnabled(False)
        self.set_status("جاري مزامنة الملاحظات مع Google Keep...", 10000)
        threading.Thread(target=self._sync_keep_worker, daemon=True).start()

    def _sync_keep_worker(self):
        try:
            cfg = self.data["keep"]
            keep = gkeepapi.Keep()
            keep.authenticate(cfg["email"], cfg["master_token"])

            local_by_keep_id = {}
            for n in self.data["notes"]:
                if n.get("password"):
                    continue
                if n.get("keep_id"):
                    kn = keep.get(n["keep_id"])
                    if kn and not kn.trashed:
                        kn.title = n["title"] or "بدون عنوان"
                        kn.text = n["content"] or ""
                        kn.pinned = bool(n.get("pinned"))
                        local_by_keep_id[n["keep_id"]] = n
                else:
                    created = keep.createNote(n["title"] or "بدون عنوان", n["content"] or "")
                    created.pinned = bool(n.get("pinned"))
                    n["keep_id"] = created.id
                    local_by_keep_id[created.id] = n

            keep.sync()

            for kn in keep.all():
                if kn.trashed or kn.id in local_by_keep_id:
                    continue
                self.data["notes"].append({
                    "id": f"keep_{kn.id}",
                    "keep_id": kn.id,
                    "title": kn.title or "ملاحظة من Keep",
                    "category": "All",
                    "content": kn.text or "",
                    "html": "",
                    "theme": "داكن أنيق",
                    "pinned": bool(kn.pinned),
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": []
                })

            now_str = datetime.now().strftime("%H:%M")
            self.data["keep"]["last_sync"] = f"تمت {now_str}"
            self.save_data()
            self.signaler.sync_finished.emit(True, f"تمت مزامنة Google Keep ({now_str})")
        except Exception as e:
            self.signaler.sync_finished.emit(False, f"تعذرت المزامنة: {e}")

    def on_sync_finished(self, ok, msg):
        self.is_syncing = False
        self.sync_btn.setText(" مزامنة Google Keep")
        self.sync_btn.setEnabled(True)
        self.sync_status_lbl.setText(f"Keep: {self.data['keep'].get('last_sync', '')}")
        self.refresh_notes_list()
        self.set_status(msg, 5000)
        if not ok:
            QMessageBox.warning(self, "خطأ المزامنة", msg)

    def auto_keep_worker(self):
        while True:
            time.sleep(300)
            if self.data.get("keep", {}).get("auto_sync") and not self.is_syncing:
                self.start_keep_sync()

    # ================= Editor Formatting =================
    def change_font_family(self, font):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.editor.mergeCurrentCharFormat(fmt)

    def change_font_size(self, sz_str):
        if sz_str.isdigit():
            fmt = QTextCharFormat()
            fmt.setFontPointSize(float(sz_str))
            self.editor.mergeCurrentCharFormat(fmt)

    def format_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        self.editor.mergeCurrentCharFormat(fmt)

    def format_italic(self):
        self.editor.setFontItalic(not self.editor.fontItalic())

    def format_underline(self):
        self.editor.setFontUnderline(not self.editor.fontUnderline())

    def pick_text_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.editor.setTextColor(c)

    def pick_highlight_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.editor.setTextBackgroundColor(c)

    def insert_bullet_list(self):
        self.editor.textCursor().insertList(QTextListFormat.Style.ListDisc)

    def apply_editor_theme(self, theme_name):
        th = PAGE_THEMES.get(theme_name, PAGE_THEMES["داكن أنيق"])
        self.editor.setStyleSheet(
            f"background-color: {th['bg']}; color: {th['fg']}; "
            f"border: 1px solid {th['border']}; border-radius: 12px; padding: 16px; font-size: 14.5px;"
        )

    def change_page_theme(self, theme_name):
        self.apply_editor_theme(theme_name)
        note = self.get_current_note()
        if note:
            note["theme"] = theme_name
            self.save_data()
            self.set_status(f"تم تغيير مظهر الصفحة إلى: {theme_name}", 2500)

    def open_floating_window(self):
        note = self.get_current_note()
        if not note:
            return
        w = FloatingNoteWindow(note, self)
        w.show()
        self.floating_windows.append(w)
        self.set_status("تم فتح الملاحظة في نافذة عائمة", 2500)

    # ================= Notes CRUD =================
    def set_category(self, cat):
        self.current_category = cat
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == cat else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.refresh_notes_list()

    def get_current_note(self):
        return next((n for n in self.data["notes"] if n["id"] == self.current_note_id), None)

    def refresh_notes_list(self):
        self.notes_list.clear()
        q = self.search_box.text().strip().lower()
        filtered = []

        for n in self.data["notes"]:
            locked = bool(n.get("password"))
            if self.current_category == "Pinned" and not n.get("pinned"):
                continue
            if self.current_category == "Locked" and not locked:
                continue
            if self.current_category not in ["All", "Pinned", "Locked"] and n.get("category") != self.current_category:
                continue
            if q and q not in n["title"].lower() and (locked or q not in n["content"].lower()):
                continue
            filtered.append(n)

        filtered.sort(key=lambda x: x.get("pinned", False), reverse=True)

        for n in filtered:
            title = (n["title"] or "بدون عنوان").strip()
            if n.get("password"):
                snippet = "ملاحظة مقفلة بكلمة مرور"
            else:
                one_line = " ".join((n.get("content") or "").split())
                snippet = (one_line[:52] + "...") if len(one_line) > 52 else (one_line or "بدون محتوى")

            sync_tag = "  •  Keep" if n.get("keep_id") else ""
            item_text = f"{title}\n{snippet}\n{n['category']}  •  {n['updated_at']}{sync_tag}"

            item = QListWidgetItem(item_text)
            if n.get("password"):
                item.setIcon(qta.icon("fa5s.lock", color="#EF4444"))
            elif n.get("pinned"):
                item.setIcon(qta.icon("fa5s.thumbtack", color="#F59E0B"))
            else:
                item.setIcon(qta.icon("fa5s.file-alt", color="#818CF8"))

            item.setData(Qt.ItemDataRole.UserRole, n["id"])
            self.notes_list.addItem(item)
            if n["id"] == self.current_note_id:
                item.setSelected(True)

        if not self.current_note_id and filtered:
            self.load_note(filtered[0]["id"])

    def on_note_clicked(self, item):
        self.load_note(item.data(Qt.ItemDataRole.UserRole))

    def load_note(self, note_id):
        note = next((n for n in self.data["notes"] if n["id"] == note_id), None)
        if not note:
            return

        if note.get("password") and note_id not in self.unlocked_notes:
            pwd, ok = QInputDialog.getText(self, "ملاحظة مقفلة", "أدخل كلمة المرور:", QLineEdit.EchoMode.Password)
            if not ok or pwd != note["password"]:
                if ok:
                    self.set_status("كلمة المرور غير صحيحة", 3500)
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_edit.blockSignals(True)
        self.editor.blockSignals(True)
        self.theme_combo.blockSignals(True)

        self.title_edit.setText(note["title"])
        theme_name = note.get("theme", "داكن أنيق")
        self.theme_combo.setCurrentText(theme_name)
        self.apply_editor_theme(theme_name)

        if note.get("html"):
            self.editor.setHtml(note["html"])
        else:
            self.editor.setPlainText(note.get("content", ""))

        self.cat_combo.setCurrentText(note.get("category", "Projects"))
        self.lock_btn.setText(" مقفلة" if note.get("password") else " قفل")
        self.lock_btn.setIcon(qta.icon("fa5s.lock" if note.get("password") else "fa5s.unlock", color="#F59E0B" if note.get("password") else "#CBD5E1"))
        self.pin_btn.setIcon(qta.icon("fa5s.thumbtack", color="#6366F1" if note.get("pinned") else "#CBD5E1"))

        self.title_edit.blockSignals(False)
        self.editor.blockSignals(False)
        self.theme_combo.blockSignals(False)

        self.update_stats()
        self.refresh_tasks()
        self.refresh_notes_list()

    def create_note(self):
        nid = str(int(datetime.now().timestamp() * 1000))
        cat = self.current_category if self.current_category not in ["All", "Pinned", "Locked"] else "Projects"
        self.data["notes"].insert(0, {
            "id": nid, "keep_id": "", "title": "ملاحظة جديدة", "category": cat,
            "content": "", "html": "", "theme": "داكن أنيق",
            "pinned": False, "password": "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "tasks": []
        })
        self.save_data()
        self.load_note(nid)
        self.set_status("تم إنشاء ملاحظة جديدة", 2500)

    def auto_save(self):
        note = self.get_current_note()
        if not note:
            return
        note["title"] = self.title_edit.text()
        note["content"] = self.editor.toPlainText()
        note["html"] = self.editor.toHtml()
        note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.update_stats()
        self.save_data()
        self.set_status("تم الحفظ تلقائياً", 1500)

    def update_stats(self):
        txt = self.editor.toPlainText()
        self.stats_lbl.setText(f"الكلمات: {len(txt.split())}  |  الأحرف: {len(txt)}")

    def change_category(self, cat):
        note = self.get_current_note()
        if note:
            note["category"] = cat
            self.save_data()
            self.refresh_notes_list()

    def toggle_pin(self):
        note = self.get_current_note()
        if note:
            note["pinned"] = not note.get("pinned", False)
            self.save_data()
            self.load_note(note["id"])
            self.set_status("تم تحديث حالة التثبيت", 2000)

    def toggle_lock(self):
        note = self.get_current_note()
        if not note:
            return
        if note.get("password"):
            if QMessageBox.question(self, "إزالة القفل", "إزالة كلمة المرور؟") == QMessageBox.StandardButton.Yes:
                note["password"] = ""
                self.save_data()
                self.load_note(note["id"])
                self.set_status("تم إزالة القفل عن الملاحظة", 2500)
        else:
            pwd, ok = QInputDialog.getText(self, "قفل الملاحظة", "أدخل كلمة مرور:", QLineEdit.EchoMode.Password)
            if ok and pwd.strip():
                note["password"] = pwd.strip()
                self.unlocked_notes.add(note["id"])
                self.save_data()
                self.load_note(note["id"])
                self.set_status("تم قفل الملاحظة بكلمة مرور", 2500)

    def delete_note(self):
        if not self.current_note_id:
            return
        if QMessageBox.question(self, "حذف", "حذف هذه الملاحظة نهائياً؟") == QMessageBox.StandardButton.Yes:
            self.data["notes"] = [n for n in self.data["notes"] if n["id"] != self.current_note_id]
            self.current_note_id = None
            self.title_edit.clear()
            self.editor.clear()
            self.save_data()
            self.refresh_notes_list()
            self.refresh_tasks()
            self.set_status("تم حذف الملاحظة", 2500)

    def export_note(self):
        note = self.get_current_note()
        if not note:
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير", f"{note['title']}.md", "Markdown (*.md);;HTML (*.html);;Text (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".html"):
                    f.write(note.get("html") or note.get("content", ""))
                else:
                    f.write(f"# {note['title']}\n\n{note['content']}\n")
            self.set_status(f"تم تصدير الملاحظة إلى: {os.path.basename(path)}", 4000)

    # ================= Tasks & Reminders =================
    def add_task(self):
        note = self.get_current_note()
        txt = self.task_input.text().strip()
        rem = self.rem_input.text().strip()
        if not note or not txt:
            return
        if rem:
            try:
                datetime.strptime(rem, "%H:%M")
            except ValueError:
                self.set_status("صيغة التنبيه يجب أن تكون HH:MM مثل 21:30", 4000)
                return
        note.setdefault("tasks", []).append({
            "text": txt, "done": False, "priority": self.prio_combo.currentText(),
            "reminder": rem, "alerted": False
        })
        self.task_input.clear()
        self.rem_input.clear()
        self.save_data()
        self.refresh_tasks()
        self.set_status("تمت إضافة المهمة", 2000)

    def refresh_tasks(self):
        while self.tasks_list_lay.count():
            ch = self.tasks_list_lay.takeAt(0)
            if ch.widget():
                ch.widget().deleteLater()

        note = self.get_current_note()
        tasks = note.get("tasks", []) if note else []
        p_colors = {"High": "#F87171", "Medium": "#FBBF24", "Low": "#34D399"}

        for idx, t in enumerate(tasks):
            card = QFrame()
            card.setProperty("class", "TaskRowCard")
            lay = QHBoxLayout(card)
            lay.setContentsMargins(9, 6, 9, 6)

            rem_txt = f" [{t['reminder']}]" if t.get("reminder") else ""
            cb = QCheckBox(f"{t['text']}{rem_txt}")
            cb.setChecked(t["done"])
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_task(i))
            lay.addWidget(cb, 1)

            prio = QLabel(t["priority"])
            prio.setStyleSheet(f"color: {p_colors.get(t['priority'], '#CBD5E1')}; font-size: 11px; font-weight: 700;")
            lay.addWidget(prio)

            rm_btn = QPushButton()
            rm_btn.setIcon(qta.icon("fa5s.times", color="#94A3B8"))
            rm_btn.setStyleSheet("border: none; background: transparent;")
            rm_btn.clicked.connect(lambda checked, i=idx: self.delete_task(i))
            lay.addWidget(rm_btn)

            self.tasks_list_lay.addWidget(card)

        if tasks:
            done = sum(1 for t in tasks if t["done"])
            pct = int((done / len(tasks)) * 100)
            self.prog_bar.setValue(pct)
            self.prog_lbl.setText(f"الإنجاز: {pct}% ({done}/{len(tasks)})")
        else:
            self.prog_bar.setValue(0)
            self.prog_lbl.setText("الإنجاز: 0%")

    def toggle_task(self, idx):
        note = self.get_current_note()
        if note:
            note["tasks"][idx]["done"] = not note["tasks"][idx]["done"]
            self.save_data()
            self.refresh_tasks()

    def delete_task(self, idx):
        note = self.get_current_note()
        if note:
            note["tasks"].pop(idx)
            self.save_data()
            self.refresh_tasks()

    def reminder_worker(self):
        while True:
            now = datetime.now().strftime("%H:%M")
            for note in self.data.get("notes", []):
                for t in note.get("tasks", []):
                    if not t.get("done") and t.get("reminder") == now and not t.get("alerted"):
                        t["alerted"] = True
                        self.save_data()
                        self.signaler.alarm_triggered.emit(t["text"], note["title"])
            time.sleep(10)

    def show_alarm_popup(self, task_text, note_title):
        try:
            winsound.Beep(1000, 500)
        except Exception:
            pass
        QMessageBox.information(self, "تذكير", f"المهمة: {task_text}\nالملاحظة: {note_title}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLESHEET)
    win = NotesHamzaStudio()
    win.show()
    sys.exit(app.exec())
