import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_db


class ProductManager:
    def __init__(self):
        self.conn = connect_db()
        if not self.conn:
            raise Exception("Database connection failed in ProductManager")
        self.cur = self.conn.cursor()

    def add_product(self, description, quantity, price, weight):
        try:
            self.cur.execute("""
                INSERT INTO products
                (product_description, product_quantity, product_price, product_weight)
                VALUES (%s, %s, %s, %s)
            """, (description, quantity, price, weight))

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error adding product:", e)
            raise

    def get_all_products(self):
        try:
            self.cur.execute("""
                SELECT *
                FROM products
                ORDER BY product_number
            """)
            return self.cur.fetchall()

        except Exception as e:
            print("Error fetching products:", e)
            return []

    def get_product(self, product_number):
        try:
            self.cur.execute("""
                SELECT *
                FROM products
                WHERE product_number = %s
            """, (product_number,))

            return self.cur.fetchone()

        except Exception as e:
            print("Error fetching product:", e)
            return None

    def update_product(self, product_number, field, new_value):
        allowed_fields = {
            "product_description",
            "product_quantity",
            "product_price",
            "product_weight"
        }

        if field not in allowed_fields:
            raise ValueError("Invalid field name")

        try:
            query = f"UPDATE products SET {field} = %s WHERE product_number = %s"
            self.cur.execute(query, (new_value, product_number))
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error updating product:", e)
            raise

    def delete_product(self, product_number):
        try:
            self.cur.execute("""
                DELETE FROM products
                WHERE product_number = %s
            """, (product_number,))

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            print("Error deleting product:", e)
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
        #               PRODUCT GUI - PART 1
        # =====================================================

class ProductGUI:

            def __init__(self):
                self.product_manager = ProductManager()

                self.root = tk.Tk()
                self.root.title("StockFlow - Product Management")
                self.root.geometry("1000x650")
                self.root.configure(bg="#F8F5F2")

                self.primary = "#5E548E"
                self.secondary = "#9F86C0"
                self.button = "#BE95C4"
                self.accent = "#E0B1CB"

                self.create_widgets()

                self.load_products()

                self.root.mainloop()

            # -----------------------------------

            def clear_entries(self):
                self.description.delete(0, tk.END)
                self.quantity.delete(0, tk.END)
                self.price.delete(0, tk.END)
                self.weight.delete(0, tk.END)

            # -----------------------------------

            def create_widgets(self):
                tk.Label(
                    self.root,
                    text="Product Management",
                    font=("Segoe UI", 22, "bold"),
                    bg="#F8F5F2",
                    fg=self.primary
                ).pack(pady=15)

                form = tk.Frame(self.root, bg="#F8F5F2")
                form.pack()

                tk.Label(form, text="Description", bg="#F8F5F2").grid(row=0, column=0, padx=5, pady=5)

                self.description = tk.Entry(form, width=30)
                self.description.grid(row=0, column=1)

                tk.Label(form, text="Quantity", bg="#F8F5F2").grid(row=1, column=0, padx=5, pady=5)

                self.quantity = tk.Entry(form, width=30)
                self.quantity.grid(row=1, column=1)

                tk.Label(form, text="Price", bg="#F8F5F2").grid(row=2, column=0, padx=5, pady=5)

                self.price = tk.Entry(form, width=30)
                self.price.grid(row=2, column=1)

                tk.Label(form, text="Weight", bg="#F8F5F2").grid(row=3, column=0, padx=5, pady=5)

                self.weight = tk.Entry(form, width=30)
                self.weight.grid(row=3, column=1)

                button_frame = tk.Frame(self.root, bg="#F8F5F2")
                button_frame.pack(pady=15)

                tk.Button(
                    button_frame,
                    text="Add Product",
                    width=15,
                    bg=self.button,
                    fg="white",
                    command=self.add_product
                ).grid(row=0, column=0, padx=5)

                tk.Button(
                    button_frame,
                    text="Clear",
                    width=15,
                    bg=self.primary,
                    fg="white",
                    command=self.clear_entries
                ).grid(row=0, column=1, padx=5)
                tk.Button(
                    button_frame,
                    text="Update Product",
                    width=15,
                    bg="#5E548E",
                    fg="white",
                    command=self.update_product
                ).grid(row=0, column=2, padx=5)

                tk.Button(
                    button_frame,
                    text="Delete Product",
                    width=15,
                    bg="#C44536",
                    fg="white",
                    command=self.delete_product
                ).grid(row=0, column=3, padx=5)

                self.tree = ttk.Treeview(
                    self.root,
                    columns=("ID", "Description", "Quantity", "Price", "Weight"),
                    show="headings",
                    height=15
                )

                self.tree.heading("ID", text="ID")
                self.tree.heading("Description", text="Description")
                self.tree.heading("Quantity", text="Quantity")
                self.tree.heading("Price", text="Price")
                self.tree.heading("Weight", text="Weight")

                self.tree.column("ID", width=70)
                self.tree.pack(fill="both", expand=True, padx=20, pady=10)
                self.selected_product = None

                # -----------------------------------
                # Load Products
                # -----------------------------------

            def load_products(self):

                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    products = self.product_manager.get_all_products()

                    for product in products:
                        self.tree.insert("", tk.END, values=product)

                # -----------------------------------
                # Add Product
                # -----------------------------------

            def add_product(self):

                    description = self.description.get().strip()
                    quantity = self.quantity.get().strip()
                    price = self.price.get().strip()
                    weight = self.weight.get().strip()

                    if description == "" or quantity == "" or price == "" or weight == "":
                        messagebox.showwarning(
                            "Warning",
                            "Please fill all fields."
                        )
                        return

                    try:

                        self.product_manager.add_product(
                            description,
                            int(quantity),
                            float(price),
                            float(weight)
                        )

                        messagebox.showinfo(
                            "Success",
                            "Product Added Successfully."
                        )

                        self.clear_entries()
                        self.load_products()

                    except Exception as e:

                        messagebox.showerror(
                            "Error",
                            str(e)
                        )

                # -----------------------------------
                # Select Product
                # -----------------------------------

            def select_product(self, event):

                    selected = self.tree.focus()

                    if not selected:
                        return

                    values = self.tree.item(selected, "values")

                    self.clear_entries()

                    self.description.insert(0, values[1])
                    self.quantity.insert(0, values[2])
                    self.price.insert(0, values[3])
                    self.weight.insert(0, values[4])

                    self.selected_product = values[0]

                    self.tree.bind("<<TreeviewSelect>>", self.select_product)

            # -----------------------------------
            # Update Product
            # -----------------------------------

            def update_product(self):

                if self.selected_product is None:
                    messagebox.showwarning(
                        "Warning",
                        "Please select a product first."
                    )
                    return

                try:

                    self.product_manager.update_product(
                        self.selected_product,
                        "product_description",
                        self.description.get()
                    )

                    self.product_manager.update_product(
                        self.selected_product,
                        "product_quantity",
                        int(self.quantity.get())
                    )

                    self.product_manager.update_product(
                        self.selected_product,
                        "product_price",
                        float(self.price.get())
                    )

                    self.product_manager.update_product(
                        self.selected_product,
                        "product_weight",
                        float(self.weight.get())
                    )

                    messagebox.showinfo(
                        "Success",
                        "Product Updated Successfully."
                    )

                    self.load_products()
                    self.clear_entries()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        str(e)
                    )

            # -----------------------------------
            # Delete Product
            # -----------------------------------

            def delete_product(self):

                if self.selected_product is None:
                    messagebox.showwarning(
                        "Warning",
                        "Please select a product first."
                    )
                    return

                answer = messagebox.askyesno(
                    "Delete",
                    "Are you sure you want to delete this product?"
                )

                if answer:

                    try:

                        self.product_manager.cur.execute(
                            "DELETE FROM products WHERE product_number=%s",
                            (self.selected_product,)
                        )

                        self.product_manager.conn.commit()

                        messagebox.showinfo(
                            "Success",
                            "Product Deleted Successfully."
                        )

                        self.selected_product = None

                        self.clear_entries()

                        self.load_products()

                    except Exception as e:

                        messagebox.showerror(
                            "Error",
                            str(e)
                        )
if __name__ == "__main__":
    ProductGUI()