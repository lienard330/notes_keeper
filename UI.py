import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from DB import add_note, get_notes, delete_note, update_note, upgrade_user
import os

class NotesApp(tk.Tk):
    def __init__(self, user_id, username, is_premium):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.is_premium = is_premium
        self.title("Encrypted Notes Keeper")
        self.geometry("1000x600")
        self.configure(bg="#121212")

        self.theme = "dark"

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#202020", width=200)
        self.sidebar.pack(side="left", fill="y")

        # Main area
        self.main_area = tk.Frame(self, bg="#121212")
        self.main_area.pack(side="right", expand=True, fill="both")

        self._build_sidebar()
        self._build_main_area()
        self.load_notes()

    # ---------------- Sidebar ----------------
    def _build_sidebar(self):
        tk.Label(self.sidebar, text=f"Welcome, {self.username}",
                 bg="#202020", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=15)

        ttk.Button(self.sidebar, text="📝 Notes", command=self.load_notes).pack(pady=5, fill="x")

        tk.Label(self.sidebar, text="★ Premium Features",
                 bg="#202020", fg="#1E88E5", font=("Segoe UI", 10, "bold")).pack(pady=(20, 5))

        self.sync_status = tk.Label(self.sidebar, text="☁ Offline", bg="#202020", fg="#F44336")
        self.sync_status.pack(pady=2)

        self.export_btn = ttk.Button(self.sidebar, text="⬇ Backup & Export", command=self.bulk_export)
        self.export_btn.pack(pady=5, fill="x")

        self.upgrade_btn = ttk.Button(self.sidebar, text="Upgrade to Premium", command=self.upgrade_account)
        self.upgrade_btn.pack(pady=10, fill="x")

        ttk.Button(self.sidebar, text="⚙ Settings", command=self.toggle_theme).pack(side="bottom", pady=5, fill="x")
        ttk.Button(self.sidebar, text="🚪 Logout", command=self.logout).pack(side="bottom", pady=5, fill="x")

        self._apply_premium_state()

    # ---------------- Main Area ----------------
    def _build_main_area(self):
        self.note_list_frame = tk.Frame(self.main_area, bg="#1e1e1e", width=280)
        self.note_list_frame.pack(side="left", fill="y")

        self.editor_frame = tk.Frame(self.main_area, bg="#121212")
        self.editor_frame.pack(side="right", expand=True, fill="both")

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.note_list_frame, textvariable=self.search_var)
        search_entry.pack(pady=10, padx=10, fill="x")
        search_entry.bind("<KeyRelease>", self.search_notes)

        action_frame = tk.Frame(self.note_list_frame, bg="#1e1e1e")
        action_frame.pack(pady=5, padx=10, fill="x")
        ttk.Button(action_frame, text="＋ Add", command=self.add_note).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(action_frame, text="🗑 Delete", command=self.delete_selected).pack(side="left", expand=True, fill="x", padx=2)

        self.notes_listbox = tk.Listbox(self.note_list_frame, bg="#1e1e1e", fg="white",
                                        selectbackground="#1E88E5", activestyle="dotbox")
        self.notes_listbox.pack(expand=True, fill="both", padx=10, pady=10)
        self.notes_listbox.bind("<<ListboxSelect>>", self.display_note)

        self.note_title_var = tk.StringVar()
        self.title_entry = ttk.Entry(self.editor_frame, textvariable=self.note_title_var, font=("Segoe UI", 14, "bold"))
        self.title_entry.pack(pady=10, padx=10, fill="x")

        editor_actions = tk.Frame(self.editor_frame, bg="#121212")
        editor_actions.pack(pady=5, padx=10, fill="x")

        ttk.Button(editor_actions, text="💾 Save", command=self.save_note).pack(side="left", padx=5)

        self.content_text = tk.Text(self.editor_frame, bg="#1e1e1e", fg="white",
                                    insertbackground="white", wrap="word")
        self.content_text.pack(expand=True, fill="both", padx=10, pady=10)

        self._apply_premium_state()

    # ---------------- Notes Logic ----------------
    def load_notes(self):
        self.notes_listbox.delete(0, tk.END)
        self.notes = get_notes(self.user_id)
        for n in self.notes:
            preview = (n[2][:30] + "...") if len(n[2]) > 30 else n[2]
            self.notes_listbox.insert(tk.END, f"{n[1]} - {preview}")

    def add_note(self):
        add_note(self.user_id, "Untitled", "")
        self.load_notes()

    def delete_selected(self):
        selection = self.notes_listbox.curselection()
        if selection:
            note_id = self.notes[selection[0]][0]
            delete_note(note_id)
            self.load_notes()
            self.note_title_var.set("")
            self.content_text.delete("1.0", tk.END)

    def display_note(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            note = self.notes[selection[0]]
            self.note_title_var.set(note[1])
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert(tk.END, note[2])

    def save_note(self):
        selection = self.notes_listbox.curselection()
        if selection:
            note_id = self.notes[selection[0]][0]
            new_title = self.note_title_var.get()
            new_content = self.content_text.get("1.0", tk.END).strip()
            update_note(note_id, new_title, new_content)
            self.load_notes()

    # ---------------- Premium Features ----------------
    def search_notes(self, event):
        if not self.is_premium:
            return
        query = self.search_var.get().lower()
        self.notes_listbox.delete(0, tk.END)
        for n in self.notes:
            if query in n[1].lower() or query in n[2].lower():
                self.notes_listbox.insert(tk.END, f"{n[1]} - {n[2][:30]}")

    def bulk_export(self):
        if not self.is_premium:
            return
        folder = filedialog.askdirectory()
        if folder:
            for n in self.notes:
                filepath = os.path.join(folder, f"{n[1]}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(n[2])

    def toggle_theme(self):
        if not self.is_premium:
            return
        self.theme = "light" if self.theme == "dark" else "dark"
        bg_color = "#FFFFFF" if self.theme == "light" else "#121212"
        self.configure(bg=bg_color)

    def upgrade_account(self):
        upgrade_user(self.user_id)
        self.is_premium = 1
        self._apply_premium_state()
        messagebox.showinfo("Success", "🎉 You are now a Premium user!")

    def _apply_premium_state(self):
        if self.is_premium:
            self.export_btn.state(["!disabled"])
            self.upgrade_btn.pack_forget()
            self.sync_status.config(text="☁ Online", fg="#4CAF50")
        else:
            self.export_btn.state(["disabled"])
            self.sync_status.config(text="☁ Offline", fg="#F44336")

    def logout(self):
        self.destroy()
        from login import LoginApp
        LoginApp().mainloop()
