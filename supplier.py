import tkinter as tk
from tkinter import ttk, messagebox

from db import connect_db


# ==========================================================
#                    SUPPLIER MANAGER
# ==========================================================

class SupplierManager:

    def __init__(self):

        self.conn = connect_db()

        if not self.conn:
            raise Exception(
                "Database connection failed in SupplierManager"
            )

        self.cur = self.conn.cursor()

    # ======================================================
    #                    ADD SUPPLIER
    # ======================================================

    def add_supplier(
        self,
        supplier_name,
        supplier_email,
        product_name,
        minimum_stock
    ):

        try:

            self.cur.execute("""
                INSERT INTO suppliers
                (
                    supplier_name,
                    supplier_email,
                    product_name,
                    minimum_stock
                )
                VALUES (%s, %s, %s, %s)
            """, (
                supplier_name,
                supplier_email,
                product_name,
                minimum_stock
            ))

            self.conn.commit()

            return True, "Supplier added successfully."

        except Exception as e:

            self.conn.rollback()

            print("Error adding supplier:", e)

            return False, str(e)

    # ======================================================
    #                    GET ALL SUPPLIERS
    # ======================================================

    def get_all_suppliers(self):

        try:

            self.cur.execute("""
                SELECT
                    supplier_id,
                    supplier_name,
                    supplier_email,
                    product_name,
                    minimum_stock
                FROM suppliers
                ORDER BY supplier_id
            """)

            return self.cur.fetchall()

        except Exception as e:

            print("Error fetching suppliers:", e)

            return []

    # ======================================================
    #                    GET ALL PRODUCTS
    # ======================================================

    def get_all_products(self):

        try:

            self.cur.execute("""
                SELECT
                    product_number,
                    product_description,
                    product_quantity
                FROM products
                ORDER BY product_description
            """)

            return self.cur.fetchall()

        except Exception as e:

            print("Error fetching products:", e)

            return []

    # ======================================================
    #                    GET SUPPLIER BY PRODUCT
    # ======================================================

    def get_supplier_by_product(self, product_name):

        try:

            self.cur.execute("""
                SELECT
                    supplier_name,
                    supplier_email,
                    minimum_stock
                FROM suppliers
                WHERE product_name = %s
            """, (product_name,))

            return self.cur.fetchone()

        except Exception as e:

            print("Error fetching supplier:", e)

            return None

    # ======================================================
    #                    UPDATE SUPPLIER
    # ======================================================

    def update_supplier(
        self,
        supplier_id,
        supplier_name,
        supplier_email,
        product_name,
        minimum_stock
    ):

        try:

            self.cur.execute("""
                UPDATE suppliers
                SET
                    supplier_name = %s,
                    supplier_email = %s,
                    product_name = %s,
                    minimum_stock = %s
                WHERE supplier_id = %s
            """, (
                supplier_name,
                supplier_email,
                product_name,
                minimum_stock,
                supplier_id
            ))

            self.conn.commit()

            return True, "Supplier updated successfully."

        except Exception as e:

            self.conn.rollback()

            print("Error updating supplier:", e)

            return False, str(e)

    # ======================================================
    #                    DELETE SUPPLIER
    # ======================================================

    def delete_supplier(self, supplier_id):

        try:

            self.cur.execute("""
                DELETE FROM suppliers
                WHERE supplier_id = %s
            """, (supplier_id,))

            self.conn.commit()

            return True, "Supplier deleted successfully."

        except Exception as e:

            self.conn.rollback()

            print("Error deleting supplier:", e)

            return False, str(e)

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

    def __del__(self):

        try:
            self.close()

        except Exception:
            pass


# ==========================================================
#                    SUPPLIER GUI
# ==========================================================

class SupplierGUI:

    def __init__(self, root):

        self.root = root

        # --------------------------------------------------
        # Window
        # --------------------------------------------------

        self.root.title(
            "StockFlow - Supplier Management"
        )

        self.root.geometry(
            "1100x700"
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
        # Manager
        # --------------------------------------------------

        try:

            self.manager = SupplierManager()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

            self.root.destroy()

            return

        # --------------------------------------------------
        # Product Mapping
        # --------------------------------------------------

        self.product_map = {}

        # --------------------------------------------------
        # Create GUI
        # --------------------------------------------------

        self.create_widgets()

        self.load_products()

        self.load_suppliers()

        # --------------------------------------------------
        # Close Event
        # --------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

    # ======================================================
    #                    CREATE WIDGETS
    # ======================================================

    def create_widgets(self):

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = tk.Label(
            self.root,
            text="Supplier Management",
            font=("Segoe UI", 22, "bold"),
            bg=self.background,
            fg=self.primary
        )

        title.pack(
            pady=15
        )

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        form = tk.Frame(
            self.root,
            bg=self.background
        )

        form.pack(
            pady=5
        )

        # --------------------------------------------------
        # Supplier Name
        # --------------------------------------------------

        tk.Label(
            form,
            text="Supplier Name",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=8,
            sticky="e"
        )

        self.name_entry = tk.Entry(
            form,
            width=30,
            font=("Segoe UI", 10)
        )

        self.name_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=8
        )

        # --------------------------------------------------
        # Supplier Email
        # --------------------------------------------------

        tk.Label(
            form,
            text="Supplier Email",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=8,
            sticky="e"
        )

        self.email_entry = tk.Entry(
            form,
            width=30,
            font=("Segoe UI", 10)
        )

        self.email_entry.grid(
            row=0,
            column=3,
            padx=10,
            pady=8
        )

        # --------------------------------------------------
        # Product
        # --------------------------------------------------

        tk.Label(
            form,
            text="Product",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8,
            sticky="e"
        )

        self.product_combo = ttk.Combobox(
            form,
            width=28,
            state="readonly"
        )

        self.product_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=8
        )

        # --------------------------------------------------
        # Minimum Stock
        # --------------------------------------------------

        tk.Label(
            form,
            text="Minimum Stock",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=8,
            sticky="e"
        )

        self.minimum_entry = tk.Entry(
            form,
            width=30,
            font=("Segoe UI", 10)
        )

        self.minimum_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=8
        )

        # ==================================================
        # BUTTONS
        # ==================================================

        button_frame = tk.Frame(
            self.root,
            bg=self.background
        )

        button_frame.pack(
            pady=12
        )

        # Add

        tk.Button(
            button_frame,
            text="Add Supplier",
            width=16,
            bg=self.secondary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.add_supplier
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        # Update

        tk.Button(
            button_frame,
            text="Update Supplier",
            width=16,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.update_supplier
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        # Delete

        tk.Button(
            button_frame,
            text="Delete Supplier",
            width=16,
            bg=self.danger,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.delete_supplier
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        # Clear

        tk.Button(
            button_frame,
            text="Clear",
            width=16,
            bg=self.accent,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.clear_entries
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        # Refresh

        tk.Button(
            button_frame,
            text="Refresh",
            width=16,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.refresh_data
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        # ==================================================
        # SUPPLIER TABLE
        # ==================================================

        table_frame = tk.Frame(
            self.root,
            bg=self.background
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "ID",
            "Supplier",
            "Email",
            "Product",
            "Minimum Stock"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=14
        )

        # --------------------------------------------------
        # Headings
        # --------------------------------------------------

        for column in columns:

            self.tree.heading(
                column,
                text=column
            )

        # --------------------------------------------------
        # Column Widths
        # --------------------------------------------------

        self.tree.column(
            "ID",
            width=60,
            anchor="center"
        )

        self.tree.column(
            "Supplier",
            width=180
        )

        self.tree.column(
            "Email",
            width=250
        )

        self.tree.column(
            "Product",
            width=230
        )

        self.tree.column(
            "Minimum Stock",
            width=130,
            anchor="center"
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

        # --------------------------------------------------
        # Select Event
        # --------------------------------------------------

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_supplier
        )

    # ======================================================
    #                    LOAD PRODUCTS
    # ======================================================

    def load_products(self):

        try:

            products = self.manager.get_all_products()

            self.product_map.clear()

            display_values = []

            for product_number, description, quantity in products:

                display = (
                    f"{product_number} - {description}"
                )

                # Store PRODUCT NAME, not product number
                self.product_map[display] = description

                display_values.append(
                    display
                )

            self.product_combo["values"] = display_values

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                f"Unable to load products.\n\n{e}"
            )

    # ======================================================
    #                    LOAD SUPPLIERS
    # ======================================================

    def load_suppliers(self):

        # Clear table

        for row in self.tree.get_children():

            self.tree.delete(row)

        # Get suppliers

        suppliers = self.manager.get_all_suppliers()

        # Insert suppliers

        for supplier in suppliers:

            self.tree.insert(
                "",
                tk.END,
                values=supplier
            )

    # ======================================================
    #                    ADD SUPPLIER
    # ======================================================

    def add_supplier(self):

        name = (
            self.name_entry
            .get()
            .strip()
        )

        email = (
            self.email_entry
            .get()
            .strip()
        )

        product_display = (
            self.product_combo
            .get()
            .strip()
        )

        minimum_text = (
            self.minimum_entry
            .get()
            .strip()
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not name:

            messagebox.showwarning(
                "Missing Information",
                "Please enter supplier name."
            )

            return

        if not email:

            messagebox.showwarning(
                "Missing Information",
                "Please enter supplier email."
            )

            return

        if not product_display:

            messagebox.showwarning(
                "Missing Information",
                "Please select a product."
            )

            return

        if not minimum_text:

            messagebox.showwarning(
                "Missing Information",
                "Please enter minimum stock."
            )

            return

        # --------------------------------------------------
        # Minimum Stock Validation
        # --------------------------------------------------

        try:

            minimum_stock = int(
                minimum_text
            )

            if minimum_stock < 0:

                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Minimum Stock",
                "Minimum stock must be a non-negative whole number."
            )

            return

        # --------------------------------------------------
        # Get Product Name
        # --------------------------------------------------

        product_name = self.product_map.get(
            product_display
        )

        if product_name is None:

            messagebox.showerror(
                "Error",
                "Invalid product selected."
            )

            return

        # --------------------------------------------------
        # Add to Database
        # --------------------------------------------------

        success, message = (
            self.manager.add_supplier(
                name,
                email,
                product_name,
                minimum_stock
            )
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_entries()

            self.load_suppliers()

        else:

            messagebox.showerror(
                "Database Error",
                message
            )

    # ======================================================
    #                    UPDATE SUPPLIER
    # ======================================================

    def update_supplier(self):

        selected = self.tree.focus()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a supplier first."
            )

            return

        values = self.tree.item(
            selected,
            "values"
        )

        supplier_id = values[0]

        name = (
            self.name_entry
            .get()
            .strip()
        )

        email = (
            self.email_entry
            .get()
            .strip()
        )

        product_display = (
            self.product_combo
            .get()
            .strip()
        )

        minimum_text = (
            self.minimum_entry
            .get()
            .strip()
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not name:

            messagebox.showwarning(
                "Missing Information",
                "Please enter supplier name."
            )

            return

        if not email:

            messagebox.showwarning(
                "Missing Information",
                "Please enter supplier email."
            )

            return

        if not product_display:

            messagebox.showwarning(
                "Missing Information",
                "Please select a product."
            )

            return

        try:

            minimum_stock = int(
                minimum_text
            )

            if minimum_stock < 0:

                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Minimum Stock",
                "Minimum stock must be a non-negative whole number."
            )

            return

        # --------------------------------------------------
        # Get Product Name
        # --------------------------------------------------

        product_name = self.product_map.get(
            product_display
        )

        if product_name is None:

            messagebox.showerror(
                "Error",
                "Invalid product selected."
            )

            return

        # --------------------------------------------------
        # Confirm
        # --------------------------------------------------

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Update this supplier?"
        )

        if not confirm:

            return

        # --------------------------------------------------
        # Update Database
        # --------------------------------------------------

        success, message = (
            self.manager.update_supplier(
                supplier_id,
                name,
                email,
                product_name,
                minimum_stock
            )
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_entries()

            self.load_suppliers()

        else:

            messagebox.showerror(
                "Database Error",
                message
            )

    # ======================================================
    #                    DELETE SUPPLIER
    # ======================================================

    def delete_supplier(self):

        selected = self.tree.focus()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a supplier first."
            )

            return

        values = self.tree.item(
            selected,
            "values"
        )

        supplier_id = values[0]

        supplier_name = values[1]

        # --------------------------------------------------
        # Confirm Delete
        # --------------------------------------------------

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete supplier '{supplier_name}'?"
        )

        if not confirm:

            return

        # --------------------------------------------------
        # Delete
        # --------------------------------------------------

        success, message = (
            self.manager.delete_supplier(
                supplier_id
            )
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.clear_entries()

            self.load_suppliers()

        else:

            messagebox.showerror(
                "Database Error",
                message
            )

    # ======================================================
    #                    SELECT SUPPLIER
    # ======================================================

    def select_supplier(
        self,
        event=None
    ):

        selected = self.tree.focus()

        if not selected:

            return

        values = self.tree.item(
            selected,
            "values"
        )

        # --------------------------------------------------
        # Clear Current Entries
        # --------------------------------------------------

        self.clear_entries(
            keep_product=True
        )

        # --------------------------------------------------
        # Supplier Name
        # --------------------------------------------------

        self.name_entry.insert(
            0,
            values[1]
        )

        # --------------------------------------------------
        # Email
        # --------------------------------------------------

        self.email_entry.insert(
            0,
            values[2]
        )

        # --------------------------------------------------
        # Product
        # --------------------------------------------------

        product_name = values[3]

        for display, name in self.product_map.items():

            if name == product_name:

                self.product_combo.set(
                    display
                )

                break

        # --------------------------------------------------
        # Minimum Stock
        # --------------------------------------------------

        self.minimum_entry.insert(
            0,
            values[4]
        )

    # ======================================================
    #                    CLEAR ENTRIES
    # ======================================================

    def clear_entries(
        self,
        keep_product=False
    ):

        self.name_entry.delete(
            0,
            tk.END
        )

        self.email_entry.delete(
            0,
            tk.END
        )

        self.minimum_entry.delete(
            0,
            tk.END
        )

        if not keep_product:

            self.product_combo.set("")

    # ======================================================
    #                    REFRESH
    # ======================================================

    def refresh_data(self):

        self.load_products()

        self.load_suppliers()

        self.clear_entries()

        messagebox.showinfo(
            "Refresh",
            "Supplier data refreshed successfully."
        )

    # ======================================================
    #                    CLOSE WINDOW
    # ======================================================

    def close_window(self):

        try:

            self.manager.close()

        except Exception:
            pass

        self.root.destroy()


# ==========================================================
#                    RUN SUPPLIER GUI
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    SupplierGUI(root)

    root.mainloop()