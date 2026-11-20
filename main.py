import customtkinter as ctk
import json
import os
import threading
import time
import winsound
from datetime import datetime
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageDraw

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "notes_hamza_data.json"
ICON_FILE = "icon.ico"

def generate_app_icon():
    """توليد أيقونة احترافية للبرنامج تلقائياً إذا لم تكن موجودة"""
    if not os.path.exists(ICON_FILE):
        img = Image.new("RGBA", (256, 256), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([20, 20, 236, 236], radius=45, fill=(59, 130, 246, 255))
        draw.rectangle([65, 70, 191, 90], fill=(255, 255, 255, 255))
        draw.rectangle([65, 118, 191, 138], fill=(255, 255, 255, 255))
        draw.rectangle([65, 166, 150, 186], fill=(255, 255, 255, 255))
        img.save(ICON_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32)])

class NotesHamzaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        generate_app_icon()

        self.title("Notes Hamza v2.0 - Advanced Notepad & To-Do")
        self.geometry("1300x780")
        self.minsize(1050, 620)
        if os.path.exists(ICON_FILE):
            self.iconbitmap(ICON_FILE)

        self.data = self.load_data()
        self.current_note_id = None
        self.current_category = "All"
        self.unlocked_notes = set()

        self.setup_ui()
        self.refresh_notes_list()

        self.reminder_thread = threading.Thread(target=self.check_reminders_loop, daemon=True)
        self.reminder_thread.start()

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
                    "title": "مرحباً بك في Notes Hamza v2.0",
                    "category": "Projects",
                    "content": "أهلاً بك في النسخة المتقدمة!\n\nالمميزات الجديدة:\n• قفل الملاحظات السرية بكلمة مرور (زر القفل بالأعلى)\n• تحديد وقت تذكير للمهام مع تنبيه صوتي تلقائي\n• جاهز للتصدير والرفع على GitHub",
                    "pinned": True,
                    "password": "",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tasks": [
                        {"text": "تجربة قفل ملاحظة بكلمة مرور", "done": False, "priority": "High", "reminder": "", "alerted": False},
                        {"text": "رفع المشروع على GitHub", "done": False, "priority": "Medium", "reminder": "", "alerted": False}
                    ]
                }
            ]
        }

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=0, minsize=270)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=1, minsize=340)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#111622")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        logo_label = ctk.CTkLabel(
            self.sidebar, text="📝 Notes Hamza",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#3B82F6"
        )
        logo_label.pack(pady=(25, 20), padx=20, anchor="w")

        new_btn = ctk.CTkButton(
            self.sidebar, text="+ ملاحظة جديدة", command=self.create_new_note,
            font=ctk.CTkFont(size=14, weight="bold"), height=38
        )
        new_btn.pack(pady=(0, 20), padx=15, fill="x")

        categories = [("📁 الكل", "All"), ("📌 المثبتة", "Pinned"), ("🔒 المقفلة", "Locked"),
                      ("🚀 المشاريع", "Projects"), ("👤 شخصي", "Personal"),
                      ("💼 العمل", "Work"), ("💡 أفكار", "Ideas")]
        
        for label, cat in categories:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", fg_color="transparent",
                hover_color="#1E293B", text_color="#CBD5E1",
                command=lambda c=cat: self.filter_category(c)
            )
            btn.pack(pady=3, padx=15, fill="x")

        export_btn = ctk.CTkButton(
            self.sidebar, text="📤 تصدير الملاحظة", fg_color="#1E293B",
            hover_color="#334155", command=self.export_note
        )
        export_btn.pack(side="bottom", pady=20, padx=15, fill="x")

        # 2. Notes List
        self.notes_list_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#161D2C")
        self.notes_list_frame.grid(row=0, column=1, sticky="nsew", padx=(1, 1))
        self.notes_list_frame.grid_rowconfigure(1, weight=1)
        self.notes_list_frame.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_notes_list())
        search_entry = ctk.CTkEntry(
            self.notes_list_frame, placeholder_text="🔍 بحث في الملاحظات...",
            textvariable=self.search_var, height=35, fg_color="#0F172A", border_width=0
        )
        search_entry.grid(row=0, column=0, padx=12, pady=15, sticky="ew")

        self.notes_scroll = ctk.CTkScrollableFrame(self.notes_list_frame, fg_color="transparent")
        self.notes_scroll.grid(row=1, column=0, sticky="nsew", padx=5)

        # 3. Editor
        self.editor_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0F172A")
        self.editor_frame.grid(row=0, column=2, sticky="nsew")
        self.editor_frame.grid_rowconfigure(2, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        top_bar.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(
            top_bar, placeholder_text="عنوان الملاحظة...",
            font=ctk.CTkFont(size=22, weight="bold"), fg_color="transparent", border_width=0
        )
        self.title_entry.grid(row=0, column=0, sticky="ew")
        self.title_entry.bind("<KeyRelease>", self.auto_save_current_note)

        self.cat_menu = ctk.CTkOptionMenu(
            top_bar, values=["Projects", "Personal", "Work", "Ideas"],
            width=105, command=self.change_note_category
        )
        self.cat_menu.grid(row=0, column=1, padx=4)

        self.lock_btn = ctk.CTkButton(top_bar, text="🔓", width=35, fg_color="#1E293B", command=self.manage_password)
        self.lock_btn.grid(row=0, column=2, padx=3)

        self.pin_btn = ctk.CTkButton(top_bar, text="📌", width=35, fg_color="#1E293B", command=self.toggle_pin)
        self.pin_btn.grid(row=0, column=3, padx=3)

        del_btn = ctk.CTkButton(top_bar, text="🗑️", width=35, fg_color="#7F1D1D", hover_color="#991B1B", command=self.delete_note)
        del_btn.grid(row=0, column=4, padx=3)

        format_bar = ctk.CTkFrame(self.editor_frame, fg_color="#1E293B", height=36, corner_radius=8)
        format_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        ctk.CTkButton(format_bar, text="• قائمة", width=65, height=26, fg_color="transparent", command=lambda: self.insert_format("• ")).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(format_bar, text="B عريض", width=65, height=26, fg_color="transparent", command=lambda: self.insert_format("**نص عريض**")).pack(side="left", padx=5)
        ctk.CTkButton(format_bar, text="</> كود", width=65, height=26, fg_color="transparent", command=lambda: self.insert_format("\n```\nاكتب الكود هنا\n```\n")).pack(side="left", padx=5)
        ctk.CTkButton(format_bar, text="🕒 الوقت", width=65, height=26, fg_color="transparent", command=lambda: self.insert_format(datetime.now().strftime("%Y-%m-%d %H:%M"))).pack(side="left", padx=5)

        self.content_textbox = ctk.CTkTextbox(
            self.editor_frame, font=ctk.CTkFont(size=15), fg_color="#0F172A",
            wrap="word", undo=True
        )
        self.content_textbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        self.content_textbox.bind("<KeyRelease>", self.auto_save_current_note)

        self.status_label = ctk.CTkLabel(
            self.editor_frame, text="الكلمات: 0 | الأحرف: 0",
            font=ctk.CTkFont(size=12), text_color="#64748B"
        )
        self.status_label.grid(row=3, column=0, sticky="e", padx=25, pady=(0, 10))

        # 4. To-Do Panel
        self.todo_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#161D2C")
        self.todo_frame.grid(row=0, column=3, sticky="nsew", padx=(1, 0))
        self.todo_frame.grid_rowconfigure(3, weight=1)
        self.todo_frame.grid_columnconfigure(0, weight=1)

        todo_header = ctk.CTkLabel(
            self.todo_frame, text="✅ المهام والتنبيهات (To-Do)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        todo_header.grid(row=0, column=0, padx=15, pady=(20, 10), sticky="w")

        self.progress_label = ctk.CTkLabel(self.todo_frame, text="نسبة الإنجاز: 0%", font=ctk.CTkFont(size=12), text_color="#94A3B8")
        self.progress_label.grid(row=1, column=0, padx=15, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self.todo_frame, height=8)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(22, 10), sticky="ew")
        self.progress_bar.set(0)

        add_task_frame = ctk.CTkFrame(self.todo_frame, fg_color="transparent")
        add_task_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        add_task_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(add_task_frame, placeholder_text="أضف مهمة جديدة...")
        self.task_entry.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 6))
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        self.reminder_entry = ctk.CTkEntry(add_task_frame, placeholder_text="تنبيه HH:MM", width=105)
        self.reminder_entry.grid(row=1, column=0, sticky="w")

        self.priority_menu = ctk.CTkOptionMenu(add_task_frame, values=["High", "Medium", "Low"], width=90)
        self.priority_menu.grid(row=1, column=1, padx=5)

        add_task_btn = ctk.CTkButton(add_task_frame, text="+ إضافة", width=70, command=self.add_task)
        add_task_btn.grid(row=1, column=2)

        self.tasks_scroll = ctk.CTkScrollableFrame(self.todo_frame, fg_color="transparent")
        self.tasks_scroll.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

    def get_current_note(self):
        for note in self.data["notes"]:
            if note["id"] == self.current_note_id:
                return note
        return None

    def filter_category(self, category):
        self.current_category = category
        self.refresh_notes_list()

    def refresh_notes_list(self):
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        filtered_notes = []

        for note in self.data["notes"]:
            is_locked = bool(note.get("password"))
            if self.current_category == "Pinned" and not note.get("pinned", False):
                continue
            elif self.current_category == "Locked" and not is_locked:
                continue
            elif self.current_category not in ["All", "Pinned", "Locked"] and note.get("category") != self.current_category:
                continue

            searchable_content = "" if is_locked else note["content"].lower()
            if query in note["title"].lower() or query in searchable_content:
                filtered_notes.append(note)

        filtered_notes.sort(key=lambda x: x.get("pinned", False), reverse=True)

        for note in filtered_notes:
            is_selected = (note["id"] == self.current_note_id)
            bg_color = "#1E293B" if is_selected else "transparent"
            pin_icon = "📌 " if note.get("pinned") else ""
            lock_icon = "🔒 " if note.get("password") else ""
            
            card = ctk.CTkButton(
                self.notes_scroll,
                text=f"{pin_icon}{lock_icon}{note['title'] or 'بدون عنوان'}\n{note['category']} • {note['updated_at']}",
                anchor="w", fg_color=bg_color, hover_color="#1E293B",
                height=55, corner_radius=8,
                command=lambda n_id=note["id"]: self.select_note(n_id)
            )
            card.pack(fill="x", pady=3, padx=5)

        if not self.current_note_id and filtered_notes:
            self.select_note(filtered_notes[0]["id"])

    def select_note(self, note_id):
        target_note = next((n for n in self.data["notes"] if n["id"] == note_id), None)
        if not target_note:
            return

        if target_note.get("password") and note_id not in self.unlocked_notes:
            pwd = simpledialog.askstring("ملاحظة محمية 🔒", "أدخل كلمة المرور لفتح الملاحظة:", show="*")
            if pwd != target_note["password"]:
                if pwd is not None:
                    messagebox.showerror("خطأ", "كلمة المرور غير صحيحة!")
                return
            self.unlocked_notes.add(note_id)

        self.current_note_id = note_id
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, target_note["title"])

        self.content_textbox.delete("1.0", "end")
        self.content_textbox.insert("1.0", target_note["content"])

        self.cat_menu.set(target_note.get("category", "Projects"))
        self.pin_btn.configure(fg_color="#3B82F6" if target_note.get("pinned") else "#1E293B")
        self.lock_btn.configure(
            text="🔒" if target_note.get("password") else "🔓",
            fg_color="#D97706" if target_note.get("password") else "#1E293B"
        )

        self.update_word_count()
        self.refresh_tasks_list()
        self.refresh_notes_list()

    def manage_password(self):
        note = self.get_current_note()
        if not note:
            return

        if note.get("password"):
            if messagebox.askyesno("إزالة القفل", "هذه الملاحظة مقفلة حالياً. هل تريد إزالة كلمة المرور؟"):
                note["password"] = ""
                self.lock_btn.configure(text="🔓", fg_color="#1E293B")
                self.save_data()
                self.refresh_notes_list()
        else:
            new_pwd = simpledialog.askstring("قفل الملاحظة 🔒", "أدخل كلمة مرور جديدة لحماية هذه الملاحظة:", show="*")
            if new_pwd and new_pwd.strip():
                note["password"] = new_pwd.strip()
                self.unlocked_notes.add(note["id"])
                self.lock_btn.configure(text="🔒", fg_color="#D97706")
                self.save_data()
                self.refresh_notes_list()
                messagebox.showinfo("تم القفل", "تم تأمين الملاحظة بكلمة مرور بنجاح!")

    def create_new_note(self):
        new_id = str(int(datetime.now().timestamp() * 1000))
        new_note = {
            "id": new_id,
            "title": "ملاحظة جديدة",
            "category": self.current_category if self.current_category not in ["All", "Pinned", "Locked"] else "Projects",
            "content": "",
            "pinned": False,
            "password": "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tasks": []
        }
        self.data["notes"].insert(0, new_note)
        self.save_data()
        self.select_note(new_id)

    def auto_save_current_note(self, event=None):
        note = self.get_current_note()
        if not note:
            return
        note["title"] = self.title_entry.get()
        note["content"] = self.content_textbox.get("1.0", "end-1c")
        note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.update_word_count()
        self.save_data()

    def update_word_count(self):
        text = self.content_textbox.get("1.0", "end-1c")
        self.status_label.configure(text=f"الكلمات: {len(text.split())} | الأحرف: {len(text)}")

    def change_note_category(self, new_cat):
        note = self.get_current_note()
        if note:
            note["category"] = new_cat
            self.save_data()
            self.refresh_notes_list()

    def toggle_pin(self):
        note = self.get_current_note()
        if note:
            note["pinned"] = not note.get("pinned", False)
            self.pin_btn.configure(fg_color="#3B82F6" if note["pinned"] else "#1E293B")
            self.save_data()
            self.refresh_notes_list()

    def delete_note(self):
        if not self.current_note_id:
            return
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذه الملاحظة؟"):
            self.data["notes"] = [n for n in self.data["notes"] if n["id"] != self.current_note_id]
            self.current_note_id = None
            self.save_data()
            self.title_entry.delete(0, "end")
            self.content_textbox.delete("1.0", "end")
            self.refresh_notes_list()
            self.refresh_tasks_list()

    def insert_format(self, text):
        self.content_textbox.insert("insert", text)
        self.auto_save_current_note()

    def export_note(self):
        note = self.get_current_note()
        if not note:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialfile=f"{note['title']}.md",
            filetypes=[("Markdown File", "*.md"), ("Text File", "*.txt")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {note['title']}\n\n{note['content']}\n\n## المهام:\n")
                for t in note.get("tasks", []):
                    status = "[x]" if t["done"] else "[ ]"
                    rem = f" [⏰ {t['reminder']}]" if t.get("reminder") else ""
                    f.write(f"- {status} {t['text']} ({t['priority']}){rem}\n")
            messagebox.showinfo("تم التصدير", "تم حفظ الملف بنجاح!")

    def add_task(self):
        note = self.get_current_note()
        task_text = self.task_entry.get().strip()
        reminder_time = self.reminder_entry.get().strip()
        if not note or not task_text:
            return

        if reminder_time:
            try:
                datetime.strptime(reminder_time, "%H:%M")
            except ValueError:
                messagebox.showwarning("تنسيق خاطئ", "يرجى إدخال وقت التنبيه بصيغة HH:MM مثل 14:30")
                return

        note.setdefault("tasks", []).append({
            "text": task_text,
            "done": False,
            "priority": self.priority_menu.get(),
            "reminder": reminder_time,
            "alerted": False
        })
        self.task_entry.delete(0, "end")
        self.reminder_entry.delete(0, "end")
        self.save_data()
        self.refresh_tasks_list()

    def refresh_tasks_list(self):
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()

        note = self.get_current_note()
        tasks = note.get("tasks", []) if note else []
        priority_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

        for idx, task in enumerate(tasks):
            row = ctk.CTkFrame(self.tasks_scroll, fg_color="#1E293B", corner_radius=8)
            row.pack(fill="x", pady=4, padx=2)

            rem_text = f" ⏰ {task['reminder']}" if task.get("reminder") else ""
            var = ctk.BooleanVar(value=task["done"])
            cb = ctk.CTkCheckBox(
                row, text=f"{task['text']}{rem_text}", variable=var,
                command=lambda i=idx: self.toggle_task(i)
            )
            cb.pack(side="left", padx=10, pady=8)

            del_t = ctk.CTkButton(
                row, text="✕", width=24, height=24, fg_color="transparent",
                hover_color="#7F1D1D", command=lambda i=idx: self.delete_task(i)
            )
            del_t.pack(side="right", padx=5)

            badge = ctk.CTkLabel(
                row, text=task["priority"], font=ctk.CTkFont(size=10, weight="bold"),
                text_color=priority_colors.get(task["priority"], "#FFFFFF")
            )
            badge.pack(side="right", padx=5)

        if tasks:
            done_count = sum(1 for t in tasks if t["done"])
            ratio = done_count / len(tasks)
            self.progress_bar.set(ratio)
            self.progress_label.configure(text=f"نسبة الإنجاز: {int(ratio * 100)}% ({done_count}/{len(tasks)})")
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="نسبة الإنجاز: 0%")

    def toggle_task(self, idx):
        note = self.get_current_note()
        if note:
            note["tasks"][idx]["done"] = not note["tasks"][idx]["done"]
            self.save_data()
            self.refresh_tasks_list()

    def delete_task(self, idx):
        note = self.get_current_note()
        if note:
            note["tasks"].pop(idx)
            self.save_data()
            self.refresh_tasks_list()

    def check_reminders_loop(self):
        while True:
            now_str = datetime.now().strftime("%H:%M")
            for note in self.data.get("notes", []):
                for task in note.get("tasks", []):
                    if not task.get("done") and task.get("reminder") == now_str and not task.get("alerted"):
                        task["alerted"] = True
                        self.save_data()
                        self.after(0, lambda t=task["text"], n=note["title"]: self.trigger_alarm(t, n))
            time.sleep(10)

    def trigger_alarm(self, task_text, note_title):
        try:
            winsound.Beep(1000, 700)
            winsound.Beep(1200, 700)
        except Exception:
            pass
        messagebox.showinfo("⏰ تذكير بمهمة - Notes Hamza", f"حان موعد المهمة:\n\n• {task_text}\n(من ملاحظة: {note_title})")

if __name__ == "__main__":
    app = NotesHamzaApp()
    app.mainloop()
