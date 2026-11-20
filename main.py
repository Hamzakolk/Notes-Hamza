import sys
import json
import os
import threading
import time
import winsound
from datetime import datetime
from PIL import Image, ImageDraw
import qtawesome as qta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QFrame, QMessageBox, QInputDialog, QFileDialog,
    QCheckBox, QFontComboBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QColor, QTextListFormat

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"


def generate_app_icon():
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([20, 20, 236, 236], radius=50, fill=(59, 130, 246, 255))
        draw.rounded_rectangle([65, 70, 191, 88], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([65, 118, 191, 136], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([65, 166, 145, 184], radius=8, fill=(147, 197, 253, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])


PAGE_THEMES = {
    "افتراضي (ليلي داكن)": {"bg": "#111827", "fg": "#F8FAFC"},
    "أزرق ليلي عميق": {"bg": "#0F172A", "fg": "#E2E8F0"},
    "أخضر زمردي داكن": {"bg": "#062C22", "fg": "#ECFDF5"},
    "بنفسجي ملكي داكن": {"bg": "#1E1035", "fg": "#F3E8FF"},
    "ورقة صفراء دافئة": {"bg": "#FEF9C3", "fg": "#1E293B"},
    "ورقة بيضاء كلاسيكية": {"bg": "#FFFFFF", "fg": "#0F172A"}
}

STYLESHEET = """
QMainWindow {
    background-color: #0B0F19;
}
QWidget {
    color: #F8FAFC;
    font-family: 'Segoe UI', Tahoma, Arial;
    font-size: 14px;
}
#Sidebar {
    background-color: #111827;
    border-left: 1px solid #1F2937;
}
#LogoLabel {
    font-size: 20px;
    font-weight: bold;
    color: #3B82F6;
    padding: 15px 5px;
}
#NewNoteBtn {
    background-color: #2563EB;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 12px;
    font-size: 15px;
}
#NewNoteBtn:hover {
    background-color: #1D4ED8;
}
.NavBtn {
    background-color: transparent;
    text-align: right;
    padding: 10px 15px;
    border-radius: 8px;
    color: #9CA3AF;
    font-weight: 600;
}
.NavBtn:hover {
    background-color: #1F2937;
    color: #F9FAFB;
}
.NavBtn[active="true"] {
    background-color: #1E293B;
    color: #3B82F6;
    border-right: 3px solid #3B82F6;
}
#NotesPanel {
    background-color: #0F172A;
    border-left: 1px solid #1E293B;
}
#SearchBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px 14px;
    color: #F8FAFC;
}
#SearchBox:focus {
    border: 1px solid #3B82F6;
}
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    background-color: #161F33;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 8px;
    border: 1px solid transparent;
}
QListWidget::item:hover {
    background-color: #1E293B;
    border: 1px solid #334155;
}
QListWidget::item:selected {
    background-color: #1E293B;
    border: 1px solid #3B82F6;
}
#EditorPanel {
    background-color: #0B0F19;
}
#TitleInput {
    background-color: transparent;
    border: none;
    font-size: 24px;
    font-weight: bold;
    color: #FFFFFF;
    padding: 5px;
}
#FormatBar {
    background-color: #111827;
    border-radius: 10px;
    border: 1px solid #1F2937;
}
.ToolBtn {
    background-color: transparent;
    border-radius: 6px;
    padding: 6px 10px;
    color: #CBD5E1;
    font-weight: bold;
}
.ToolBtn:hover {
    background-color: #1F2937;
    color: #FFFFFF;
}
QComboBox, QFontComboBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 10px;
    color: white;
}
#TodoPanel {
    background-color: #111827;
    border-right: 1px solid #1F2937;
}
QProgressBar {
    background-color: #1E293B;
    border-radius: 5px;
    height: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #10B981;
    border-radius: 5px;
}
.TaskCard {
    background-color: #1E293B;
    border-radius: 10px;
    padding: 8px;
    border: 1px solid #2D3748;
}
QLineEdit {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
}
"""


class AlarmSignaler(QObject):
    triggered = pyqtSignal(str, str)


class FloatingNoteWindow(QWidget):
    def __init__(self, note, parent_app):
        super().__init__()
        self.note = note
        self.parent_app = parent_app
        self.setWindowTitle(f"📌 {note.get('title', 'ملاحظة طائرة')} - Notes Hamza")
        self.resize(520, 480)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        self.title_lbl = QLabel(note.get("title", "بدون عنوان"))
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #3B82F6;")
        layout.addWidget(self.title_lbl)

        self.float_editor = QTextEdit()
        theme = PAGE_THEMES.get(note.get("theme", "افتراضي (ليلي داكن)"), PAGE_THEMES["افتراضي (ليلي داكن)"])
        self.float_editor.setStyleSheet(
            f"background-color: {theme['bg']}; color: {theme['fg']}; border-radius: 10px; padding: 12px; font-size: 15px;"
        )
        if note.get("html"):
            self.float_editor.setHtml(note["html"])
        else:
            self.float_editor.setPlainText(note.get("content", ""))

        self.float_editor.textChanged.connect(self.sync_back)
        layout.addWidget(self.float_editor)

    def sync_back(self):
        self.note["content"] = self.float_editor.toPlainText()
        self.note["html"] = self.float_editor.toHtml()
        self.note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.parent_app.save_data()
        if self.parent_app.current_note_id == self.note["id"]:
            self.parent_app.editor.blockSignals(True)
            self.parent_app.editor.setHtml(self.note["html"])
            self.parent_app.editor.blockSignals(False)
            self.parent_app.update_stats()


class NotesHamzaPro(QMainWindow):
    def __init__(self):
        super().__init__()
        generate_app_icon()
        self.setWindowTitle("Notes Hamza Pro - إدارة الملاحظات والمهام")
        self.resize(1380, 840)
        if os.path.exists(ICON_FILE):
            self.setWindowIcon(QIcon(ICON_FILE))

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.data = self.load_data()
        self.current_note_id = None
        self.current_category = "All"
        self.unlocked_notes = set()
        self.nav_buttons = {}
        self.floating_windows = []

        self.signaler = AlarmSignaler()
        self.signaler.triggered.connect(self.show_alarm_popup)

        self.init_ui()
        self.refresh_notes_list()

        threading.Thread(target=self.reminder_worker, daemon=True).start()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "notes": [
                {
                    "id": "1",
                    "title": "مرحباً بك في Notes Hamza Pro",
                    "category": "Projects",
                    "content": (
                        "تم تحديث البرنامج بأيقونات حديثة ومحرر نصوص متكامل شبيه بـ Word.\n\n"
                        "• يمكنك تغيير نوع الخط وحجمه ولونه\n"
                        "• يمكنك تلوين خلفية كل صفحة ملاحظة بشكل مستقل\n"
                        "• يمكنك فتح أي ملاحظة في تبويب طائر فوق البرامج"
                    ),
                    "html": "",
                    "theme": "افتراضي (ليلي داكن)",
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": "تجربة شريط تنسيق الخطوط والألوان", "done": False, "priority": "High", "reminder": ""},
                        {"text": "فتح الملاحظة في نافذة طائرة", "done": False, "priority": "Medium", "reminder": ""}
                    ]
                }
            ]
        }

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= 1. القائمة الجانبية =================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(235)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 20, 16, 20)
        side_layout.setSpacing(8)

        logo = QLabel("  Notes Hamza")
        logo.setObjectName("LogoLabel")
        side_layout.addWidget(logo)

        new_btn = QPushButton("  ملاحظة جديدة")
        new_btn.setIcon(qta.icon("fa5s.plus-circle", color="white"))
        new_btn.setIconSize(QSize(18, 18))
        new_btn.setObjectName("NewNoteBtn")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.create_note)
        side_layout.addWidget(new_btn)
        side_layout.addSpacing(15)

        cats = [
            ("جميع الملاحظات", "All", "fa5s.folder-open", "#60A5FA"),
            ("المثبتة بالأعلى", "Pinned", "fa5s.thumbtack", "#F59E0B"),
            ("الملاحظات السرية", "Locked", "fa5s.lock", "#EF4444"),
            ("المشاريع", "Projects", "fa5s.rocket", "#A78BFA"),
            ("شخصي", "Personal", "fa5s.user", "#34D399"),
            ("العمل", "Work", "fa5s.briefcase", "#38BDF8"),
            ("أفكار
