import tkinter as tk
from tkinter import messagebox


# ==========================================================
#                    OPEN MAIN POS
# ==========================================================

def open_pos(staff):

    root = tk.Tk()

    root.title(
        "StockFlow - Smart Retail & Inventory Management System"
    )

    root.geometry("900x600")

    root.configure(
        bg="#F8F5F2"
    )

    root.resizable(False, False)

    # ======================================================
    #                    THEME
    # ======================================================

    primary = "#5E548E"
    secondary = "#BE95C4"
    accent = "#E0B1CB"
    background = "#F8F5F2"
    danger = "#C44536"

    # ======================================================
    #                    HEADER
    # ======================================================

    header = tk.Frame(
        root,
        bg=primary,
        height=100
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)

    tk.Label(
        header,
        text="StockFlow",
        font=("Segoe UI", 28, "bold"),
        bg=primary,
        fg="white"
    ).pack(
        pady=(15, 0)
    )

    tk.Label(
        header,
        text="Smart Retail & Inventory Management System",
        font=("Segoe UI", 11),
        bg=primary,
        fg="white"
    ).pack()

    # ======================================================
    #                    USER INFORMATION
    # ======================================================

    user_frame = tk.Frame(
        root,
        bg=background
    )

    user_frame.pack(
        pady=20
    )

    tk.Label(
        user_frame,
        text=f"Logged in as: {staff['role']}",
        font=("Segoe UI", 12, "bold"),
        bg=background,
        fg=primary
    ).pack()

    tk.Label(
        user_frame,
        text=f"Staff ID: {staff['staff_id']}",
        font=("Segoe UI", 10),
        bg=background,
        fg="#555555"
    ).pack(
        pady=3
    )

    # ======================================================
    #                    BUTTON FRAME
    # ======================================================

    button_frame = tk.Frame(
        root,
        bg=background
    )

    button_frame.pack(
        pady=10
    )

    # ======================================================
    #                    OPEN PRODUCTS
    # ======================================================

    def open_products():

        try:

            import product

            product.ProductGUI()

        except Exception as e:

            messagebox.showerror(
                "Products Error",
                f"Unable to open Products.\n\n{e}"
        )

    # ======================================================
    #                    OPEN CUSTOMERS
    # ======================================================

    def open_customers():

        try:

           import customers

           customers.CustomerGUI()

        except Exception as e:

         messagebox.showerror(
            "Customers Error",
            f"Unable to open Customers.\n\n{e}"
        )

    # ======================================================
    #                    OPEN BILLING
    # ======================================================

    def open_billing():

        try:

            import billing

            billing.BillingGUI()

        except Exception as e:

         messagebox.showerror(
            "Billing Error",
            f"Unable to open Billing.\n\n{e}"
        )

    # ======================================================
    #                    OPEN SUPPLIERS
    # ======================================================

    def open_suppliers():

        try:

            import supplier

            supplier_window = tk.Toplevel(root)

            supplier.SupplierGUI(
                supplier_window
            )

        except Exception as e:

            messagebox.showerror(
                "Supplier Error",
                f"Unable to open Suppliers.\n\n{e}"
            )

    # ======================================================
    #                    PRODUCTS BUTTON
    # ======================================================

    tk.Button(
        button_frame,
        text="Products",
        width=25,
        height=2,
        bg=secondary,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=open_products
    ).grid(
        row=0,
        column=0,
        padx=15,
        pady=15
    )

    # ======================================================
    #                    CUSTOMERS BUTTON
    # ======================================================

    tk.Button(
        button_frame,
        text="Customers",
        width=25,
        height=2,
        bg=primary,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=open_customers
    ).grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    # ======================================================
    #                    BILLING BUTTON
    # ======================================================

    tk.Button(
        button_frame,
        text="Billing",
        width=25,
        height=2,
        bg=secondary,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=open_billing
    ).grid(
        row=1,
        column=0,
        padx=15,
        pady=15
    )

    # ======================================================
    #                    SUPPLIERS BUTTON
    # ======================================================

    tk.Button(
        button_frame,
        text="Suppliers",
        width=25,
        height=2,
        bg=primary,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=open_suppliers
    ).grid(
        row=1,
        column=1,
        padx=15,
        pady=15
    )

    # ======================================================
    #                    LOGOUT
    # ======================================================

    def logout():

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )

        if confirm:

            root.destroy()

            # Reopen staff login
            try:

                from staff import StaffGUI

                login_root = tk.Tk()

                StaffGUI(
                    login_root
                )

                login_root.mainloop()

            except Exception as e:

                messagebox.showerror(
                    "Logout Error",
                    str(e)
                )

    tk.Button(
        root,
        text="Logout",
        width=25,
        height=2,
        bg=danger,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=logout
    ).pack(
        pady=20
    )

    # ======================================================
    #                    MAIN LOOP
    # ======================================================

    root.mainloop()


# ==========================================================
#                    DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    # Temporary test staff
    test_staff = {
        "staff_id": 1,
        "role": "Admin"
    }

    open_pos(test_staff)