import tkinter as tk
from tkinter import ttk, messagebox

import bcrypt

from db import connect_db


# ==========================================================
#                    STAFF MANAGER
# ==========================================================

class StaffManager:

    def __init__(self):

        self.conn = connect_db()

        if not self.conn:
            raise Exception(
                "Database connection failed in StaffManager"
            )

        self.cur = self.conn.cursor()

    # ======================================================
    #                    REGISTER STAFF
    # ======================================================

    def register_staff(self, username, password, role):

        try:

            # Hash password before storing it
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            )

            self.cur.execute(
                """
                INSERT INTO staff
                (
                    username,
                    password,
                    role
                )
                VALUES (%s, %s, %s)
                """,
                (
                    username,
                    hashed_password.decode("utf-8"),
                    role
                )
            )

            self.conn.commit()

            return True, "Staff registered successfully."

        except Exception as e:

            self.conn.rollback()

            print(
                "Error registering staff:",
                e
            )

            return False, str(e)

    # ======================================================
    #                    LOGIN STAFF
    # ======================================================

    def login_staff(self, username, password):

        try:

            self.cur.execute(
                """
                SELECT
                    staff_id,
                    username,
                    password,
                    role
                FROM staff
                WHERE username = %s
                """,
                (username,)
            )

            staff = self.cur.fetchone()

            if not staff:
                return None

            staff_id = staff[0]
            stored_username = staff[1]
            stored_password = staff[2]
            role = staff[3]

            # Check password
            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            ):

                return {
                    "staff_id": staff_id,
                    "username": stored_username,
                    "role": role
                }

            return None

        except Exception as e:

            print(
                "Error logging in:",
                e
            )

            return None

    # ======================================================
    #                    CHECK USERNAME
    # ======================================================

    def username_exists(self, username):

        try:

            self.cur.execute(
                """
                SELECT staff_id
                FROM staff
                WHERE username = %s
                """,
                (username,)
            )

            return self.cur.fetchone() is not None

        except Exception as e:

            print(
                "Error checking username:",
                e
            )

            return False

    # ======================================================
    #                    CLOSE DATABASE
    # ======================================================

    def close(self):

        try:

            if self.cur:
                self.cur.close()

            if self.conn:
                self.conn.close()

        except Exception:
            pass

    # ======================================================
    #                    DESTRUCTOR
    # ======================================================

    def __del__(self):

        try:
            self.close()

        except Exception:
            pass


# ==========================================================
#                       STAFF GUI
# ==========================================================

class StaffGUI:

    def __init__(self):

        # --------------------------------------------------
        # Main Window
        # --------------------------------------------------

        self.root = tk.Tk()

        self.root.title(
            "StockFlow - Staff Login"
        )

        self.root.geometry(
            "500x550"
        )

        self.root.configure(
            bg="#F8F5F2"
        )

        self.root.resizable(
            False,
            False
        )

        # --------------------------------------------------
        # StockFlow Theme
        # --------------------------------------------------

        self.primary = "#5E548E"
        self.secondary = "#BE95C4"
        self.accent = "#E0B1CB"
        self.background = "#F8F5F2"
        self.danger = "#C44536"

        # --------------------------------------------------
        # Database Manager
        # --------------------------------------------------

        try:

            self.staff_manager = StaffManager()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

            self.root.destroy()

            return

        # --------------------------------------------------
        # Show Login
        # --------------------------------------------------

        self.login_screen()

        # --------------------------------------------------
        # Close Event
        # --------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

        self.root.mainloop()

    # ======================================================
    #                    CLEAR WINDOW
    # ======================================================

    def clear_window(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    # ======================================================
    #                    LOGIN SCREEN
    # ======================================================

    def login_screen(self):

        self.clear_window()

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        tk.Label(
            self.root,
            text="StockFlow",
            font=("Segoe UI", 28, "bold"),
            bg=self.background,
            fg=self.primary
        ).pack(
            pady=(45, 5)
        )

        tk.Label(
            self.root,
            text="Staff Login",
            font=("Segoe UI", 18, "bold"),
            bg=self.background,
            fg=self.primary
        ).pack(
            pady=(0, 25)
        )

        # --------------------------------------------------
        # Login Form
        # --------------------------------------------------

        form = tk.Frame(
            self.root,
            bg=self.background
        )

        form.pack()

        # --------------------------------------------------
        # Username
        # --------------------------------------------------

        tk.Label(
            form,
            text="Username",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.username_entry = tk.Entry(
            form,
            width=28,
            font=("Segoe UI", 11)
        )

        self.username_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )

        # --------------------------------------------------
        # Password
        # --------------------------------------------------

        tk.Label(
            form,
            text="Password",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.password_entry = tk.Entry(
            form,
            width=28,
            show="*",
            font=("Segoe UI", 11)
        )

        self.password_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=10
        )

        # --------------------------------------------------
        # Login Button
        # --------------------------------------------------

        tk.Button(
            self.root,
            text="Login",
            width=25,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.login
        ).pack(
            pady=(25, 10)
        )

        # --------------------------------------------------
        # Register Button
        # --------------------------------------------------

        tk.Button(
            self.root,
            text="Create Staff Account",
            width=25,
            bg=self.secondary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.register_screen
        ).pack(
            pady=5
        )

        # --------------------------------------------------
        # Enter Key
        # --------------------------------------------------

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.username_entry.focus()

    # ======================================================
    #                    LOGIN
    # ======================================================

    def login(self):

        username = (
            self.username_entry
            .get()
            .strip()
        )

        password = (
            self.password_entry
            .get()
            .strip()
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not username:

            messagebox.showwarning(
                "Missing Username",
                "Please enter your username."
            )

            self.username_entry.focus()

            return

        if not password:

            messagebox.showwarning(
                "Missing Password",
                "Please enter your password."
            )

            self.password_entry.focus()

            return

        # --------------------------------------------------
        # Verify Login
        # --------------------------------------------------

        staff = self.staff_manager.login_staff(
            username,
            password
        )

        if staff:

            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {staff['username']}!"
            )

            # Save staff information before closing
            # the login window.
            logged_in_staff = staff

            self.root.destroy()

            # ------------------------------------------------
            # Open Main POS
            # ------------------------------------------------

            try:

                from main_pos import open_pos

                open_pos(logged_in_staff)

            except ImportError:

                messagebox.showerror(
                    "Error",
                    "main_pos.py could not be imported."
                )

            except Exception as e:

                messagebox.showerror(
                    "Error",
                    f"Unable to open POS system.\n\n{e}"
                )

        else:

            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

            self.password_entry.delete(
                0,
                tk.END
            )

            self.password_entry.focus()

    # ======================================================
    #                    REGISTER SCREEN
    # ======================================================

    def register_screen(self):

        self.clear_window()

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        tk.Label(
            self.root,
            text="Staff Registration",
            font=("Segoe UI", 22, "bold"),
            bg=self.background,
            fg=self.primary
        ).pack(
            pady=(35, 25)
        )

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        form = tk.Frame(
            self.root,
            bg=self.background
        )

        form.pack()

        # --------------------------------------------------
        # Username
        # --------------------------------------------------

        tk.Label(
            form,
            text="Username",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.reg_username = tk.Entry(
            form,
            width=28,
            font=("Segoe UI", 11)
        )

        self.reg_username.grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )

        # --------------------------------------------------
        # Password
        # --------------------------------------------------

        tk.Label(
            form,
            text="Password",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.reg_password = tk.Entry(
            form,
            width=28,
            show="*",
            font=("Segoe UI", 11)
        )

        self.reg_password.grid(
            row=1,
            column=1,
            padx=10,
            pady=10
        )

        # --------------------------------------------------
        # Role
        # --------------------------------------------------

        tk.Label(
            form,
            text="Role",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.role = ttk.Combobox(
            form,
            values=[
                "Admin",
                "Cashier"
            ],
            state="readonly",
            width=25
        )

        self.role.grid(
            row=2,
            column=1,
            padx=10,
            pady=10
        )

        self.role.current(1)

        # --------------------------------------------------
        # Register Button
        # --------------------------------------------------

        tk.Button(
            self.root,
            text="Register Staff",
            width=25,
            bg=self.secondary,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.register_staff
        ).pack(
            pady=(25, 10)
        )

        # --------------------------------------------------
        # Back Button
        # --------------------------------------------------

        tk.Button(
            self.root,
            text="Back to Login",
            width=25,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.login_screen
        ).pack(
            pady=5
        )

        self.reg_username.focus()

    # ======================================================
    #                    REGISTER STAFF
    # ======================================================

    def register_staff(self):

        username = (
            self.reg_username
            .get()
            .strip()
        )

        password = (
            self.reg_password
            .get()
            .strip()
        )

        role = (
            self.role
            .get()
            .strip()
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not username:

            messagebox.showwarning(
                "Missing Username",
                "Please enter a username."
            )

            self.reg_username.focus()

            return

        if not password:

            messagebox.showwarning(
                "Missing Password",
                "Please enter a password."
            )

            self.reg_password.focus()

            return

        if not role:

            messagebox.showwarning(
                "Missing Role",
                "Please select a role."
            )

            return

        if len(username) < 3:

            messagebox.showwarning(
                "Invalid Username",
                "Username must contain at least 3 characters."
            )

            return

        if len(password) < 4:

            messagebox.showwarning(
                "Invalid Password",
                "Password must contain at least 4 characters."
            )

            return

        # --------------------------------------------------
        # Check Duplicate Username
        # --------------------------------------------------

        if self.staff_manager.username_exists(
            username
        ):

            messagebox.showerror(
                "Username Exists",
                "This username is already registered."
            )

            return

        # --------------------------------------------------
        # Register Staff
        # --------------------------------------------------

        success, message = (
            self.staff_manager.register_staff(
                username,
                password,
                role
            )
        )

        if success:

            messagebox.showinfo(
                "Registration Successful",
                message
            )

            self.login_screen()

        else:

            messagebox.showerror(
                "Registration Failed",
                message
            )

    # ======================================================
    #                    CLOSE WINDOW
    # ======================================================

    def close_window(self):

        try:

            self.staff_manager.close()

        except Exception:
            pass

        self.root.destroy()


# ==========================================================
#                    START APPLICATION
# ==========================================================

if __name__ == "__main__":

    StaffGUI()