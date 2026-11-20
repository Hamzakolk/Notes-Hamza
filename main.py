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
    QCheckBox, QFontComboBox, QColorDialog, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QColor, QTextListFormat

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"

def generate_app_icon():
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([16, 16, 240, 240], radius=50, fill=(59, 130, 246, 255))
        draw.rounded_rectangle([60, 70, 196, 92], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([60, 118, 170, 140], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([60, 166, 140, 188], radius=8, fill=(147, 197, 253, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])

STYLESHEET = """
QMainWindow, QWidget#FloatingWin {
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
    padding: 10px 14px;
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
QComboBox, QFontComboBox, QSpinBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px 8px;
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

NOTE_PAGE_THEMES = {
    "داكن افتراضي": ("#111827", "#F8FAFC"),
    "أزرق ليلي": ("#0F2942", "#F0F9FF"),
    "أخضر زمردي": ("#063729", "#ECFDF5"),
    "بنفسجي هادئ": ("#24163D", "#F5F3FF"),
    "بني دافئ": ("#2C1E16", "#FFFBEB"),
    "ورقة صفراء": ("#FEF9C3", "#1E293B"),
    "ورقة بيضاء": ("#FFFFFF", "#0F172A"),
}

class AlarmSignaler(QObject):
    triggered = pyqtSignal(str, str)


class FloatingNoteWindow(QWidget):
    """نافذة طائرة مستقلة لفتح الملاحظة خارج البرنامج الرئيسي"""
    def __init__(self, note_data, save_callback, refresh_main_callback):
        super().__init__()
        self.note = note_data
        self.save_callback = save_callback
        self.refresh_main_callback = refresh_main_callback

        self.setObjectName("FloatingWin")
        self.setWindowTitle(f"📌 {self.note['title']} - نافذة مستقلة")
        self.resize(620, 520)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top_bar = QHBoxLayout()
        self.title_edit = QLineEdit(self.note["title"])
        self.title_edit.setStyleSheet("font-size: 18px; font-weight: bold; background: #1E293B; border: none;")
        self.title_edit.textEdited.connect(self.on_change)
        top_bar.addWidget(self.title_edit)

        self.pin_top_btn = QPushButton("مثبت فوق النوافذ")
        self.pin_top_btn.setCheckable(True)
        self.pin_top_btn.setChecked(True)
        self.pin_top_btn.setIcon(qta.icon("fa5s.thumbtack", color="#3B82F6"))
        self.pin_top_btn.setProperty("class", "ToolBtn")
        self.pin_top_btn.clicked.connect(self.toggle_on_top)
        top_bar.addWidget(self.pin_top_btn)

        layout.addLayout(top_bar)

        self.editor = QTextEdit()
        self.editor.setHtml(self.note.get("html_content") or self.note.get("content", ""))
        self.apply_page_theme()
        self.editor.textChanged.connect(self.on_change)
        layout.addWidget(self.editor)

    def apply_page_theme(self):
        bg, fg = NOTE_PAGE_THEMES.get(self.note.get("page_theme", "داكن افتراضي"), ("#111827", "#F8FAFC"))
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 14px;
                font-size: 15px;
            }}
        """)

    def toggle_on_top(self):
        flags = self.windowFlags()
        if self.pin_top_btn.isChecked():
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def on_change(self):
        self.note["title"] = self.title_edit.text()
        self.note["content"] = self.editor.toPlainText()
        self.note["html_content"] = self.editor.toHtml()
        self.note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save_callback()
        self.refresh_main_callback(self.note["id"])


class NotesHamzaPro(QMainWindow):
    def __init__(self):
        super().__init__()
        generate_app_icon()
        self.setWindowTitle("Notes Hamza Pro - محرر الملاحظات والمهام المتطور")
        self.resize(1420, 840)
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
                    "content": "أهلاً بك في النسخة الاحترافية بالأيقونات الحديثة ومحرر النصوص المتكامل!",
                    "html_content": "",
                    "page_theme": "داكن افتراضي",
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": "تجربة شريط أدوات التنسيق (الخط، الحجم، الألوان)", "done": False, "priority": "High", "reminder": ""},
                        {"text": "فتح ملاحظة في نافذة طائرة مستقلة", "done": False, "priority": "Medium", "reminder": ""}
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

        logo_row = QHBoxLayout()
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon("fa5s.feather-alt", color="#3B82F6").pixmap(24, 24))
        logo_text = QLabel("Notes Hamza")
        logo_text.setObjectName("LogoLabel")
        logo_row.addWidget(logo_icon)
        logo_row.addWidget(logo_text)
        logo_row.addStretch()
        side_layout.addLayout(logo_row)

        new_btn = QPushButton("  ملاحظة جديدة")
        new_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        new_btn.setObjectName("NewNoteBtn")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.create_note)
        side_layout.addWidget(new_btn)
        side_layout.addSpacing(12)

        cats = [
            ("جميع الملاحظات", "All", "fa5s.layer-group", "#60A5FA"),
            ("المثبتة بالأعلى", "Pinned", "fa5s.thumbtack", "#F59E0B"),
            ("الملاحظات السرية", "Locked", "fa5s.lock", "#EF4444"),
            ("المشاريع", "Projects", "fa5s.rocket", "#8B5CF6"),
            ("شخصي", "Personal", "fa5s.user", "#10B981"),
            ("العمل", "Work", "fa5s.briefcase", "#3B82F6"),
            ("أفكار", "Ideas", "fa5s.lightbulb", "#FBBF24")
        ]
        for text, key, icon_name, color in cats:
            btn = QPushButton(f"  {text}")
            btn.setIcon(qta.icon(icon_name, color=color))
            btn.setIconSize(QSize(16, 16))
            btn.setProperty("class", "NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.set_category(k))
            side_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        side_layout.addStretch()

        export_btn = QPushButton("  تصدير الملاحظة")
        export_btn.setIcon(qta.icon("fa5s.file-export", color="#94A3B8"))
        export_btn.setProperty("class", "NavBtn")
        export_btn.clicked.connect(self.export_note)
        side_layout.addWidget(export_btn)

        # ================= 2. قائمة الملاحظات =================
        notes_panel = QFrame()
        notes_panel.setObjectName("NotesPanel")
        notes_panel.setFixedWidth(285)
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(14, 20, 14, 14)
        notes_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBox")
        self.search_input.setPlaceholderText("ابحث في ملاحظاتك...")
        self.search_input.textChanged.connect(self.refresh_notes_list)
        notes_layout.addWidget(self.search_input)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_clicked)
        notes_layout.addWidget(self.notes_list)

        # ================= 3. محرر النصوص المتطور (مثل Word) =================
        editor_panel = QFrame()
        editor_panel.setObjectName("EditorPanel")
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(22, 18, 22, 14)
        editor_layout.setSpacing(10)

        # الشريط العلوي للعنوان والأزرار
        header_row = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setObjectName("TitleInput")
        self.title_input.setPlaceholderText("عنوان الملاحظة...")
        self.title_input.textEdited.connect(self.auto_save)
        header_row.addWidget(self.title_input)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["Projects", "Personal", "Work", "Ideas"])
        self.cat_combo.currentTextChanged.connect(self.change_category)
        header_row.addWidget(self.cat_combo)

        # زر فتح الملاحظة في تبويب طائر خارج البرنامج
        self.popout_btn = QPushButton(" نافذة طائرة")
        self.popout_btn.setIcon(qta.icon("fa5s.external-link-alt", color="#38BDF8"))
        self.popout_btn.setProperty("class", "ToolBtn")
        self.popout_btn.setToolTip("فتح الملاحظة في نافذة مستقلة عائمة")
        self.popout_btn.clicked.connect(self.open_floating_window)
        header_row.addWidget(self.popout_btn)

        self.lock_btn = QPushButton(" قفل")
        self.lock_btn.setIcon(qta.icon("fa5s.unlock", color="#CBD5E1"))
        self.lock_btn.setProperty("class", "ToolBtn")
        self.lock_btn.clicked.connect(self.toggle_lock)
        header_row.addWidget(self.lock_btn)

        self.pin_btn = QPushButton(" تثبيت")
        self.pin_btn.setIcon(qta.icon("fa5s.thumbtack", color="#CBD5E1"))
        self.pin_btn.setProperty("class", "ToolBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        header_row.addWidget(self.pin_btn)

        del_btn = QPushButton()
        del_btn.setIcon(qta.icon("fa5s.trash-alt", color="#EF4444"))
        del_btn.setProperty("class", "ToolBtn")
        del_btn.clicked.connect(self.delete_note)
        header_row.addWidget(del_btn)

        editor_layout.addLayout(header_row)

        # شريط تنسيق النصوص الشبيه بـ Word (صفين مدمجين وأنيقين)
        format_bar = QFrame()
        format_bar.setObjectName("FormatBar")
        fmt_layout = QHBoxLayout(format_bar)
        fmt_layout.setContentsMargins(10, 6, 10, 6)
        fmt_layout.setSpacing(6)

        # اختيار نوع الخط
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setFixedWidth(145)
        self.font_family_combo.currentFontChanged.connect(lambda f: self.editor.setFontFamily(f.family()))
        fmt_layout.addWidget(self.font_family_combo)

        # اختيار حجم الخط
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(14)
        self.font_size_spin.setFixedWidth(60)
        self.font_size_spin.valueChanged.connect(lambda s: self.editor.setFontPointSize(float(s)))
        fmt_layout.addWidget(self.font_size_spin)

        # أزرار Bold, Italic, Underline, Strike
        btn_bold = QPushButton()
        btn_bold.setIcon(qta.icon("fa5s.bold", color="#E2E8F0"))
        btn_bold.setProperty("class", "ToolBtn")
        btn_bold.setToolTip("عريض (Bold)")
        btn_bold.clicked.connect(self.format_bold)
        fmt_layout.addWidget(btn_bold)

        btn_italic = QPushButton()
        btn_italic.setIcon(qta.icon("fa5s.italic", color="#E2E8F0"))
        btn_italic.setProperty("class", "ToolBtn")
        btn_italic.setToolTip("مائل (Italic)")
        btn_italic.clicked.connect(self.format_italic)
        fmt_layout.addWidget(btn_italic)

        btn_under = QPushButton()
        btn_under.setIcon(qta.icon("fa5s.underline", color="#E2E8F0"))
        btn_under.setProperty("class", "ToolBtn")
        btn_under.setToolTip("تحته خط (Underline)")
        btn_under.clicked.connect(self.format_underline)
        fmt_layout.addWidget(btn_under)

        btn_strike = QPushButton()
        btn_strike.setIcon(qta.icon("fa5s.strikethrough", color="#E2E8F0"))
        btn_strike.setProperty("class", "ToolBtn")
        btn_strike.setToolTip("يتوسطه خط")
        btn_strike.clicked.connect(self.format_strike)
        fmt_layout.addWidget(btn_strike)

        # لون الخط ولون التظليل
        btn_txt_color = QPushButton()
        btn_txt_color.setIcon(qta.icon("fa5s.font", color="#38BDF8"))
        btn_txt_color.setProperty("class", "ToolBtn")
        btn_txt_color.setToolTip("تغيير لون الخط")
        btn_txt_color.clicked.connect(self.pick_text_color)
        fmt_layout.addWidget(btn_txt_color)

        btn_highlight = QPushButton()
        btn_highlight.setIcon(qta.icon("fa5s.highlighter", color="#FACC15"))
        btn_highlight.setProperty("class", "ToolBtn")
        btn_highlight.setToolTip("تمييز / تظليل النص")
        btn_highlight.clicked.connect(self.pick_highlight_color)
        fmt_layout.addWidget(btn_highlight)

        # محاذاة وقوائم
        btn_align_r = QPushButton()
        btn_align_r.setIcon(qta.icon("fa5s.align-right", color="#E2E8F0"))
        btn_align_r.setProperty("class", "ToolBtn")
        btn_align_r.clicked.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        fmt_layout.addWidget(btn_align_r)

        btn_align_c = QPushButton()
        btn_align_c.setIcon(qta.icon("fa5s.align-center", color="#E2E8F0"))
        btn_align_c.setProperty("class", "ToolBtn")
        btn_align_c.clicked.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        fmt_layout.addWidget(btn_align_c)

        btn_list = QPushButton()
        btn_list.setIcon(qta.icon("fa5s.list-ul", color="#E2E8F0"))
        btn_list.setProperty("class", "ToolBtn")
        btn_list.setToolTip("قائمة نقطية")
        btn_list.clicked.connect(self.insert_bullet_list)
        fmt_layout.addWidget(btn_list)

        fmt_layout.addStretch()

        # اختيار لون خلفية الصفحة لكل ملاحظة
        page_lbl = QLabel("لون الصفحة:")
        page_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        fmt_layout.addWidget(page_lbl)

        self.page_theme_combo = QComboBox()
        self.page_theme_combo.addItems(list(NOTE_PAGE_THEMES.keys()))
        self.page_theme_combo.currentTextChanged.connect(self.change_page_theme)
        fmt_layout.addWidget(self.page_theme_combo)

        editor_layout.addWidget(format_bar)

        self.editor = QTextEdit()
        self.editor.setObjectName("ContentEditor")
        self.editor.setPlaceholderText("ابدأ بكتابة أفكارك وملاحظاتك المنسقة هنا...")
        self.editor.textChanged.connect(self.auto_save)
        editor_layout.addWidget(self.editor)

        self.stats_label = QLabel("الكلمات: 0   |   الأحرف: 0")
        self.stats_label.setStyleSheet("color: #64748B; font-size: 12px;")
        editor_layout.addWidget(self.stats_label)

        # ================= 4. لوحة المهام الذكية =================
        todo_panel = QFrame()
        todo_panel.setObjectName("TodoPanel")
        todo_panel.setFixedWidth(335)
        todo_layout = QVBoxLayout(todo_panel)
        todo_layout.setContentsMargins(18, 20, 18, 18)
        todo_layout.setSpacing(12)

        todo_header = QHBoxLayout()
        t_icon = QLabel()
        t_icon.setPixmap(qta.icon("fa5s.check-circle", color="#10B981").pixmap(20, 20))
        todo_title = QLabel("قائمة المهام والتنبيهات")
        todo_title.setStyleSheet("font-size: 17px; font-weight: bold;")
        todo_header.addWidget(t_icon)
        todo_header.addWidget(todo_title)
        todo_header.addStretch()
        todo_layout.addLayout(todo_header)

        self.progress_text = QLabel("نسبة الإنجاز: 0%")
        self.progress_text.setStyleSheet("color: #94A3B8; font-size: 13px;")
        todo_layout.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        todo_layout.addWidget(self.progress_bar)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("اكتب مهمة جديدة واضغط Enter...")
        self.task_input.returnPressed.connect(self.add_task)
        todo_layout.addWidget(self.task_input)

        task_controls = QHBoxLayout()
        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText("تنبيه HH:MM")
        self.reminder_input.setFixedWidth(105)
        task_controls.addWidget(self.reminder_input)

        self.prio_combo = QComboBox()
        self.prio_combo.addItems(["High", "Medium", "Low"])
        task_controls.addWidget(self.prio_combo)

        add_task_btn = QPushButton(" إضافة")
        add_task_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        add_task_btn.setStyleSheet("background-color: #2563EB; border-radius: 8px; padding: 8px 12px; font-weight: bold;")
        add_task_btn.clicked.connect(self.add_task)
        task_controls.addWidget(add_task_btn)
        todo_layout.addLayout(task_controls)

        self.tasks_container = QVBoxLayout()
        self.tasks_container.setSpacing(8)
        todo_layout.addLayout(self.tasks_container)
        todo_layout.addStretch()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(notes_panel)
        main_layout.addWidget(editor_panel, 1)
        main_layout.addWidget(todo_panel)

        self.set_category("All")

    # ================= وظائف التنسيق المتقدمة (Word-Like) =================
    def format_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        self.editor.mergeCurrentCharFormat(fmt)

    def format_italic(self):
        self.editor.setFontItalic(not self.editor.fontItalic())

    def format_underline(self):
        self.editor.setFontUnderline(not self.editor.fontUnderline())

    def format_strike(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.editor.mergeCurrentCharFormat(fmt)

    def pick_text_color(self):
        color = QColorDialog.getColor(parent=self, title="اختر لون الخط")
        if color.isValid():
            self.editor.setTextColor(color)

    def pick_highlight_color(self):
        color = QColorDialog.getColor(parent=self, title="اختر لون تظليل النص")
        if color.isValid():
            self.editor.setTextBackgroundColor(color)

    def insert_bullet_list(self):
        cursor = self.editor.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDisc)

    def change_page_theme(self, theme_name):
        note = self.get_current_note()
        if note:
            note["page_theme"] = theme_name
            self.apply_editor_theme(theme_name)
            self.save_data()
            self.refresh_notes_list()

    def apply_editor_theme(self, theme_name):
        bg, fg = NOTE_PAGE_THEMES.get(theme_name, ("#111827", "#F8FAFC"))
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid #1F2937;
                border-radius: 12px;
                padding: 18px;
                font-size: 15px;
                line-height: 1.6;
            }}
        """)

    def open_floating_window(self):
        note = self.get_current_note()
        if not note:
            return
        win = FloatingNoteWindow(note, self.save_data, self.sync_from_floating)
        win.show()
        self.floating_windows.append(win)

    def sync_from_floating(self, note_id):
        if self.current_note_id == note_id:
            note = self.get_current_note()
            if note:
                self.title_input.blockSignals(True)
                self.editor.blockSignals(True)
                self.title_input.setText(note["title"])
                self.editor.setHtml(note.get("html_content") or note.get("content", ""))
                self.title_input.blockSignals(False)
                self.editor.blockSignals(False)
                self.update_stats()
        self.refresh_notes_list()

    # ================= الوظائف الأساسية =================
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
        query = self.search_input.text().lower()
        notes = []

        for n in self.data["notes"]:
            is_locked = bool(n.get("password"))
            if self.current_category == "Pinned" and not n.get("pinned"):
                continue
            elif self.current_category == "Locked" and not is_locked:
                continue
            elif self.current_category not in ["All", "Pinned", "Locked"] and n.get("category") != self.current_category:
                continue

            if query in n["title"].lower() or (not is_locked and query in n["content"].lower()):
                notes.append(n)

        notes.sort(key=lambda x: x.get("pinned", False), reverse=True)

        for n in notes:
            theme_bg, _ = NOTE_PAGE_THEMES.get(n.get("page_theme", "داكن افتراضي"), ("#161F33", "#FFF"))
            item = QListWidgetItem(f"{n['title'] or 'بدون عنوان'}
{n['category']}  •  {n['updated_at']}")
            item.setData(Qt.ItemDataRole.UserRole, n["id"])
            if n.get("password"):
                item.setIcon(qta.icon("fa5s.lock", color="#EF4444"))
            elif n.get("pinned"):
                item.setIcon(qta.icon("fa5s.thumbtack", color="#F59E0B"))
            else:
                item.setIcon(qta.icon("fa5s.sticky-note", color=theme_bg if theme_bg != "#111827" else "#3B82F6"))

            self.notes_list.addItem(item)
            if n["id"] == self.current_note_id:
                item.setSelected(True)

        if not self.current_note_id and notes:
            self.load_note(notes[0]["id"])

    def on_note_clicked(self, item):
        self.load_note(item.data(Qt.ItemDataRole.UserRole))

    def load_note(self, note_id):
        note = next((n for n in self.data["notes"] if n["id"] == note_id), None)
        if not note:
            return

        if note.get("password") and note_id not in self.unlocked_notes:
            pwd, ok = QInputDialog.getText(self, "ملاحظة محمية", "أدخل كلمة المرور:", QLineEdit.EchoMode.Password)
            if not ok or pwd != note["password"]:
                if ok:
                    QMessageBox.warning(self, "خطأ", "كلمة المرور غير صحيحة!")
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_input.blockSignals(True)
        self.editor.blockSignals(True)
        self.page_theme_combo.blockSignals(True)

        self.title_input.setText(note["title"])
        if note.get("html_content"):
            self.editor.setHtml(note["html_content"])
        else:
            self.editor.setPlainText(note["content"])

        self.cat_combo.setCurrentText(note.get("category", "Projects"))
        theme = note.get("page_theme", "داكن افتراضي")
        self.page_theme_combo.setCurrentText(theme)
        self.apply_editor_theme(theme)

        if note.get("password"):
            self.lock_btn.setText(" مقفلة")
            self.lock_btn.setIcon(qta.icon("fa5s.lock", color="#F59E0B"))
        else:
            self.lock_btn.setText(" قفل")
            self.lock_btn.setIcon(qta.icon("fa5s.unlock", color="#CBD5E1"))

        self.pin_btn.setIcon(qta.icon("fa5s.thumbtack", color="#3B82F6" if note.get("pinned") else "#CBD5E1"))

        self.title_input.blockSignals(False)
        self.editor.blockSignals(False)
        self.page_theme_combo.blockSignals(False)

        self.update_stats()
        self.refresh_tasks()
        self.refresh_notes_list()

    def create_note(self):
        new_id = str(int(datetime.now().timestamp() * 1000))
        cat = self.current_category if self.current_category not in ["All", "Pinned", "Locked"] else "Projects"
        self.data["notes"].insert(0, {
            "id": new_id, "title": "ملاحظة جديدة", "category": cat,
            "content": "", "html_content": "", "page_theme": "داكن افتراضي",
            "pinned": False, "password": "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "tasks": []
        })
        self.save_data()
        self.load_note(new_id)

    def auto_save(self):
        note = self.get_current_note()
        if not note:
            return
        note["title"] = self.title_input.text()
        note["content"] = self.editor.toPlainText()
        note["html_content"] = self.editor.toHtml()
        note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.update_stats()
        self.save_data()

    def update_stats(self):
        txt = self.editor.toPlainText()
        self.stats_label.setText(f"الكلمات: {len(txt.split())}   |   الأحرف: {len(txt)}")

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

    def toggle_lock(self):
        note = self.get_current_note()
        if not note:
            return
        if note.get("password"):
            reply = QMessageBox.question(self, "إزالة القفل", "هل تريد إزالة كلمة المرور عن هذه الملاحظة؟")
            if reply == QMessageBox.StandardButton.Yes:
                note["password"] = ""
                self.save_data()
                self.load_note(note["id"])
        else:
            pwd, ok = QInputDialog.getText(self, "قفل الملاحظة", "أدخل كلمة مرور جديدة:", QLineEdit.EchoMode.Password)
            if ok and pwd.strip():
                note["password"] = pwd.strip()
                self.unlocked_notes.add(note["id"])
                self.save_data()
                self.load_note(note["id"])

    def delete_note(self):
        if not self.current_note_id:
            return
        reply = QMessageBox.question(self, "حذف الملاحظة", "هل أنت متأكد من حذف هذه الملاحظة نهائياً؟")
        if reply == QMessageBox.StandardButton.Yes:
            self.data["notes"] = [n for n in self.data["notes"] if n["id"] != self.current_note_id]
            self.current_note_id = None
            self.title_input.clear()
            self.editor.clear()
            self.save_data()
            self.refresh_notes_list()
            self.refresh_tasks()

    def export_note(self):
        note = self.get_current_note()
        if not note:
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير الملاحظة", f"{note['title']}.html", "HTML File (*.html);;Markdown (*.md);;Text (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".html"):
                    f.write(note.get("html_content") or note["content"])
                else:
                    f.write(f"# {note['title']}\n\n{note['content']}\n\n## المهام:\n")
                    for t in note.get("tasks", []):
                        f.write(f"- [{'x' if t['done'] else ' '}] {t['text']} ({t['priority']})\n")
            QMessageBox.information(self, "تم التصدير", "تم حفظ الملاحظة بنجاح!")

    # ================= المهام =================
    def add_task(self):
        note = self.get_current_note()
        txt = self.task_input.text().strip()
        rem = self.reminder_input.text().strip()
        if not note or not txt:
            return
        if rem:
            try:
                datetime.strptime(rem, "%H:%M")
            except ValueError:
                QMessageBox.warning(self, "تنسيق خاطئ", "أدخل وقت التنبيه بصيغة HH:MM مثل 18:30")
                return

        note.setdefault("tasks", []).append({
            "text": txt, "done": False, "priority": self.prio_combo.currentText(),
            "reminder": rem, "alerted": False
        })
        self.task_input.clear()
        self.reminder_input.clear()
        self.save_data()
        self.refresh_tasks()

    def refresh_tasks(self):
        while self.tasks_container.count():
            child = self.tasks_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        note = self.get_current_note()
        tasks = note.get("tasks", []) if note else []
        colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

        for idx, t in enumerate(tasks):
            card = QFrame()
            card.setProperty("class", "TaskCard")
            row = QHBoxLayout(card)
            row.setContentsMargins(10, 6, 10, 6)

            rem_str = f"  [{t['reminder']}]" if t.get("reminder") else ""
            cb = QCheckBox(f"{t['text']}{rem_str}")
            cb.setChecked(t["done"])
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_task(i))
            row.addWidget(cb, 1)

            badge = QLabel(t["priority"])
            badge.setStyleSheet(f"color: {colors.get(t['priority'], '#FFF')}; font-weight: bold; font-size: 11px;")
            row.addWidget(badge)

            del_btn = QPushButton()
            del_btn.setIcon(qta.icon("fa5s.times", color="#94A3B8"))
            del_btn.setStyleSheet("border: none;")
            del_btn.clicked.connect(lambda checked, i=idx: self.delete_task(i))
            row.addWidget(del_btn)

            self.tasks_container.addWidget(card)

        if tasks:
            done = sum(1 for t in tasks if t["done"])
            pct = int((done / len(tasks)) * 100)
            self.progress_bar.setValue(pct)
            self.progress_text.setText(f"نسبة الإنجاز: {pct}% ({done} من {len(tasks)})")
        else:
            self.progress_bar.setValue(0)
            self.progress_text.setText("نسبة الإنجاز: 0%")

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
                        self.signaler.triggered.emit(t["text"], note["title"])
            time.sleep(10)

    def show_alarm_popup(self, task_text, note_title):
        try:
            winsound.Beep(1000, 600)
            winsound.Beep(1300, 600)
        except Exception:
            pass
        QMessageBox.information(self, "تذكير بمهمة - Notes Hamza", f"حان موعد المهمة:\n\n• {task_text}\n(من ملاحظة: {note_title})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = NotesHamzaPro()
    window.show()
    sys.exit(app.exec())
