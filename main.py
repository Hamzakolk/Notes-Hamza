import sys
import json
import os
import threading
import time
import winsound
from datetime import datetime
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QFrame, QMessageBox, QInputDialog, QFileDialog,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"

def generate_app_icon():
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([20, 20, 236, 236], radius=50, fill=(59, 130, 246, 255))
        draw.rounded_rectangle([65, 70, 191, 90], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([65, 118, 191, 138], radius=8, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([65, 166, 150, 186], radius=8, fill=(147, 197, 253, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])

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
    padding: 6px 12px;
    color: #CBD5E1;
    font-weight: bold;
}
.ToolBtn:hover {
    background-color: #1F2937;
    color: #FFFFFF;
}
#ContentEditor {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 16px;
    font-size: 15px;
    line-height: 1.6;
}
QComboBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 12px;
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

class NotesHamzaPro(QMainWindow):
    def __init__(self):
        super().__init__()
        generate_app_icon()
        self.setWindowTitle("Notes Hamza Pro - إدارة الملاحظات والمهام")
        self.resize(1360, 820)
        if os.path.exists(ICON_FILE):
            self.setWindowIcon(QIcon(ICON_FILE))

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.data = self.load_data()
        self.current_note_id = None
        self.current_category = "All"
        self.unlocked_notes = set()
        self.nav_buttons = {}

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
                    "title": "مرحباً بك في التصميم الاحترافي الجديد",
                    "category": "Projects",
                    "content": "تم تطوير واجهة Notes Hamza بالكامل لتدعم اللغة العربية بشكل صحيح وتصميم ويندوز 11 الحديث.\n\n• جرب تنسيق النصوص من الشريط بالأعلى\n• أضف مهامك وحدد وقت التنبيه الصوتي\n• احمِ ملاحظاتك السرية بكلمة مرور",
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": "استكشاف الواجهة الجديدة", "done": True, "priority": "High", "reminder": ""},
                        {"text": "إضافة مهمة مع وقت تنبيه", "done": False, "priority": "Medium", "reminder": ""}
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

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 20, 16, 20)
        side_layout.setSpacing(8)

        logo = QLabel("📝  Notes Hamza")
        logo.setObjectName("LogoLabel")
        side_layout.addWidget(logo)

        new_btn = QPushButton("＋  ملاحظة جديدة")
        new_btn.setObjectName("NewNoteBtn")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.create_note)
        side_layout.addWidget(new_btn)
        side_layout.addSpacing(15)

        cats = [
            ("📁   جميع الملاحظات", "All"),
            ("📌   المثبتة بالأعلى", "Pinned"),
            ("🔒   الملاحظات السرية", "Locked"),
            ("🚀   المشاريع", "Projects"),
            ("👤   شخصي", "Personal"),
            ("💼   العمل", "Work"),
            ("💡   أفكار", "Ideas")
        ]
        for text, key in cats:
            btn = QPushButton(text)
            btn.setProperty("class", "NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.set_category(k))
            side_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        side_layout.addStretch()

        export_btn = QPushButton("📤  تصدير الملاحظة")
        export_btn.setProperty("class", "NavBtn")
        export_btn.clicked.connect(self.export_note)
        side_layout.addWidget(export_btn)

        notes_panel = QFrame()
        notes_panel.setObjectName("NotesPanel")
        notes_panel.setFixedWidth(290)
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(14, 20, 14, 14)
        notes_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBox")
        self.search_input.setPlaceholderText("🔍  ابحث في ملاحظاتك...")
        self.search_input.textChanged.connect(self.refresh_notes_list)
        notes_layout.addWidget(self.search_input)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_clicked)
        notes_layout.addWidget(self.notes_list)

        editor_panel = QFrame()
        editor_panel.setObjectName("EditorPanel")
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(24, 20, 24, 16)
        editor_layout.setSpacing(12)

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

        self.lock_btn = QPushButton("🔓 قفل")
        self.lock_btn.setProperty("class", "ToolBtn")
        self.lock_btn.clicked.connect(self.toggle_lock)
        header_row.addWidget(self.lock_btn)

        self.pin_btn = QPushButton("📌 تثبيت")
        self.pin_btn.setProperty("class", "ToolBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        header_row.addWidget(self.pin_btn)

        del_btn = QPushButton("🗑️")
        del_btn.setProperty("class", "ToolBtn")
        del_btn.setStyleSheet("color: #EF4444;")
        del_btn.clicked.connect(self.delete_note)
        header_row.addWidget(del_btn)

        editor_layout.addLayout(header_row)

        format_bar = QFrame()
        format_bar.setObjectName("FormatBar")
        fmt_layout = QHBoxLayout(format_bar)
        fmt_layout.setContentsMargins(10, 6, 10, 6)

        btn_bold = QPushButton("B  عريض")
        btn_bold.setProperty("class", "ToolBtn")
        btn_bold.clicked.connect(self.format_bold)
        fmt_layout.addWidget(btn_bold)

        btn_italic = QPushButton("I  مائل")
        btn_italic.setProperty("class", "ToolBtn")
        btn_italic.clicked.connect(self.format_italic)
        fmt_layout.addWidget(btn_italic)

        btn_bullet = QPushButton("•  نقطة")
        btn_bullet.setProperty("class", "ToolBtn")
        btn_bullet.clicked.connect(lambda: self.editor.insertPlainText("• "))
        fmt_layout.addWidget(btn_bullet)

        btn_time = QPushButton("🕒  إدراج الوقت")
        btn_time.setProperty("class", "ToolBtn")
        btn_time.clicked.connect(lambda: self.editor.insertPlainText(datetime.now().strftime("%Y-%m-%d %H:%M ")))
        fmt_layout.addWidget(btn_time)

        fmt_layout.addStretch()
        editor_layout.addWidget(format_bar)

        self.editor = QTextEdit()
        self.editor.setObjectName("ContentEditor")
        self.editor.setPlaceholderText("ابدأ بكتابة أفكارك وملاحظاتك هنا...")
        self.editor.textChanged.connect(self.auto_save)
        editor_layout.addWidget(self.editor)

        self.stats_label = QLabel("الكلمات: 0   |   الأحرف: 0")
        self.stats_label.setStyleSheet("color: #64748B; font-size: 12px;")
        editor_layout.addWidget(self.stats_label)

        todo_panel = QFrame()
        todo_panel.setObjectName("TodoPanel")
        todo_panel.setFixedWidth(340)
        todo_layout = QVBoxLayout(todo_panel)
        todo_layout.setContentsMargins(18, 20, 18, 18)
        todo_layout.setSpacing(12)

        todo_title = QLabel("✅  قائمة المهام والتنبيهات")
        todo_title.setStyleSheet("font-size: 17px; font-weight: bold;")
        todo_layout.addWidget(todo_title)

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

        add_task_btn = QPushButton("＋ إضافة")
        add_task_btn.setStyleSheet("background-color: #2563EB; border-radius: 8px; padding: 8px 14px; font-weight: bold;")
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
            icons = ("📌 " if n.get("pinned") else "") + ("🔒 " if n.get("password") else "")
            item = QListWidgetItem(f"{icons}{n['title'] or 'بدون عنوان'}\n{n['category']}  •  {n['updated_at']}")
            item.setData(Qt.ItemDataRole.UserRole, n["id"])
            self.notes_list.addItem(item)
            if n["id"] == self.current_note_id:
                item.setSelected(True)

        if not self.current_note_id and notes:
            self.load_note(notes[0]["id"])

    def on_note_clicked(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_note(note_id)

    def load_note(self, note_id):
        note = next((n for n in self.data["notes"] if n["id"] == note_id), None)
        if not note:
            return

        if note.get("password") and note_id not in self.unlocked_notes:
            pwd, ok = QInputDialog.getText(self, "ملاحظة محمية 🔒", "أدخل كلمة المرور:", QLineEdit.EchoMode.Password)
            if not ok or pwd != note["password"]:
                if ok:
                    QMessageBox.warning(self, "خطأ", "كلمة المرور غير صحيحة!")
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_input.blockSignals(True)
        self.editor.blockSignals(True)

        self.title_input.setText(note["title"])
        self.editor.setPlainText(note["content"])
        self.cat_combo.setCurrentText(note.get("category", "Projects"))

        self.lock_btn.setText("🔒 مقفلة" if note.get("password") else "🔓 قفل")
        self.pin_btn.setStyleSheet("color: #3B82F6;" if note.get("pinned") else "")

        self.title_input.blockSignals(False)
        self.editor.blockSignals(False)

        self.update_stats()
        self.refresh_tasks()
        self.refresh_notes_list()

    def create_note(self):
        new_id = str(int(datetime.now().timestamp() * 1000))
        cat = self.current_category if self.current_category not in ["All", "Pinned", "Locked"] else "Projects"
        self.data["notes"].insert(0, {
            "id": new_id, "title": "ملاحظة جديدة", "category": cat,
            "content": "", "pinned": False, "password": "",
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
            pwd, ok = QInputDialog.getText(self, "قفل الملاحظة 🔒", "أدخل كلمة مرور جديدة:", QLineEdit.EchoMode.Password)
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

    def format_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        self.editor.mergeCurrentCharFormat(fmt)

    def format_italic(self):
        self.editor.setFontItalic(not self.editor.fontItalic())

    def export_note(self):
        note = self.get_current_note()
        if not note:
            return
        path, _ = QFileDialog.getSaveFileName(self, "تصدير الملاحظة", f"{note['title']}.md", "Markdown (*.md);;Text (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# {note['title']}\n\n{note['content']}\n\n## المهام:\n")
                for t in note.get("tasks", []):
                    f.write(f"- [{'x' if t['done'] else ' '}] {t['text']} ({t['priority']})\n")
            QMessageBox.information(self, "تم التصدير", "تم حفظ الملاحظة بنجاح!")

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

            rem_str = f"  ⏰ {t['reminder']}" if t.get("reminder") else ""
            cb = QCheckBox(f"{t['text']}{rem_str}")
            cb.setChecked(t["done"])
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_task(i))
            row.addWidget(cb, 1)

            badge = QLabel(t["priority"])
            badge.setStyleSheet(f"color: {colors.get(t['priority'], '#FFF')}; font-weight: bold; font-size: 11px;")
            row.addWidget(badge)

            del_btn = QPushButton("✕")
            del_btn.setStyleSheet("color: #94A3B8; border: none; font-weight: bold;")
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
        QMessageBox.information(self, "⏰ تذكير بمهمة - Notes Hamza", f"حان موعد المهمة:\n\n• {task_text}\n(من ملاحظة: {note_title})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = NotesHamzaPro()
    window.show()
    sys.exit(app.exec())
