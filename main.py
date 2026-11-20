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
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QTextListFormat

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"

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
        self.lang_combo