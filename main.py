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
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QTextListFormat, QColor


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
    opp_border_side = "border-right" if lang == "ar" else "border
