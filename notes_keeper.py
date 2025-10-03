from DB import init_db
from login import LoginApp

if __name__ == "__main__":
    init_db()
    app = LoginApp()
    app.mainloop()
