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
from PyQt6.QtGui import QFont, QIcon, QTextCharFormat, QColor, QTextListFormat

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

        # مبدل اللغة (العربية / English)
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
        side_lay.addSpacing(4)

        new_note_btn = QPushButton(f" {self.tr('new_note')}")
        new_note_btn.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        new_note_btn.setIconSize(QSize(15, 15))
        new_note_btn.setObjectName("PrimaryBtn")
        new_note_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_note_btn.clicked.connect(self.create_note)
        side_lay.addWidget(new_note_btn)
        side_lay.addSpacing(8)

        sections = [
            (self.tr("cat_all"), "All", "fa5s.layer-group", "#818CF8"),
            (self.tr("cat_pinned"), "Pinned", "fa5s.thumbtack", "#F59E0B"),
            (self.tr("cat_locked"), "Locked", "fa5s.lock", "#EF4444"),
            (self.tr("cat_projects"), "Projects", "fa5s.rocket", "#38BDF8"),
            (self.tr("cat_personal"), "Personal", "fa5s.user", "#34D399"),
            (self.tr("cat_work"), "Work", "fa5s.briefcase", "#FBBF24"),
            (self.tr("cat_ideas"), "Ideas", "fa5s.lightbulb", "#C084FC")
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

        self.sync_btn = QPushButton(f" {self.tr('sync_keep')}")
        self.sync_btn.setIcon(qta.icon("fa5s.sync", color="#38BDF8"))
        self.sync_btn.setObjectName("SyncBtn")
        self.sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_btn.clicked.connect(self.start_keep_sync)
        side_lay.addWidget(self.sync_btn)

        cfg_btn = QPushButton(f" {self.tr('keep_settings')}")
        cfg_btn.setIcon(qta.icon("fa5s.cog", color="#94A3B8"))
        cfg_btn.setProperty("class", "NavItem")
        cfg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_btn.clicked.connect(self.open_keep_settings)
        side_lay.addWidget(cfg_btn)

        export_btn = QPushButton(f" {self.tr('export_note')}")
        export_btn.setIcon(qta.icon("fa5s.file-export", color="#94A3B8"))
        export_btn.setProperty("class", "NavItem")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self.export_note)
        side_lay.addWidget(export_btn)

        last_sync_txt = self.data["keep"].get("last_sync") or self.tr("keep_not_synced")
        self.sync_status_lbl = QLabel(f"{self.tr('keep_prefix')} {last_sync_txt}")
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
        self.search_box.setPlaceholderText(self.tr("search_placeholder"))
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
        self.title_edit.setPlaceholderText(self.tr("title_placeholder"))
        self.title_edit.textEdited.connect(self.auto_save)
        top_bar.addWidget(self.title_edit, 1)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["Projects", "Personal", "Work", "Ideas"])
        self.cat_combo.setFixedWidth(115)
        self.cat_combo.currentTextChanged.connect(self.change_category)
        top_bar.addWidget(self.cat_combo)

        float_btn = QPushButton(f" {self.tr('floating')}")
        float_btn.setIcon(qta.icon("fa5s.external-link-alt", color="#38BDF8"))
        float_btn.setProperty("class", "IconActionBtn")
        float_btn.setToolTip(self.tr("floating_tip"))
        float_btn.clicked.connect(self.open_floating_window)
        top_bar.addWidget(float_btn)

        self.lock_btn = QPushButton(f" {self.tr('lock')}")
        self.lock_btn.setIcon(qta.icon("fa5s.unlock", color="#CBD5E1"))
        self.lock_btn.setProperty("class", "IconActionBtn")
        self.lock_btn.clicked.connect(self.toggle_lock)
        top_bar.addWidget(self.lock_btn)

        self.pin_btn = QPushButton(f" {self.tr('pin')}")
        self.pin_btn.setIcon(qta.icon("fa5s.thumbtack", color="#CBD5E1"))
        self.pin_btn.setProperty("class", "IconActionBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        top_bar.addWidget(self.pin_btn)

        del_note_btn = QPushButton()
        del_note_btn.setIcon(qta.icon("fa5s.trash-alt", color="#F87171"))
        del_note_btn.setProperty("class", "IconActionBtn")
        del_note_btn.setToolTip(self.tr("delete_tip"))
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

        themes_map = get_page_themes(self.lang)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(themes_map.keys()))
        self.theme_combo.setFixedWidth(175)
        self.theme_combo.currentTextChanged.connect(self.change_page_theme)
        tb_lay.addWidget(self.theme_combo)

        fmt_actions = [
            ("fa5s.bold", self.tr("bold_tip"), self.format_bold),
            ("fa5s.italic", self.tr("italic_tip"), self.format_italic),
            ("fa5s.underline", self.tr("underline_tip"), self.format_underline),
            ("fa5s.palette", self.tr("text_color_tip"), self.pick_text_color),
            ("fa5s.highlighter", self.tr("highlight_tip"), self.pick_highlight_color),
            ("fa5s.list-ul", self.tr("bullet_tip"), self.insert_bullet_list),
            ("fa5s.align-right", self.tr("align_right_tip"), lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight)),
            ("fa5s.align-left", self.tr("align_left_tip"), lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft)),
            ("fa5s.i-cursor", self.tr("select_all_tip"), self.select_all_note_text),
            ("fa5s.copy", self.tr("copy_all_tip"), self.copy_full_note)
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
        self.editor.setPlaceholderText(self.tr("editor_placeholder"))
        self.editor.textChanged.connect(self.auto_save)
        editor_lay.addWidget(self.editor, 1)

        self.stats_lbl = QLabel(self.tr("stats", words=0, chars=0))
        self.stats_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        editor_lay.addWidget(self.stats_lbl)

        # 4) لوحة المهام والتنبيهات
        tasks_panel = QFrame()
        tasks_panel.setObjectName("TasksPanel")
        tasks_panel.setFixedWidth(325)
        tasks_lay = QVBoxLayout(tasks_panel)
        tasks_lay.setContentsMargins(16, 18, 16, 16)
        tasks_lay.setSpacing(10)

        t_head = QLabel(self.tr("tasks_header"))
        t_head.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        tasks_lay.addWidget(t_head)

        self.prog_lbl = QLabel(self.tr("progress_zero"))
        self.prog_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        tasks_lay.addWidget(self.prog_lbl)

        self.prog_bar = QProgressBar()
        self.prog_bar.setTextVisible(False)
        tasks_lay.addWidget(self.prog_bar)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText(self.tr("task_placeholder"))
        self.task_input.returnPressed.connect(self.add_task)
        tasks_lay.addWidget(self.task_input)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(6)
        self.rem_input = QLineEdit()
        self.rem_input.setPlaceholderText(self.tr("reminder_placeholder"))
        self.rem_input.setFixedWidth(76)
        sub_row.addWidget(self.rem_input)

        self.prio_combo = QComboBox()
        self.prio_combo.addItems(["High", "Medium", "Low"])
        self.prio_combo.setFixedWidth(86)
        sub_row.addWidget(self.prio_combo)

        add_t_btn = QPushButton(self.tr("add_task"))
        add_t_btn.setObjectName("PrimaryBtn")
        add_t_btn.setStyleSheet("padding: 8px 10px; font-size: 12.5px;")
        add_t_btn.clicked.connect(self.add_task)
        sub_row.addWidget(add_t_btn, 1)
        tasks_lay.addLayout(sub_row)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(6)
        btn_15m = QPushButton(self.tr("plus_15m"))
        btn_15m.setProperty("class", "QuickTimeBtn")
        btn_15m.clicked.connect(lambda: self.set_quick_reminder(15))

        btn_1h = QPushButton(self.tr("plus_1h"))
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
        self.set_status(self.tr("ready"), 3000)

        self.set_category(self.current_category)

    def set_quick_reminder(self, minutes):
        target_time = (datetime.now() + timedelta(minutes=minutes)).strftime("%H:%M")
        self.rem_input.setText(target_time)
        self.set_status(self.tr("status_reminder_set", time=target_time), 2500)

    # ================= Google Keep Sync =================
    def open_keep_settings(self):
        dlg = KeepSettingsDialog(self.data.get("keep", {}), self.lang, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            self.data["keep"]["email"] = vals["email"]
            self.data["keep"]["master_token"] = vals["master_token"]
            self.data["keep"]["auto_sync"] = vals["auto_sync"]
            self.save_data()
            self.set_status(self.tr("status_settings_saved"), 3500)

    def start_keep_sync(self):
        if self.is_syncing:
            return
        if not HAS_GKEEP:
            self.set_status(self.tr("status_missing_gkeep"), 5000)
            QMessageBox.warning(self, self.tr("missing_gkeep_title"), self.tr("missing_gkeep_msg"))
            return

        cfg = self.data.get("keep", {})
        if not cfg.get("email") or not cfg.get("master_token"):
            self.open_keep_settings()
            cfg = self.data.get("keep", {})
            if not cfg.get("email") or not cfg.get("master_token"):
                return

        self.is_syncing = True
        self.sync_btn.setText(f" {self.tr('syncing')}")
        self.sync_btn.setEnabled(False)
        self.set_status(self.tr("status_syncing"), 10000)
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
                        kn.title = n["title"] or self.tr("untitled")
                        kn.text = n["content"] or ""
                        kn.pinned = bool(n.get("pinned"))
                        local_by_keep_id[n["keep_id"]] = n
                else:
                    created = keep.createNote(n["title"] or self.tr("untitled"), n["content"] or "")
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
                    "title": kn.title or self.tr("keep_default_title"),
                    "category": "All",
                    "content": kn.text or "",
                    "html": "",
                    "theme": next(iter(get_page_themes(self.lang).keys())),
                    "pinned": bool(kn.pinned),
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": []
                })

            now_str = datetime.now().strftime("%H:%M")
            self.data["keep"]["last_sync"] = self.tr("keep_synced_prefix", time=now_str)
            self.save_data()
            self.signaler.sync_finished.emit(True, self.tr("status_synced", time=now_str))
        except Exception as e:
            self.signaler.sync_finished.emit(False, self.tr("status_sync_fail", err=e))

    def on_sync_finished(self, ok, msg):
        self.is_syncing = False
        self.sync_btn.setText(f" {self.tr('sync_keep')}")
        self.sync_btn.setEnabled(True)
        last_sync_txt = self.data["keep"].get("last_sync") or self.tr("keep_not_synced")
        self.sync_status_lbl.setText(f"{self.tr('keep_prefix')} {last_sync_txt}")
        self.refresh_notes_list()
        self.set_status(msg, 5000)
        if not ok:
            QMessageBox.warning(self, self.tr("sync_err_title"), msg)

    def auto_keep_worker(self):
        while True:
            time.sleep(300)
            if self.data.get("keep", {}).get("auto_sync") and not self.is_syncing:
                self.start_keep_sync()

    # ================= Editor Formatting & Actions =================
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

    def select_all_note_text(self):
        self.editor.selectAll()
        self.editor.setFocus()
        self.set_status(self.tr("status_selected_all"), 2500)

    def copy_full_note(self):
        note = self.get_current_note()
        title = (self.title_edit.text() or (note.get("title") if note else "") or "").strip()
        body = (self.editor.toPlainText() or (note.get("content") if note else "") or "").strip()

        if title and body:
            full_text = f"{title}\n\n{body}"
        else:
            full_text = title or body

        if not full_text:
            self.set_status(self.tr("status_nothing_to_copy"), 2500)
            return

        QApplication.clipboard().setText(full_text)
        self.set_status(self.tr("status_copied_all"), 3000)

    def apply_editor_theme(self, theme_name):
        themes = get_page_themes(self.lang)
        th = themes.get(theme_name) or next(iter(themes.values()))
        if th.get("ruled"):
            ruled_bg = (
                f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {th['bg']}, stop:0.92 {th['bg']}, "
                f"stop:0.96 {th['line']}, stop:1 {th['bg']});"
            )
            self.editor.setStyleSheet(
                f"QTextEdit {{ background: {ruled_bg} color: {th['fg']}; "
                f"border: 1px solid {th['border']}; border-radius: 12px; "
                f"padding: 16px; font-size: 15px; line-height: 28px; }}"
            )
        else:
            self.editor.setStyleSheet(
                f"QTextEdit {{ background-color: {th['bg']}; color: {th['fg']}; "
                f"border: 1px solid {th['border']}; border-radius: 12px; "
                f"padding: 16px; font-size: 14.5px; }}"
            )

    def change_page_theme(self, theme_name):
        self.apply_editor_theme(theme_name)
        note = self.get_current_note()
        if note:
            note["theme"] = theme_name
            self.save_data()
            self.set_status(self.tr("status_theme_changed", theme=theme_name), 2500)

    def open_floating_window(self):
        note = self.get_current_note()
        if not note:
            return
        w = FloatingNoteWindow(note, self)
        w.show()
        self.floating_windows.append(w)
        self.set_status(self.tr("status_float_opened"), 2500)

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
            title = (n["title"] or self.tr("untitled")).strip()
            if n.get("password"):
                snippet = self.tr("locked_note_snippet")
            else:
                one_line = " ".join((n.get("content") or "").split())
                snippet = (one_line[:52] + "...") if len(one_line) > 52 else (one_line or self.tr("no_content"))

            sync_tag = f"  •  {self.tr('keep_tag')}" if n.get("keep_id") else ""
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
            pwd, ok = QInputDialog.getText(
                self, self.tr("enter_password_title"), self.tr("enter_password_prompt"), QLineEdit.EchoMode.Password
            )
            if not ok or pwd != note["password"]:
                if ok:
                    self.set_status(self.tr("wrong_password"), 3500)
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_edit.blockSignals(True)
        self.editor.blockSignals(True)
        self.theme_combo.blockSignals(True)

        self.title_edit.setText(note["title"])
        themes = get_page_themes(self.lang)
        theme_name = note.get("theme") if note.get("theme") in themes else next(iter(themes.keys()))
        self.theme_combo.setCurrentText(theme_name)
        self.apply_editor_theme(theme_name)

        if note.get("html"):
            self.editor.setHtml(note["html"])
        else:
            self.editor.setPlainText(note.get("content", ""))

        self.cat_combo.setCurrentText(note.get("category", "Projects"))
        self.lock_btn.setText(f" {self.tr('locked')}" if note.get("password") else f" {self.tr('lock')}")
        self.lock_btn.setIcon(
            qta.icon("fa5s.lock" if note.get("password") else "fa5s.unlock", color="#F59E0B" if note.get("password") else "#CBD5E1")
        )
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
        default_theme = next(iter(get_page_themes(self.lang).keys()))
        self.data["notes"].insert(0, {
            "id": nid, "keep_id": "", "title": self.tr("new_note"), "category": cat,
            "content": "", "html": "", "theme": default_theme,
            "pinned": False, "password": "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "tasks": []
        })
        self.save_data()
        self.load_note(nid)
        self.set_status(self.tr("status_note_created"), 2500)

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
        self.set_status(self.tr("status_auto_saved"), 1500)

    def update_stats(self):
        txt = self.editor.toPlainText()
        self.stats_lbl.setText(self.tr("stats", words=len(txt.split()), chars=len(txt)))

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
            self.set_status(self.tr("status_pin_updated"), 2000)

    def toggle_lock(self):
        note = self.get_current_note()
        if not note:
            return
        if note.get("password"):
            if QMessageBox.question(self, self.tr("unlock_title"), self.tr("unlock_prompt")) == QMessageBox.StandardButton.Yes:
                note["password"] = ""
                self.save_data()
                self.load_note(note["id"])
                self.set_status(self.tr("status_unlocked"), 2500)
        else:
            pwd, ok = QInputDialog.getText(
                self, self.tr("lock_title"), self.tr("lock_prompt"), QLineEdit.EchoMode.Password
            )
            if ok and pwd.strip():
                note["password"] = pwd.strip()
                self.unlocked_notes.add(note["id"])
                self.save_data()
                self.load_note(note["id"])
                self.set_status(self.tr("status_locked"), 2500)

    def delete_note(self):
        if not self.current_note_id:
            return
        if QMessageBox.question(self, self.tr("delete_title"), self.tr("delete_prompt")) == QMessageBox.StandardButton.Yes:
            self.data["notes"] = [n for n in self.data["notes"] if n["id"] != self.current_note_id]
            self.current_note_id = None
            self.title_edit.clear()
            self.editor.clear()
            self.save_data()
            self.refresh_notes_list()
            self.refresh_tasks()
            self.set_status(self.tr("status_deleted"), 2500)

    def export_note(self):
        note = self.get_current_note()
        if not note:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("export_title"), f"{note['title']}.md", "Markdown (*.md);;HTML (*.html);;Text (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".html"):
                    f.write(note.get("html") or note.get("content", ""))
                else:
                    f.write(f"# {note['title']}\n\n{note['content']}\n")
            self.set_status(self.tr("status_exported", name=os.path.basename(path)), 4000)

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
                self.set_status(self.tr("status_bad_time"), 4000)
                return
        note.setdefault("tasks", []).append({
            "text": txt, "done": False, "priority": self.prio_combo.currentText(),
            "reminder": rem, "alerted": False
        })
        self.task_input.clear()
        self.rem_input.clear()
        self.save_data()
        self.refresh_tasks()
        self.set_status(self.tr("status_task_added"), 2000)

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
            self.prog_lbl.setText(self.tr("progress", pct=pct, done=done, total=len(tasks)))
        else:
            self.prog_bar.setValue(0)
            self.prog_lbl.setText(self.tr("progress_zero"))

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
        QMessageBox.information(self, self.tr("alarm_title"), self.tr("alarm_body", task=task_text, note=note_title))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NotesHamzaStudio()
    win.show()
    sys.exit(app.exec())
