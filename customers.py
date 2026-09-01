import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_db


class CustomerManager:
    def __init__(self):
        self.conn = connect_db()
        if not self.conn:
            raise Exception("Database connection failed in CustomerManager")
        self.cur = self.conn.cursor()

    def add_customer(self, name, contact, gender, age):
        try:
            self.cur.execute("""
                INSERT INTO customers
                (customer_name, customer_contact_number, customer_gender, customer_age)
                VALUES (%s, %s, %s, %s)
            """, (name, contact, gender, age))

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error adding customer:", e)
            raise

    def get_all_customers(self):
        try:
            self.cur.execute("""
                SELECT *
                FROM customers
                ORDER BY customer_id
            """)

            return self.cur.fetchall()

        except Exception as e:
            print("Error fetching customers:", e)
            return []

    def get_customer(self, customer_id):
        try:
            self.cur.execute("""
                SELECT *
                FROM customers
                WHERE customer_id = %s
            """, (customer_id,))

            return self.cur.fetchone()

        except Exception as e:
            print("Error fetching customer:", e)
            return None

    def update_customer(self, customer_id, field, new_value):
        allowed_fields = {
            "customer_name",
            "customer_contact_number",
            "customer_gender",
            "customer_age"
        }

        if field not in allowed_fields:
            raise ValueError("Invalid field name")

        try:
            query = f"UPDATE customers SET {field} = %s WHERE customer_id = %s"
            self.cur.execute(query, (new_value, customer_id))

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error updating customer:", e)
            raise

    def delete_customer(self, customer_id):
        try:
            self.cur.execute("""
                DELETE FROM customers
                WHERE customer_id = %s
            """, (customer_id,))

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error deleting customer:", e)
            raise

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()

            if self.conn:
                self.conn.close()

        except:
            pass

# =====================================================
#              CUSTOMER GUI - PART 1
# =====================================================

import tkinter as tk
from tkinter import ttk, messagebox


class CustomerGUI:

    def __init__(self):

        self.customer_manager = CustomerManager()

        self.root = tk.Tk()
        self.root.title("StockFlow - Customer Management")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F8F5F2")
        self.root.resizable(False, False)

        self.primary = "#5E548E"
        self.button = "#BE95C4"

        self.selected_customer = None

        self.create_widgets()
        self.load_customers()

        self.root.mainloop()

    # ----------------------------------------

    def clear_entries(self):

        self.name.delete(0, tk.END)
        self.contact.delete(0, tk.END)
        self.gender.set("")
        self.age.delete(0, tk.END)

    # ----------------------------------------

    def create_widgets(self):

        title = tk.Label(
            self.root,
            text="Customer Management",
            font=("Segoe UI", 22, "bold"),
            fg=self.primary,
            bg="#F8F5F2"
        )
        title.pack(pady=15)

        form = tk.Frame(self.root, bg="#F8F5F2")
        form.pack(pady=10)

        tk.Label(form, text="Customer Name", bg="#F8F5F2").grid(row=0, column=0, padx=10, pady=8)

        self.name = tk.Entry(form, width=30)
        self.name.grid(row=0, column=1)

        tk.Label(form, text="Contact Number", bg="#F8F5F2").grid(row=1, column=0, padx=10, pady=8)

        self.contact = tk.Entry(form, width=30)
        self.contact.grid(row=1, column=1)

        tk.Label(form, text="Gender", bg="#F8F5F2").grid(row=2, column=0, padx=10, pady=8)

        self.gender = ttk.Combobox(
            form,
            values=["Male", "Female", "Other"],
            state="readonly",
            width=27
        )
        self.gender.grid(row=2, column=1)

        tk.Label(form, text="Age", bg="#F8F5F2").grid(row=3, column=0, padx=10, pady=8)

        self.age = tk.Entry(form, width=30)
        self.age.grid(row=3, column=1)

        button_frame = tk.Frame(self.root, bg="#F8F5F2")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add Customer",
            width=15,
            bg=self.button,
            fg="white",
            command=self.add_customer
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Update",
            width=15,
            bg="#5E548E",
            fg="white",
            command=self.update_customer
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Delete",
            width=15,
            bg="#C44536",
            fg="white",
            command=self.delete_customer
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="Clear",
            width=15,
            bg="#777777",
            fg="white",
            command=self.clear_entries
        ).grid(row=0, column=3, padx=5)

        self.tree = ttk.Treeview(
            self.root,
            columns=("ID", "Name", "Contact", "Gender", "Age"),
            show="headings",
            height=15
        )

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Age", text="Age")

        self.tree.column("ID", width=70)
        self.tree.column("Name", width=220)
        self.tree.column("Contact", width=170)
        self.tree.column("Gender", width=120)
        self.tree.column("Age", width=80)

        self.tree.pack(fill="both", expand=True, padx=20, pady=15)

        self.tree.bind("<<TreeviewSelect>>", self.select_customer)

    # ----------------------------------------

    def load_customers(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        customers = self.customer_manager.get_all_customers()

        for customer in customers:
            self.tree.insert("", tk.END, values=customer)

    # ----------------------------------------
    # Add Customer
    # ----------------------------------------

    def add_customer(self):

        name = self.name.get().strip()
        contact = self.contact.get().strip()
        gender = self.gender.get().strip()
        age = self.age.get().strip()

        if name == "" or contact == "" or gender == "" or age == "":
            messagebox.showwarning(
                "Warning",
                "Please fill all fields."
            )
            return

        try:

            self.customer_manager.add_customer(
                name,
                contact,
                gender,
                int(age)
            )

            messagebox.showinfo(
                "Success",
                "Customer Added Successfully."
            )

            self.clear_entries()
            self.load_customers()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ----------------------------------------
    # Select Customer
    # ----------------------------------------

    def select_customer(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(selected, "values")

        self.selected_customer = values[0]

        self.clear_entries()

        self.name.insert(0, values[1])
        self.contact.insert(0, values[2])
        self.gender.set(values[3])
        self.age.insert(0, values[4])

    # ----------------------------------------
    # Update Customer
    # ----------------------------------------

    def update_customer(self):

        if self.selected_customer is None:
            messagebox.showwarning(
                "Warning",
                "Please select a customer."
            )
            return

        try:

            self.customer_manager.update_customer(
                self.selected_customer,
                "customer_name",
                self.name.get()
            )

            self.customer_manager.update_customer(
                self.selected_customer,
                "customer_contact_number",
                self.contact.get()
            )

            self.customer_manager.update_customer(
                self.selected_customer,
                "customer_gender",
                self.gender.get()
            )

            self.customer_manager.update_customer(
                self.selected_customer,
                "customer_age",
                int(self.age.get())
            )

            messagebox.showinfo(
                "Success",
                "Customer Updated Successfully."
            )

            self.clear_entries()
            self.load_customers()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ----------------------------------------
    # Delete Customer
    # ----------------------------------------

    def delete_customer(self):

        if self.selected_customer is None:
            messagebox.showwarning(
                "Warning",
                "Please select a customer."
            )
            return

        answer = messagebox.askyesno(
            "Delete Customer",
            "Are you sure you want to delete this customer?"
        )

        if answer:

            try:

                self.customer_manager.cur.execute(
                    "DELETE FROM customers WHERE customer_id=%s",
                    (self.selected_customer,)
                )

                self.customer_manager.conn.commit()

                messagebox.showinfo(
                    "Deleted",
                    "Customer Deleted Successfully."
                )

                self.selected_customer = None

                self.clear_entries()
                self.load_customers()

            except Exception as e:
                messagebox.showerror("Error", str(e))
if __name__ == "__main__":
    CustomerGUI()