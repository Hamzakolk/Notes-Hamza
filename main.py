import sys
import json
import os
import threading
import time
import winsound
import zipfile
import xml.etree.ElementTree as ET
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
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QTextListFormat


def get_app_storage_dir():
    base_dir = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    storage_dir = os.path.join(base_dir, "NotesHamzaStudio")
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


STORAGE_DIR = get_app_storage_dir()
DATA_FILE = os.path.join(STORAGE_DIR, "notes_hamza_data.json")
ICON_FILE = os.path.join(STORAGE_DIR, "icon.ico")

TRANSLATIONS = {
    "ar": {
        "app_title": "Notes Hamza Studio",
        "brand_sub": "Workspace & Keep Sync",
        "new_note": "ملاحظة جديدة",
        "cat_all": "الكل",
        "cat_pinned": "المثبتة",
        "cat_locked": "السرية",
        "cat_projects": "المشاريع",
        "cat_personal": "شخصي",
        "cat_work": "العمل",
        "cat_ideas": "أفكار",
        "sync_keep": "مزامنة Google Keep",
        "syncing": "جاري المزامنة...",
        "keep_settings": "إعدادات Keep",
        "open_file": "فتح ملف",
        "open_file_tip": "فتح ملف (.txt, .eml, .msg, .docx)",
        "export_note": "تصدير الملاحظة",
        "keep_not_synced": "لم تتم المزامنة بعد",
        "keep_prefix": "Keep:",
        "search_placeholder": "بحث سريع في الملاحظات...",
        "title_placeholder": "عنوان الملاحظة...",
        "floating": "عائم",
        "floating_tip": "فتح في نافذة عائمة",
        "lock": "قفل",
        "locked": "مقفلة",
        "pin": "تثبيت",
        "delete_tip": "حذف الملاحظة",
        "bold_tip": "عريض",
        "italic_tip": "مائل",
        "underline_tip": "تسطير",
        "text_color_tip": "لون النص",
        "highlight_tip": "تظليل",
        "bullet_tip": "قائمة",
        "align_right_tip": "يمين",
        "align_left_tip": "يسار",
        "select_all_tip": "تحديد الكل",
        "copy_all_tip": "نسخ الملاحظة كاملة",
        "editor_placeholder": "اكتب ملاحظتك هنا...",
        "stats": "الكلمات: {words}  |  الأحرف: {chars}",
        "tasks_header": "المهام والتنبيهات",
        "progress": "الإنجاز: {pct}% ({done}/{total})",
        "progress_zero": "الإنجاز: 0%",
        "task_placeholder": "مهمة جديدة ثم Enter...",
        "reminder_placeholder": "HH:MM",
        "add_task": "إضافة",
        "plus_15m": "+15 دقيقة",
        "plus_1h": "+1 ساعة",
        "ready": "جاهز للعمل",
        "untitled": "بدون عنوان",
        "no_content": "بدون محتوى",
        "locked_note_snippet": "ملاحظة مقفلة بكلمة مرور",
        "keep_tag": "Keep",
        "welcome_title": "أهلاً بك في Notes Hamza Studio",
        "welcome_content": "واجهة أنيقة ومرتبة لإدارة الملاحظات والمهام مع دعم مزامنة Google Keep.",
        "welcome_task": "إعداد بيانات Google Keep",
        "theme_dark": "داكن أنيق",
        "theme_midnight": "أزرق منتصف الليل",
        "theme_emerald": "زمردي هادئ",
        "theme_cream": "ورقة دافئة (Cream)",
        "theme_white": "أبيض ناصع",
        "theme_sticky": "استيكر أصفر مسطر (Sticky)",
        "lang_label": "اللغة:",
        "lang_ar": "العربية",
        "lang_en": "English",
        "status_reminder_set": "تم ضبط وقت التنبيه على {time}",
        "status_settings_saved": "تم حفظ إعدادات Google Keep",
        "missing_gkeep_title": "مكتبة مفقودة",
        "missing_gkeep_msg": "مكتبة gkeepapi غير مثبتة في بيئة التشغيل.\nثبتها عبر: pip install gkeepapi",
        "status_missing_gkeep": "مكتبة gkeepapi غير مثبتة في هذه البيئة",
        "status_syncing": "جاري مزامنة الملاحظات مع Google Keep...",
        "status_synced": "تمت مزامنة Google Keep ({time})",
        "status_sync_fail": "تعذرت المزامنة: {err}",
        "sync_err_title": "خطأ المزامنة",
        "status_theme_changed": "تم تغيير مظهر الصفحة إلى: {theme}",
        "status_float_opened": "تم فتح الملاحظة في نافذة عائمة",
        "status_selected_all": "تم تحديد نص الملاحظة بالكامل",
        "status_nothing_to_copy": "لا يوجد محتوى لنسخه",
        "status_copied_all": "تم نسخ الملاحظة كاملة إلى الحافظة",
        "status_file_opened": "تم فتح الملف: {name}",
        "status_file_open_fail": "تعذر فتح الملف: {err}",
        "enter_password_title": "ملاحظة مقفلة",
        "enter_password_prompt": "أدخل كلمة المرور:",
        "wrong_password": "كلمة المرور غير صحيحة",
        "status_note_created": "تم إنشاء ملاحظة جديدة",
        "status_auto_saved": "تم الحفظ تلقائياً",
        "status_pin_updated": "تم تحديث حالة التثبيت",
        "unlock_title": "إزالة القفل",
        "unlock_prompt": "إزالة كلمة المرور؟",
        "status_unlocked": "تم إزالة القفل عن الملاحظة",
        "lock_title": "قفل الملاحظة",
        "lock_prompt": "أدخل كلمة مرور:",
        "status_locked": "تم قفل الملاحظة بكلمة مرور",
        "delete_title": "حذف",
        "delete_prompt": "حذف هذه الملاحظة نهائياً؟",
        "status_deleted": "تم حذف الملاحظة",
        "export_title": "تصدير",
        "status_exported": "تم تصدير الملاحظة إلى: {name}",
        "status_bad_time": "صيغة التنبيه يجب أن تكون HH:MM مثل 21:30",
        "status_task_added": "تمت إضافة المهمة",
        "alarm_title": "تذكير",
        "alarm_body": "المهمة: {task}\nالملاحظة: {note}",
        "keep_dlg_title": "إعدادات مزامنة Google Keep",
        "keep_dlg_info": "أدخل بريد Gmail و Master Token الخاص بحساب Google Keep.\nالمزامنة تعمل في الخلفية دون تعطيل عمل التطبيق محلياً.",
        "keep_dlg_email": "البريد الإلكتروني:",
        "keep_dlg_token": "Master Token:",
        "keep_dlg_auto": "مزامنة تلقائية كل 5 دقائق",
        "save": "حفظ",
        "cancel": "إلغاء",
        "keep_default_title": "ملاحظة من Keep",
        "keep_synced_prefix": "تمت {time}"
    },
    "en": {
        "app_title": "Notes Hamza Studio",
        "brand_sub": "Workspace & Keep Sync",
        "new_note": "New Note",
        "cat_all": "All Notes",
        "cat_pinned": "Pinned",
        "cat_locked": "Locked",
        "cat_projects": "Projects",
        "cat_personal": "Personal",
        "cat_work": "Work",
        "cat_ideas": "Ideas",
        "sync_keep": "Sync Google Keep",
        "syncing": "Syncing...",
        "keep_settings": "Keep Settings",
        "open_file": "Open File",
        "open_file_tip": "Open file (.txt, .eml, .msg, .docx)",
        "export_note": "Export Note",
        "keep_not_synced": "Not synced yet",
        "keep_prefix": "Keep:",
        "search_placeholder": "Quick search notes...",
        "title_placeholder": "Note title...",
        "floating": "Float",
        "floating_tip": "Open in floating window",
        "lock": "Lock",
        "locked": "Locked",
        "pin": "Pin",
        "delete_tip": "Delete note",
        "bold_tip": "Bold",
        "italic_tip": "Italic",
        "underline_tip": "Underline",
        "text_color_tip": "Text Color",
        "highlight_tip": "Highlight",
        "bullet_tip": "Bullet List",
        "align_right_tip": "Align Right",
        "align_left_tip": "Align Left",
        "select_all_tip": "Select All",
        "copy_all_tip": "Copy Entire Note",
        "editor_placeholder": "Write your note here...",
        "stats": "Words: {words}  |  Characters: {chars}",
        "tasks_header": "Tasks & Reminders",
        "progress": "Progress: {pct}% ({done}/{total})",
        "progress_zero": "Progress: 0%",
        "task_placeholder": "New task, press Enter...",
        "reminder_placeholder": "HH:MM",
        "add_task": "Add",
        "plus_15m": "+15 min",
        "plus_1h": "+1 hour",
        "ready": "Ready",
        "untitled": "Untitled",
        "no_content": "No content",
        "locked_note_snippet": "Password-protected note",
        "keep_tag": "Keep",
        "welcome_title": "Welcome to Notes Hamza Studio",
        "welcome_content": "A clean workspace for notes and tasks with Google Keep sync support.",
        "welcome_task": "Configure Google Keep credentials",
        "theme_dark": "Elegant Dark",
        "theme_midnight": "Midnight Blue",
        "theme_emerald": "Calm Emerald",
        "theme_cream": "Warm Cream",
        "theme_white": "Pure White",
        "theme_sticky": "Yellow Ruled Sticky",
        "lang_label": "Language:",
        "lang_ar": "العربية",
        "lang_en": "English",
        "status_reminder_set": "Reminder time set to {time}",
        "status_settings_saved": "Google Keep settings saved",
        "missing_gkeep_title": "Missing Dependency",
        "missing_gkeep_msg": "gkeepapi is not installed in this environment.\nInstall it via: pip install gkeepapi",
        "status_missing_gkeep": "gkeepapi is not installed",
        "status_syncing": "Syncing notes with Google Keep...",
        "status_synced": "Synced with Google Keep ({time})",
        "status_sync_fail": "Sync failed: {err}",
        "sync_err_title": "Sync Error",
        "status_theme_changed": "Page theme changed to: {theme}",
        "status_float_opened": "Opened note in floating window",
        "status_selected_all": "Selected entire note text",
        "status_nothing_to_copy": "Nothing to copy",
        "status_copied_all": "Copied full note to clipboard",
        "status_file_opened": "Opened file: {name}",
        "status_file_open_fail": "Failed to open file: {err}",
        "enter_password_title": "Locked Note",
        "enter_password_prompt": "Enter password:",
        "wrong_password": "Incorrect password",
        "status_note_created": "Created a new note",
        "status_auto_saved": "Auto-saved",
        "status_pin_updated": "Updated pin state",
        "unlock_title": "Remove Lock",
        "unlock_prompt": "Remove password protection?",
        "status_unlocked": "Note unlocked",
        "lock_title": "Lock Note",
        "lock_prompt": "Enter password:",
        "status_locked": "Note locked with password",
        "delete_title": "Delete",
        "delete_prompt": "Delete this note permanently?",
        "status_deleted": "Note deleted",
        "export_title": "Export",
        "status_exported": "Exported note to: {name}",
        "status_bad_time": "Reminder time must be HH:MM (e.g. 21:30)",
        "status_task_added": "Task added",
        "alarm_title": "Reminder",
        "alarm_body": "Task: {task}\nNote: {note}",
        "keep_dlg_title": "Google Keep Sync Settings",
        "keep_dlg_info": "Enter your Gmail address and Google Keep Master Token.\nSync runs in the background without blocking local usage.",
        "keep_dlg_email": "Email:",
        "keep_dlg_token": "Master Token:",
        "keep_dlg_auto": "Auto-sync every 5 minutes",
        "save": "Save",
        "cancel": "Cancel",
        "keep_default_title": "Note from Keep",
        "keep_synced_prefix": "Synced {time}"
    }
}


def generate_app_icon():
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (17, 24, 39, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([18, 18, 238, 238], radius=56, fill=(79, 70, 229, 255))
        draw.rounded_rectangle([64, 72, 192, 90], radius=9, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([64, 119, 192, 137], radius=9, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([64, 166, 148, 184], radius=9, fill=(199, 210, 254, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])


def get_page_themes(lang="ar"):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
    return {
        t["theme_dark"]: {"bg": "#141A29", "fg": "#F1F5F9", "border": "#263148", "ruled": False},
        t["theme_midnight"]: {"bg": "#0D1B2A", "fg": "#E0E1DD", "border": "#1B263B", "ruled": False},
        t["theme_emerald"]: {"bg": "#0B2520", "fg": "#E6F4F1", "border": "#19433B", "ruled": False},
        t["theme_cream"]: {"bg": "#FBF7E9", "fg": "#1E293B", "border": "#E6DEC3", "ruled": False},
        t["theme_white"]: {"bg": "#FFFFFF", "fg": "#0F172A", "border": "#E2E8F0", "ruled": False},
        t["theme_sticky"]: {
            "bg": "#FFFBEB",
            "fg": "#292524",
            "border": "#FDE68A",
            "ruled": True,
            "line": "#F3E8B4"
        }
    }


def get_stylesheet(lang="ar"):
    align = "right" if lang == "ar" else "left"
    border_side = "border-left" if lang == "ar" else "border-right"
    opp_border_side = "border-right" if lang == "ar" else "border-left"
    active_border = "border-right" if lang == "ar" else "border-left"
    return f"""
QMainWindow {{
    background-color: #0B0F1A;
}}
QWidget {{
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Tahoma', Arial;
    font-size: 13.5px;
}}
#Sidebar {{
    background-color: #101624;
    {border_side}: 1px solid #1E293B;
}}
#BrandTitle {{
    font-size: 19px;
    font-weight: 700;
    color: #F8FAFC;
}}
#BrandSub {{
    font-size: 11.5px;
    color: #818CF8;
}}
#PrimaryBtn {{
    background-color: #4F46E5;
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13.5px;
}}
#PrimaryBtn:hover {{
    background-color: #4338CA;
}}
#SyncBtn {{
    background-color: #162033;
    color: #E2E8F0;
    border: 1px solid #2A3A55;
    border-radius: 10px;
    padding: 9px 12px;
    font-weight: 600;
}}
#SyncBtn:hover {{
    background-color: #1E2D47;
    border-color: #6366F1;
}}
.NavItem {{
    background-color: transparent;
    text-align: {align};
    padding: 9px 12px;
    border-radius: 9px;
    color: #94A3B8;
    font-weight: 600;
    border: none;
}}
.NavItem:hover {{
    background-color: #172033;
    color: #F8FAFC;
}}
.NavItem[active="true"] {{
    background-color: rgba(79, 70, 229, 0.18);
    color: #A5B4FC;
    {active_border}: 3px solid #6366F1;
}}
#NotesListPanel {{
    background-color: #0E1422;
    {border_side}: 1px solid #1E293B;
}}
QLineEdit {{
    background-color: #151E30;
    border: 1px solid #26334D;
    border-radius: 9px;
    padding: 8px 12px;
    color: #F8FAFC;
    selection-background-color: #4F46E5;
}}
QLineEdit:focus {{
    border-color: #6366F1;
}}
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
}}
QListWidget::item {{
    background-color: #141C2E;
    border: 1px solid #1E293B;
    border-radius: 11px;
    padding: 11px 12px;
    margin-bottom: 8px;
}}
QListWidget::item:hover {{
    background-color: #19243B;
    border-color: #334155;
}}
QListWidget::item:selected {{
    background-color: rgba(79, 70, 229, 0.16);
    border-color: #6366F1;
}}
#EditorContainer {{
    background-color: #0B0F1A;
}}
#NoteTitleEdit {{
    background-color: transparent;
    border: none;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    padding: 4px 6px;
}}
#NoteTitleEdit:focus {{
    background-color: #121929;
    border-radius: 8px;
}}
#ToolbarCard {{
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
}}
.IconActionBtn {{
    background-color: #172033;
    border: 1px solid #26334D;
    border-radius: 8px;
    padding: 6px 9px;
    color: #CBD5E1;
    font-weight: 600;
}}
.IconActionBtn:hover {{
    background-color: #22304C;
    color: #FFFFFF;
    border-color: #475569;
}}
.QuickTimeBtn {{
    background-color: #182236;
    border: 1px solid #2A3A55;
    border-radius: 7px;
    padding: 4px 8px;
    color: #93C5FD;
    font-size: 11.5px;
    font-weight: 600;
}}
.QuickTimeBtn:hover {{
    background-color: #23324E;
}}
QComboBox, QFontComboBox {{
    background-color: #172033;
    border: 1px solid #26334D;
    border-radius: 8px;
    padding: 5px 8px;
    color: #F1F5F9;
}}
QComboBox:hover, QFontComboBox:hover {{
    border-color: #6366F1;
}}
QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {{
    background-color: #131B2C;
    color: #F1F5F9;
    selection-background-color: #4F46E5;
    border: 1px solid #26334D;
}}
#TasksPanel {{
    background-color: #101624;
    {opp_border_side}: 1px solid #1E293B;
}}
QProgressBar {{
    background-color: #1A2438;
    border: none;
    border-radius: 5px;
    height: 7px;
}}
QProgressBar::chunk {{
    background-color: #10B981;
    border-radius: 5px;
}}
.TaskRowCard {{
    background-color: #151E30;
    border: 1px solid #23304A;
    border-radius: 10px;
}}
.TaskRowCard:hover {{
    border-color: #334155;
}}
QStatusBar {{
    background-color: #0E1422;
    color: #94A3B8;
    border-top: 1px solid #1E293B;
    font-size: 12px;
}}
"""


class WorkerSignaler(QObject):
    alarm_triggered = pyqtSignal(str, str)
    sync_finished = pyqtSignal(bool, str)


class KeepSettingsDialog(QDialog):
    def __init__(self, keep_cfg, lang="ar", parent=None):
        super().__init__(parent)
        t = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
        self.setWindowTitle(t["keep_dlg_title"])
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if lang == "ar" else Qt.LayoutDirection.LeftToRight)
        self.resize(440, 230)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(t["keep_dlg_info"])
        info.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(info)

        form = QFormLayout()
        self.email_edit = QLineEdit(keep_cfg.get("email", ""))
        self.email_edit.setPlaceholderText("example@gmail.com")

        self.token_edit = QLineEdit(keep_cfg.get("master_token", ""))
        self.token_edit.setPlaceholderText("aas_et/...")
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.auto_sync_cb = QCheckBox(t["keep_dlg_auto"])
        self.auto_sync_cb.setChecked(keep_cfg.get("auto_sync", False))

        form.addRow(t["keep_dlg_email"], self.email_edit)
        form.addRow(t["keep_dlg_token"], self.token_edit)
        form.addRow("", self.auto_sync_cb)
        layout.addLayout(form)

        btns = QHBoxLayout()
        save_btn = QPushButton(t["save"])
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton(t["cancel"])
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
        lang = parent_app.lang
        t = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
        themes = get_page_themes(lang)

        self.setWindowTitle(f"{note.get('title') or t['untitled']} - {t['app_title']}")
        self.resize(480, 440)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if lang == "ar" else Qt.LayoutDirection.LeftToRight)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        lbl = QLabel(note.get("title") or t["untitled"])
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #818CF8;")
        layout.addWidget(lbl)

        self.editor = QTextEdit()
        first_theme = next(iter(themes.values()))
        theme = themes.get(note.get("theme", ""), first_theme)
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
        self.data = self.load_data()
        self.lang = self.data.get("language", "ar")
        if self.lang not in TRANSLATIONS:
            self.lang = "ar"

        self.resize(1420, 860)
        if os.path.exists(ICON_FILE):
            self.setWindowIcon(QIcon(ICON_FILE))

        self.current_note_id = None
        self.current_category = "All"
        self.unlocked_notes = set()
        self.nav_buttons = {}
        self.floating_windows = []
        self.is_syncing = False

        self.signaler = WorkerSignaler()
        self.signaler.alarm_triggered.connect(self.show_alarm_popup)
        self.signaler.sync_finished.connect(self.on_sync_finished)

        self.apply_language_direction()
        self.build_ui()
        self.refresh_notes_list()

        threading.Thread(target=self.reminder_worker, daemon=True).start()
        threading.Thread(target=self.auto_keep_worker, daemon=True).start()

    def tr(self, key, **kwargs):
        template = TRANSLATIONS.get(self.lang, TRANSLATIONS["ar"]).get(key, key)
        return template.format(**kwargs) if kwargs else template

    def apply_language_direction(self):
        is_ar = self.lang == "ar"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_ar else Qt.LayoutDirection.LeftToRight)
        if QApplication.instance():
            QApplication.instance().setLayoutDirection(
                Qt.LayoutDirection.RightToLeft if is_ar else Qt.LayoutDirection.LeftToRight
            )
            QApplication.instance().setStyleSheet(get_stylesheet(self.lang))
        self.setWindowTitle(self.tr("app_title"))

    def set_status(self, msg, timeout=4000):
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(msg, timeout)

    def load_data(self):
        default_t = TRANSLATIONS["ar"]
        default_data = {
            "language": "ar",
            "keep": {
                "email": "",
                "master_token": "",
                "auto_sync": False,
                "last_sync": default_t["keep_not_synced"]
            },
            "notes": [
                {
                    "id": "1",
                    "keep_id": "",
                    "title": default_t["welcome_title"],
                    "category": "Projects",
                    "content": default_t["welcome_content"],
                    "html": "",
                    "theme": default_t["theme_dark"],
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": default_t["welcome_task"], "done": False, "priority": "High", "reminder": "", "alerted": False}
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
                        loaded.setdefault("language", "ar")
                        return loaded
            except Exception:
                pass
        return default_data

    def save_data(self):
        self.data["language"] = self.lang
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def change_language(self, lang_code):
        if lang_code not in TRANSLATIONS or lang_code == self.lang:
            return
        self.lang = lang_code
        self.save_data()
        self.apply_language_direction()
        saved_note_id = self.current_note_id
        self.current_note_id = None
        self.nav_buttons.clear()
        self.build_ui()
        if saved_note_id and any(n["id"] == saved_note_id for n in self.data["notes"]):
            self.load_note(saved_note_id)
        else:
            self.refresh_notes_list()
        self.set_status(self.tr("ready"), 2500)

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1) القائمة الجانبية
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(235)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(14, 18, 14, 18)
        side_lay.setSpacing(6)

        brand_box = QVBoxLayout()
        brand_box.setContentsMargins(6, 0, 6, 8)
        title_lbl = QLabel(self.tr("app_title"))
        title_lbl.setObjectName("BrandTitle")
        sub_lbl = QLabel(self.tr("brand_sub"))
        sub_lbl.setObjectName("BrandSub")
        brand_box.addWidget(title_lbl)
        brand_box.addWidget(sub_lbl)
        side_lay.addLayout(brand_box)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)
        lang_lbl = QLabel(self.tr("lang_label"))
        lang_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(self.tr("lang_ar"), "ar")
        self.lang_combo.addItem(self.tr("lang_en"), "en")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(
            lambda _: self.change_language(self.lang_combo.currentData())
        )
        lang_row.addWidget(lang_lbl)
        lang_row.addWidget(self.lang_combo, 1)
        side_lay.addLayout(lang_row)

        self.new_note_btn = QPushButton(qta.icon("fa5s.plus", color="#FFFFFF"), f"  {self.tr('new_note')}")
        self.new_note_btn.setObjectName("PrimaryBtn")
        self.new_note_btn.clicked.connect(self.create_new_note)
        side_lay.addWidget(self.new_note_btn)

        categories = [
            ("All", "cat_all", "fa5s.layer-group"),
            ("Pinned", "cat_pinned", "fa5s.thumbtack"),
            ("Locked", "cat_locked", "fa5s.lock"),
            ("Projects", "cat_projects", "fa5s.folder"),
            ("Personal", "cat_personal", "fa5s.user"),
            ("Work", "cat_work", "fa5s.briefcase"),
            ("Ideas", "cat_ideas", "fa5s.lightbulb"),
        ]
        for cat_key, label_key, icon_name in categories:
            btn = QPushButton(qta.icon(icon_name, color="#94A3B8"), f"  {self.tr(label_key)}")
            btn.setProperty("class", "NavItem")
            btn.setProperty("active", "true" if cat_key == self.current_category else "false")
            btn.clicked.connect(lambda _, c=cat_key: self.select_category(c))
            self.nav_buttons[cat_key] = btn
            side_lay.addWidget(btn)

        side_lay.addStretch()

        self.sync_btn = QPushButton(qta.icon("fa5s.sync", color="#818CF8"), f"  {self.tr('sync_keep')}")
        self.sync_btn.setObjectName("SyncBtn")
        self.sync_btn.clicked.connect(self.start_keep_sync)
        side_lay.addWidget(self.sync_btn)

        self.keep_settings_btn = QPushButton(qta.icon("fa5s.cog", color="#94A3B8"), f"  {self.tr('keep_settings')}")
        self.keep_settings_btn.setProperty("class", "IconActionBtn")
        self.keep_settings_btn.clicked.connect(self.open_keep_settings)
        side_lay.addWidget(self.keep_settings_btn)

        self.keep_status_lbl = QLabel(self.data.get("keep", {}).get("last_sync") or self.tr("keep_not_synced"))
        self.keep_status_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        self.keep_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_lay.addWidget(self.keep_status_lbl)

        open_file_btn = QPushButton(qta.icon("fa5s.folder-open", color="#CBD5E1"), f"  {self.tr('open_file')}")
        open_file_btn.setProperty("class", "IconActionBtn")
        open_file_btn.setToolTip(self.tr("open_file_tip"))
        open_file_btn.clicked.connect(self.open_external_file)
        side_lay.addWidget(open_file_btn)

        export_btn = QPushButton(qta.icon("fa5s.file-export", color="#CBD5E1"), f"  {self.tr('export_note')}")
        export_btn.setProperty("class", "IconActionBtn")
        export_btn.clicked.connect(self.export_current_note)
        side_lay.addWidget(export_btn)

        root_layout.addWidget(sidebar)

        # 2) قائمة الملاحظات
        list_panel = QFrame()
        list_panel.setObjectName("NotesListPanel")
        list_panel.setFixedWidth(290)
        list_lay = QVBoxLayout(list_panel)
        list_lay.setContentsMargins(12, 16, 12, 14)
        list_lay.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.tr("search_placeholder"))
        self.search_input.textChanged.connect(self.refresh_notes_list)
        list_lay.addWidget(self.search_input)

        self.notes_list = QListWidget()
        self.notes_list.currentItemChanged.connect(self.on_note_selected)
        list_lay.addWidget(self.notes_list)

        root_layout.addWidget(list_panel)

        # 3) منطقة المحرر
        editor_panel = QFrame()
        editor_panel.setObjectName("EditorContainer")
        ed_lay = QVBoxLayout(editor_panel)
        ed_lay.setContentsMargins(18, 16, 18, 14)
        ed_lay.setSpacing(10)

        top_bar = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("NoteTitleEdit")
        self.title_edit.setPlaceholderText(self.tr("title_placeholder"))
        self.title_edit.textChanged.connect(self.on_note_edited)
        top_bar.addWidget(self.title_edit, 1)

        self.cat_combo = QComboBox()
        for c_key, t_key in [
            ("Projects", "cat_projects"),
            ("Personal", "cat_personal"),
            ("Work", "cat_work"),
            ("Ideas", "cat_ideas"),
        ]:
            self.cat_combo.addItem(self.tr(t_key), c_key)
        self.cat_combo.currentIndexChanged.connect(self.on_note_edited)
        top_bar.addWidget(self.cat_combo)

        self.float_btn = QPushButton(qta.icon("fa5s.external-link-alt", color="#93C5FD"), f" {self.tr('floating')}")
        self.float_btn.setProperty("class", "IconActionBtn")
        self.float_btn.setToolTip(self.tr("floating_tip"))
        self.float_btn.clicked.connect(self.open_floating_note)
        top_bar.addWidget(self.float_btn)

        self.pin_btn = QPushButton(qta.icon("fa5s.thumbtack", color="#FBBF24"), f" {self.tr('pin')}")
        self.pin_btn.setProperty("class", "IconActionBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        top_bar.addWidget(self.pin_btn)

        self.lock_btn = QPushButton(qta.icon("fa5s.lock", color="#F87171"), f" {self.tr('lock')}")
        self.lock_btn.setProperty("class", "IconActionBtn")
        self.lock_btn.clicked.connect(self.toggle_lock)
        top_bar.addWidget(self.lock_btn)

        del_btn = QPushButton(qta.icon("fa5s.trash-alt", color="#EF4444"))
        del_btn.setProperty("class", "IconActionBtn")
        del_btn.setToolTip(self.tr("delete_tip"))
        del_btn.clicked.connect(self.delete_current_note)
        top_bar.addWidget(del_btn)

        ed_lay.addLayout(top_bar)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("ToolbarCard")
        tb_lay = QHBoxLayout(toolbar_card)
        tb_lay.setContentsMargins(10, 7, 10, 7)
        tb_lay.setSpacing(6)

        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(155)
        self.font_combo.currentFontChanged.connect(lambda f: self.editor.setCurrentFont(f))
        tb_lay.addWidget(self.font_combo)

        self.size_combo = QComboBox()
        for sz in ["11", "12", "14", "16", "18", "22", "26"]:
            self.size_combo.addItem(sz)
        self.size_combo.setCurrentText("14")
        self.size_combo.setMaximumWidth(65)
        self.size_combo.currentTextChanged.connect(lambda s: self.editor.setFontPointSize(float(s)))
        tb_lay.addWidget(self.size_combo)

        self.theme_combo = QComboBox()
        for t_name in get_page_themes(self.lang).keys():
            self.theme_combo.addItem(t_name)
        self.theme_combo.currentTextChanged.connect(self.apply_page_theme)
        tb_lay.addWidget(self.theme_combo)

        bold_btn = QPushButton(qta.icon("fa5s.bold", color="#E2E8F0"))
        bold_btn.setProperty("class", "IconActionBtn")
        bold_btn.setToolTip(self.tr("bold_tip"))
        bold_btn.clicked.connect(self.toggle_bold)
        tb_lay.addWidget(bold_btn)

        italic_btn = QPushButton(qta.icon("fa5s.italic", color="#E2E8F0"))
        italic_btn.setProperty("class", "IconActionBtn")
        italic_btn.setToolTip(self.tr("italic_tip"))
        italic_btn.clicked.connect(self.toggle_italic)
        tb_lay.addWidget(italic_btn)

        underline_btn = QPushButton(qta.icon("fa5s.underline", color="#E2E8F0"))
        underline_btn.setProperty("class", "IconActionBtn")
        underline_btn.setToolTip(self.tr("underline_tip"))
        underline_btn.clicked.connect(self.toggle_underline)
        tb_lay.addWidget(underline_btn)

        color_btn = QPushButton(qta.icon("fa5s.palette", color="#38BDF8"))
        color_btn.setProperty("class", "IconActionBtn")
        color_btn.setToolTip(self.tr("text_color_tip"))
        color_btn.clicked.connect(self.choose_text_color)
        tb_lay.addWidget(color_btn)

        hi_btn = QPushButton(qta.icon("fa5s.highlighter", color="#FACC15"))
        hi_btn.setProperty("class", "IconActionBtn")
        hi_btn.setToolTip(self.tr("highlight_tip"))
        hi_btn.clicked.connect(self.choose_highlight_color)
        tb_lay.addWidget(hi_btn)

        bullet_btn = QPushButton(qta.icon("fa5s.list-ul", color="#CBD5E1"))
        bullet_btn.setProperty("class", "IconActionBtn")
        bullet_btn.setToolTip(self.tr("bullet_tip"))
        bullet_btn.clicked.connect(self.insert_bullet_list)
        tb_lay.addWidget(bullet_btn)

        align_r_btn = QPushButton(qta.icon("fa5s.align-right", color="#CBD5E1"))
        align_r_btn.setProperty("class", "IconActionBtn")
        align_r_btn.setToolTip(self.tr("align_right_tip"))
        align_r_btn.clicked.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        tb_lay.addWidget(align_r_btn)

        align_l_btn = QPushButton(qta.icon("fa5s.align-left", color="#CBD5E1"))
        align_l_btn.setProperty("class", "IconActionBtn")
        align_l_btn.setToolTip(self.tr("align_left_tip"))
        align_l_btn.clicked.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        tb_lay.addWidget(align_l_btn)

        sel_all_btn = QPushButton(qta.icon("fa5s.check-double", color="#A5B4FC"))
        sel_all_btn.setProperty("class", "IconActionBtn")
        sel_all_btn.setToolTip(self.tr("select_all_tip"))
        sel_all_btn.clicked.connect(self.select_all_editor)
        tb_lay.addWidget(sel_all_btn)

        copy_all_btn = QPushButton(qta.icon("fa5s.copy", color="#34D399"))
        copy_all_btn.setProperty("class", "IconActionBtn")
        copy_all_btn.setToolTip(self.tr("copy_all_tip"))
        copy_all_btn.clicked.connect(self.copy_all_editor)
        tb_lay.addWidget(copy_all_btn)

        tb_lay.addStretch()
        ed_lay.addWidget(toolbar_card)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(self.tr("editor_placeholder"))
        self.editor.textChanged.connect(self.on_note_edited)
        ed_lay.addWidget(self.editor, 1)

        self.stats_lbl = QLabel(self.tr("stats", words=0, chars=0))
        self.stats_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        ed_lay.addWidget(self.stats_lbl)

        root_layout.addWidget(editor_panel, 1)

        # 4) لوحة المهام والتنبيهات
        tasks_panel = QFrame()
        tasks_panel.setObjectName("TasksPanel")
        tasks_panel.setFixedWidth(300)
        tasks_lay = QVBoxLayout(tasks_panel)
        tasks_lay.setContentsMargins(14, 16, 14, 14)
        tasks_lay.setSpacing(10)

        tasks_title = QLabel(self.tr("tasks_header"))
        tasks_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        tasks_lay.addWidget(tasks_title)

        self.progress_lbl = QLabel(self.tr("progress_zero"))
        self.progress_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        tasks_lay.addWidget(self.progress_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        tasks_lay.addWidget(self.progress_bar)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText(self.tr("task_placeholder"))
        self.task_input.returnPressed.connect(self.add_task)
        tasks_lay.addWidget(self.task_input)

        rem_row = QHBoxLayout()
        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText(self.tr("reminder_placeholder"))
        self.reminder_input.setMaximumWidth(95)
        rem_row.addWidget(self.reminder_input)

        plus_15_btn = QPushButton(self.tr("plus_15m"))
        plus_15_btn.setProperty("class", "QuickTimeBtn")
        plus_15_btn.clicked.connect(lambda: self.set_quick_reminder(15))
        rem_row.addWidget(plus_15_btn)

        plus_1h_btn = QPushButton(self.tr("plus_1h"))
        plus_1h_btn.setProperty("class", "QuickTimeBtn")
        plus_1h_btn.clicked.connect(lambda: self.set_quick_reminder(60))
        rem_row.addWidget(plus_1h_btn)

        tasks_lay.addLayout(rem_row)

        add_task_btn = QPushButton(qta.icon("fa5s.plus-circle", color="#FFFFFF"), f"  {self.tr('add_task')}")
        add_task_btn.setObjectName("PrimaryBtn")
        add_task_btn.clicked.connect(self.add_task)
        tasks_lay.addWidget(add_task_btn)

        self.tasks_list = QListWidget()
        tasks_lay.addWidget(self.tasks_list, 1)

        root_layout.addWidget(tasks_panel)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.set_status(self.tr("ready"), 2500)

    def get_current_note(self):
        for n in self.data.get("notes", []):
            if n["id"] == self.current_note_id:
                return n
        return None

    def select_category(self, category):
        self.current_category = category
        for key, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if key == category else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.refresh_notes_list()

    def refresh_notes_list(self):
        query = self.search_input.text().strip().lower() if hasattr(self, "search_input") else ""
        self.notes_list.blockSignals(True)
        self.notes_list.clear()

        notes = self.data.get("notes", [])
        notes_sorted = sorted(notes, key=lambda x: not x.get("pinned", False))

        for n in notes_sorted:
            cat = n.get("category", "Projects")
            is_pinned = bool(n.get("pinned", False))
            is_locked = bool(n.get("password", ""))

            if self.current_category == "Pinned" and not is_pinned:
                continue
            if self.current_category == "Locked" and not is_locked:
                continue
            if self.current_category not in ("All", "Pinned", "Locked") and cat != self.current_category:
                continue

            title = n.get("title") or self.tr("untitled")
            snippet = self.tr("locked_note_snippet") if (is_locked and n["id"] not in self.unlocked_notes) else (n.get("content") or self.tr("no_content"))
            snippet_clean = " ".join(snippet.split())[:70]

            if query and query not in title.lower() and query not in snippet_clean.lower():
                continue

            prefix = ""
            if is_pinned:
                prefix += "📌 "
            if is_locked:
                prefix += "🔒 "
            if n.get("keep_id"):
                prefix += f"[{self.tr('keep_tag')}] "

            item = QListWidgetItem(f"{prefix}{title}\n{snippet_clean}")
            item.setData(Qt.ItemDataRole.UserRole, n["id"])
            self.notes_list.addItem(item)
            if n["id"] == self.current_note_id:
                self.notes_list.setCurrentItem(item)

        self.notes_list.blockSignals(False)
        if self.notes_list.count() > 0 and not self.get_current_note():
            self.notes_list.setCurrentRow(0)
        elif self.notes_list.count() == 0:
            self.current_note_id = None
            self.clear_editor_and_tasks()

    def clear_editor_and_tasks(self):
        self.title_edit.blockSignals(True)
        self.editor.blockSignals(True)
        self.title_edit.clear()
        self.editor.clear()
        self.title_edit.blockSignals(False)
        self.editor.blockSignals(False)
        self.tasks_list.clear()
        self.update_stats()
        self.update_tasks_progress()

    def on_note_selected(self, current, _previous):
        if not current:
            return
        note_id = current.data(Qt.ItemDataRole.UserRole)
        self.load_note(note_id)

    def load_note(self, note_id):
        note = next((n for n in self.data.get("notes", []) if n["id"] == note_id), None)
        if not note:
            return

        if note.get("password") and note_id not in self.unlocked_notes:
            pwd, ok = QInputDialog.getText(
                self,
                self.tr("enter_password_title"),
                self.tr("enter_password_prompt"),
                QLineEdit.EchoMode.Password
            )
            if not ok:
                return
            if pwd != note["password"]:
                QMessageBox.warning(self, self.tr("enter_password_title"), self.tr("wrong_password"))
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_edit.blockSignals(True)
        self.editor.blockSignals(True)
        self.cat_combo.blockSignals(True)
        self.theme_combo.blockSignals(True)

        self.title_edit.setText(note.get("title", ""))
        c_idx = self.cat_combo.findData(note.get("category", "Projects"))
        if c_idx >= 0:
            self.cat_combo.setCurrentIndex(c_idx)

        themes = get_page_themes(self.lang)
        t_name = note.get("theme") or next(iter(themes.keys()))
        t_idx = self.theme_combo.findText(t_name)
        if t_idx >= 0:
            self.theme_combo.setCurrentIndex(t_idx)
        self.apply_page_theme(self.theme_combo.currentText(), announce=False)

        if note.get("html"):
            self.editor.setHtml(note["html"])
        else:
            self.editor.setPlainText(note.get("content", ""))

        self.lock_btn.setText(f" {self.tr('locked' if note.get('password') else 'lock')}")

        self.title_edit.blockSignals(False)
        self.editor.blockSignals(False)
        self.cat_combo.blockSignals(False)
        self.theme_combo.blockSignals(False)

        self.refresh_tasks_list()
        self.update_stats()

    def on_note_edited(self):
        note = self.get_current_note()
        if not note:
            return
        note["title"] = self.title_edit.text()
        note["category"] = self.cat_combo.currentData() or "Projects"
        note["content"] = self.editor.toPlainText()
        note["html"] = self.editor.toHtml()
        note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save_data()
        self.update_stats()
        self.refresh_notes_list()
        self.set_status(self.tr("status_auto_saved"), 1500)

    def create_new_note(self):
        new_id = str(int(time.time() * 1000))
        themes = get_page_themes(self.lang)
        default_theme = next(iter(themes.keys()))
        cat = self.current_category if self.current_category in ("Projects", "Personal", "Work", "Ideas") else "Projects"
        note = {
            "id": new_id,
            "keep_id": "",
            "title": self.tr("untitled"),
            "category": cat,
            "content": "",
            "html": "",
            "theme": default_theme,
            "pinned": False,
            "password": "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tasks": []
        }
        self.data.setdefault("notes", []).insert(0, note)
        self.save_data()
        self.current_note_id = new_id
        self.refresh_notes_list()
        self.load_note(new_id)
        self.title_edit.setFocus()
        self.set_status(self.tr("status_note_created"))

    def toggle_pin(self):
        note = self.get_current_note()
        if not note:
            return
        note["pinned"] = not bool(note.get("pinned", False))
        note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save_data()
        self.refresh_notes_list()
        self.set_status(self.tr("status_pin_updated"))

    def toggle_lock(self):
        note = self.get_current_note()
        if not note:
            return
        if note.get("password"):
            ans = QMessageBox.question(self, self.tr("unlock_title"), self.tr("unlock_prompt"))
            if ans == QMessageBox.StandardButton.Yes:
                note["password"] = ""
                self.unlocked_notes.discard(note["id"])
                self.lock_btn.setText(f" {self.tr('lock')}")
                self.save_data()
                self.refresh_notes_list()
                self.set_status(self.tr("status_unlocked"))
        else:
            pwd, ok = QInputDialog.getText(
                self,
                self.tr("lock_title"),
                self.tr("lock_prompt"),
                QLineEdit.EchoMode.Password
            )
            if ok and pwd:
                note["password"] = pwd
                self.unlocked_notes.add(note["id"])
                self.lock_btn.setText(f" {self.tr('locked')}")
                self.save_data()
                self.refresh_notes_list()
                self.set_status(self.tr("status_locked"))

    def delete_current_note(self):
        note = self.get_current_note()
        if not note:
            return
        ans = QMessageBox.question(self, self.tr("delete_title"), self.tr("delete_prompt"))
        if ans == QMessageBox.StandardButton.Yes:
            self.data["notes"] = [n for n in self.data.get("notes", []) if n["id"] != note["id"]]
            self.save_data()
            self.current_note_id = None
            self.refresh_notes_list()
            self.set_status(self.tr("status_deleted"))

    def apply_page_theme(self, theme_name, announce=True):
        themes = get_page_themes(self.lang)
        theme = themes.get(theme_name)
        if not theme:
            return
        note = self.get_current_note()
        if note:
            note["theme"] = theme_name
            self.save_data()

        bg = theme["bg"]
        fg = theme["fg"]
        border = theme["border"]
        if theme.get("ruled"):
            line = theme.get("line", "#F3E8B4")
            self.editor.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 12px; padding: 14px; "
                f"background-image: repeating-linear-gradient(to bottom, transparent, transparent 27px, {line} 28px);"
            )
        else:
            self.editor.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 12px; padding: 14px;"
            )
        if announce:
            self.set_status(self.tr("status_theme_changed", theme=theme_name), 2500)

    def open_floating_note(self):
        note = self.get_current_note()
        if not note:
            return
        fw = FloatingNoteWindow(note, self)
        fw.show()
        self.floating_windows.append(fw)
        self.set_status(self.tr("status_float_opened"))

    def toggle_bold(self):
        w = QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal
        self.editor.setFontWeight(w)

    def toggle_italic(self):
        self.editor.setFontItalic(not self.editor.fontItalic())

    def toggle_underline(self):
        self.editor.setFontUnderline(not self.editor.fontUnderline())

    def choose_text_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.editor.setTextColor(color)

    def choose_highlight_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            self.editor.mergeCurrentCharFormat(fmt)

    def insert_bullet_list(self):
        cursor = self.editor.textCursor()
        list_fmt = QTextListFormat()
        list_fmt.setStyle(QTextListFormat.Style.ListDisc)
        cursor.insertList(list_fmt)

    def select_all_editor(self):
        self.editor.selectAll()
        self.editor.setFocus()
        self.set_status(self.tr("status_selected_all"), 2000)

    def copy_all_editor(self):
        txt = self.editor.toPlainText()
        if not txt.strip():
            self.set_status(self.tr("status_nothing_to_copy"), 2000)
            return
        QApplication.clipboard().setText(txt)
        self.set_status(self.tr("status_copied_all"), 2500)

    def update_stats(self):
        txt = self.editor.toPlainText() if hasattr(self, "editor") else ""
        words = len(txt.split()) if txt.strip() else 0
        chars = len(txt)
        if hasattr(self, "stats_lbl"):
            self.stats_lbl.setText(self.tr("stats", words=words, chars=chars))

    def open_external_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("open_file"),
            "",
            "Supported Files (*.txt *.eml *.msg *.docx);;All Files (*)"
        )
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".docx":
                with zipfile.ZipFile(path) as zf:
                    xml_content = zf.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paras = ["".join(p.itertext()) for p in tree.findall(".//w:p", ns)]
                content = "\n".join([p for p in paras if p.strip()])
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

            name = os.path.basename(path)
            new_id = str(int(time.time() * 1000))
            themes = get_page_themes(self.lang)
            note = {
                "id": new_id,
                "keep_id": "",
                "title": os.path.splitext(name)[0],
                "category": "Projects",
                "content": content,
                "html": "",
                "theme": next(iter(themes.keys())),
                "pinned": False,
                "password": "",
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tasks": []
            }
            self.data.setdefault("notes", []).insert(0, note)
            self.save_data()
            self.refresh_notes_list()
            self.load_note(new_id)
            self.set_status(self.tr("status_file_opened", name=name))
        except Exception as err:
            QMessageBox.warning(self, self.tr("open_file"), self.tr("status_file_open_fail", err=str(err)))

    def export_current_note(self):
        note = self.get_current_note()
        if not note:
            return
        default_name = f"{(note.get('title') or self.tr('untitled'))}.txt"
        path, _ = QFileDialog.getSaveFileName(self, self.tr("export_title"), default_name, "Text Files (*.txt)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{note.get('title', '')}\n{'=' * 40}\n\n{note.get('content', '')}")
        self.set_status(self.tr("status_exported", name=os.path.basename(path)))

    def set_quick_reminder(self, minutes):
        target = (datetime.now() + timedelta(minutes=minutes)).strftime("%H:%M")
        self.reminder_input.setText(target)
        self.set_status(self.tr("status_reminder_set", time=target), 2500)

    def add_task(self):
        note = self.get_current_note()
        if not note:
            return
        text = self.task_input.text().strip()
        if not text:
            return
        rem = self.reminder_input.text().strip()
        if rem:
            try:
                datetime.strptime(rem, "%H:%M")
            except ValueError:
                self.set_status(self.tr("status_bad_time"))
                return

        note.setdefault("tasks", []).append({
            "text": text,
            "done": False,
            "priority": "Normal",
            "reminder": rem,
            "alerted": False
        })
        self.task_input.clear()
        self.reminder_input.clear()
        self.save_data()
        self.refresh_tasks_list()
        self.set_status(self.tr("status_task_added"), 2000)

    def refresh_tasks_list(self):
        self.tasks_list.clear()
        note = self.get_current_note()
        tasks = note.get("tasks", []) if note else []

        for idx, t_item in enumerate(tasks):
            row_widget = QFrame()
            row_widget.setProperty("class", "TaskRowCard")
            lay = QHBoxLayout(row_widget)
            lay.setContentsMargins(8, 6, 8, 6)
            lay.setSpacing(6)

            cb = QCheckBox(t_item.get("text", ""))
            cb.setChecked(bool(t_item.get("done", False)))
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_task_done(i, state == Qt.CheckState.Checked.value))
            lay.addWidget(cb, 1)

            if t_item.get("reminder"):
                rem_lbl = QLabel(f"⏰ {t_item['reminder']}")
                rem_lbl.setStyleSheet("color: #93C5FD; font-size: 11px;")
                lay.addWidget(rem_lbl)

            del_btn = QPushButton(qta.icon("fa5s.times", color="#F87171"))
            del_btn.setFixedSize(24, 24)
            del_btn.setStyleSheet("background: transparent; border: none;")
            del_btn.clicked.connect(lambda _, i=idx: self.delete_task(i))
            lay.addWidget(del_btn)

            list_item = QListWidgetItem()
            list_item.setSizeHint(row_widget.sizeHint())
            self.tasks_list.addItem(list_item)
            self.tasks_list.setItemWidget(list_item, row_widget)

        self.update_tasks_progress()

    def toggle_task_done(self, idx, done):
        note = self.get_current_note()
        if note and 0 <= idx < len(note.get("tasks", [])):
            note["tasks"][idx]["done"] = done
            self.save_data()
            self.update_tasks_progress()

    def delete_task(self, idx):
        note = self.get_current_note()
        if note and 0 <= idx < len(note.get("tasks", [])):
            note["tasks"].pop(idx)
            self.save_data()
            self.refresh_tasks_list()

    def update_tasks_progress(self):
        note = self.get_current_note()
        tasks = note.get("tasks", []) if note else []
        total = len(tasks)
        if total == 0:
            self.progress_lbl.setText(self.tr("progress_zero"))
            self.progress_bar.setValue(0)
            return
        done = sum(1 for t_item in tasks if t_item.get("done"))
        pct = int((done / total) * 100)
        self.progress_lbl.setText(self.tr("progress", pct=pct, done=done, total=total))
        self.progress_bar.setValue(pct)

    def reminder_worker(self):
        while True:
            try:
                now_hm = datetime.now().strftime("%H:%M")
                triggered = False
                for note in list(self.data.get("notes", [])):
                    for task in note.get("tasks", []):
                        if not task.get("done") and not task.get("alerted") and task.get("reminder") == now_hm:
                            task["alerted"] = True
                            triggered = True
                            body = self.tr("alarm_body", task=task.get("text", ""), note=note.get("title") or self.tr("untitled"))
                            self.signaler.alarm_triggered.emit(self.tr("alarm_title"), body)
                if triggered:
                    self.save_data()
            except Exception:
                pass
            time.sleep(10)

    def show_alarm_popup(self, title, body):
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
        QMessageBox.information(self, title, body)

    def open_keep_settings(self):
        keep_cfg = self.data.setdefault("keep", {})
        dlg = KeepSettingsDialog(keep_cfg, lang=self.lang, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            keep_cfg["email"] = vals["email"]
            keep_cfg["master_token"] = vals["master_token"]
            keep_cfg["auto_sync"] = vals["auto_sync"]
            self.save_data()
            self.set_status(self.tr("status_settings_saved"))

    def auto_keep_worker(self):
        while True:
            time.sleep(300)
            try:
                keep_cfg = self.data.get("keep", {})
                if keep_cfg.get("auto_sync") and keep_cfg.get("email") and keep_cfg.get("master_token") and not self.is_syncing:
                    self.start_keep_sync(silent=True)
            except Exception:
                pass

    def start_keep_sync(self, silent=False):
        if not HAS_GKEEP:
            if not silent:
                QMessageBox.information(self, self.tr("missing_gkeep_title"), self.tr("missing_gkeep_msg"))
            self.set_status(self.tr("status_missing_gkeep"))
            return

        keep_cfg = self.data.get("keep", {})
        email = keep_cfg.get("email", "").strip()
        token = keep_cfg.get("master_token", "").strip()
        if not email or not token:
            if not silent:
                self.open_keep_settings()
            return

        if self.is_syncing:
            return
        self.is_syncing = True
        self.sync_btn.setText(f"  {self.tr('syncing')}")
        self.set_status(self.tr("status_syncing"))
        threading.Thread(target=self._keep_sync_thread, args=(email, token), daemon=True).start()

    def _keep_sync_thread(self, email, token):
        try:
            keep = gkeepapi.Keep()
            keep.authenticate(email, token)
            keep.sync()

            existing_by_keep_id = {n.get("keep_id"): n for n in self.data.get("notes", []) if n.get("keep_id")}
            for gnote in keep.all():
                gid = getattr(gnote, "id", "")
                if not gid:
                    continue
                title = getattr(gnote, "title", "") or self.tr("keep_default_title")
                text = getattr(gnote, "text", "") or ""
                if gid in existing_by_keep_id:
                    existing_by_keep_id[gid]["title"] = title
                    existing_by_keep_id[gid]["content"] = text
                else:
                    themes = get_page_themes(self.lang)
                    self.data.setdefault("notes", []).append({
                        "id": f"keep_{gid}",
                        "keep_id": gid,
                        "title": title,
                        "category": "Personal",
                        "content": text,
                        "html": "",
                        "theme": next(iter(themes.keys())),
                        "pinned": bool(getattr(gnote, "pinned", False)),
                        "password": "",
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tasks": []
                    })

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.data.setdefault("keep", {})["last_sync"] = self.tr("keep_synced_prefix", time=now_str)
            self.save_data()
            self.signaler.sync_finished.emit(True, now_str)
        except Exception as err:
            self.signaler.sync_finished.emit(False, str(err))

    def on_sync_finished(self, ok, info):
        self.is_syncing = False
        self.sync_btn.setText(f"  {self.tr('sync_keep')}")
        if ok:
            self.keep_status_lbl.setText(self.data.get("keep", {}).get("last_sync", ""))
            self.refresh_notes_list()
            self.set_status(self.tr("status_synced", time=info))
        else:
            self.set_status(self.tr("status_sync_fail", err=info))
            QMessageBox.warning(self, self.tr("sync_err_title"), self.tr("status_sync_fail", err=info))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesHamzaStudio()
    window.show()
    sys.exit(app.exec())