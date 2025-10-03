import tkinter as tk
from tkinter import ttk, messagebox
from DB import register_user, login_user, init_db
from UI import NotesApp

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Encrypted Notes Keeper - Login")
        self.geometry("400x450")
        self.configure(bg="#121212")

        # Initialize database at app start
        init_db()

        # Centering content
        container = tk.Frame(self, bg="#121212")
        container.pack(expand=True)

        # Branding
        tk.Label(container, text="🔒", font=("Segoe UI", 40), bg="#121212", fg="#1E88E5").pack(pady=(10, 5))
        tk.Label(container, text="Encrypted Notes Keeper",
                 font=("Segoe UI", 16, "bold"), bg="#121212", fg="white").pack(pady=(0, 20))

        # Username
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(container, textvariable=self.username_var, font=("Segoe UI", 11))
        username_entry.pack(pady=10, ipady=5, ipadx=5, fill="x", padx=40)
        username_entry.insert(0, "Username")

        # Password
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(container, textvariable=self.password_var, font=("Segoe UI", 11), show="*")
        self.password_entry.pack(pady=10, ipady=5, ipadx=5, fill="x", padx=40)
        self.password_entry.insert(0, "Password")

        # Login Button
        login_btn = ttk.Button(container, text="Login", command=self.login_user_action)
        login_btn.pack(pady=20, ipadx=10, ipady=5)

        # Register Button
        register_btn = ttk.Button(container, text="Register", command=self.register_user_action)
        register_btn.pack(ipadx=10, ipady=5)

    # ---------------- Actions ----------------
    def login_user_action(self):
        username = self.username_var.get()
        password = self.password_var.get()
        result = login_user(username, password)
        if result:
            user_id, is_premium = result
            self.destroy()
            NotesApp(user_id, username, is_premium).mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register_user_action(self):
        username = self.username_var.get()
        password = self.password_var.get()
        success, msg = register_user(username, password)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    LoginApp().mainloop()
