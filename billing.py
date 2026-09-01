import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_db


# ==========================================================
#                    BILLING MANAGER
# ==========================================================

class BillingManager:

    def __init__(self):
        self.conn = connect_db()

        if not self.conn:
            raise Exception("Database connection failed in BillingManager")

        self.cur = self.conn.cursor()

    # ------------------------------------------------------
    # Get all customers
    # ------------------------------------------------------

    def get_all_customers(self):

        try:
            self.cur.execute("""
                SELECT customer_id, customer_name
                FROM customers
                ORDER BY customer_name
            """)

            return self.cur.fetchall()

        except Exception as e:
            print("Error fetching customers:", e)
            return []

    # ------------------------------------------------------
    # Get all products
    # ------------------------------------------------------

    def get_all_products(self):

        try:
            self.cur.execute("""
                SELECT product_number,
                       product_description,
                       product_quantity,
                       product_price
                FROM products
                ORDER BY product_description
            """)

            return self.cur.fetchall()

        except Exception as e:
            print("Error fetching products:", e)
            return []

    # ------------------------------------------------------
    # Get product by product number
    # ------------------------------------------------------

    def get_product(self, product_number):

        try:
            self.cur.execute("""
                SELECT product_number,
                       product_description,
                       product_quantity,
                       product_price
                FROM products
                WHERE product_number = %s
            """, (product_number,))

            return self.cur.fetchone()

        except Exception as e:
            print("Error fetching product:", e)
            return None

    # ------------------------------------------------------
    # Create Bill
    # ------------------------------------------------------

    def create_bill(self, customer_id, staff_id, items, discount_percent):

        if not items:
            raise ValueError("No products added to the bill.")

        try:

            # ----------------------------------------------
            # Calculate subtotal
            # ----------------------------------------------

            subtotal = 0.0

            for item in items:

                quantity = int(item["quantity"])
                price = float(item["price"])

                if quantity <= 0:
                    raise ValueError("Quantity must be greater than zero.")

                subtotal += price * quantity

            # ----------------------------------------------
            # Validate discount
            # ----------------------------------------------

            discount_percent = float(discount_percent)

            if discount_percent < 0 or discount_percent > 100:
                raise ValueError(
                    "Discount must be between 0 and 100."
                )

            discount_amount = subtotal * discount_percent / 100

            final_total = subtotal - discount_amount

            # ----------------------------------------------
            # Create Bill
            # ----------------------------------------------

            self.cur.execute("""
                INSERT INTO billing
                (
                    customer_id,
                    staff_id,
                    subtotal,
                    discount_percent,
                    discount_amount,
                    final_total
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING bill_id
            """, (
                customer_id,
                staff_id,
                subtotal,
                discount_percent,
                discount_amount,
                final_total
            ))

            bill_id = self.cur.fetchone()[0]

            # ----------------------------------------------
            # Process every product
            # ----------------------------------------------

            for item in items:

                product_number = item["product_number"]
                quantity = int(item["quantity"])
                price = float(item["price"])

                # ------------------------------------------
                # Check current stock
                # ------------------------------------------

                self.cur.execute("""
                    SELECT product_description,
                           product_quantity
                    FROM products
                    WHERE product_number = %s
                    FOR UPDATE
                """, (product_number,))

                product = self.cur.fetchone()

                if product is None:
                    raise ValueError(
                        f"Product ID {product_number} was not found."
                    )

                product_name = product[0]
                current_stock = int(product[1])

                if quantity > current_stock:
                    raise ValueError(
                        f"Insufficient stock for {product_name}.\n"
                        f"Available stock: {current_stock}"
                    )

                # ------------------------------------------
                # Insert billing item
                # ------------------------------------------

                item_total = price * quantity

                self.cur.execute("""
                    INSERT INTO billing_items
                    (
                        bill_id,
                        product_number,
                        quantity,
                        price,
                        total
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    bill_id,
                    product_number,
                    quantity,
                    price,
                    item_total
                ))

                # ------------------------------------------
                # Reduce stock ONCE
                # ------------------------------------------

                self.cur.execute("""
                    UPDATE products
                    SET product_quantity =
                        product_quantity - %s
                    WHERE product_number = %s
                """, (
                    quantity,
                    product_number
                ))

            # ----------------------------------------------
            # Commit everything
            # ----------------------------------------------

            self.conn.commit()

            return {
                "bill_id": bill_id,
                "subtotal": subtotal,
                "discount": discount_amount,
                "final_total": final_total
            }

        except Exception as e:

            self.conn.rollback()

            print("Billing Error:", e)

            raise

    # ------------------------------------------------------
    # Close database
    # ------------------------------------------------------

    def close(self):

        try:

            if self.cur:
                self.cur.close()

            if self.conn:
                self.conn.close()

        except Exception:
            pass

    def __del__(self):
        self.close()


# ==========================================================
#                    BILLING GUI
# ==========================================================

class BillingGUI:

    def __init__(self):

        self.manager = BillingManager()

        # --------------------------------------------------
        # Main Window
        # --------------------------------------------------

        self.root = tk.Tk()

        self.root.title("StockFlow - Billing")

        self.root.geometry("1200x720")

        self.root.configure(bg="#F8F5F2")

        self.root.resizable(False, False)

        # --------------------------------------------------
        # Theme Colors
        # --------------------------------------------------

        self.primary = "#5E548E"
        self.secondary = "#BE95C4"
        self.button = "#BE95C4"
        self.accent = "#E0B1CB"
        self.danger = "#C44536"
        self.background = "#F8F5F2"

        # --------------------------------------------------
        # Data
        # --------------------------------------------------

        self.customer_map = {}
        self.product_map = {}

        self.create_widgets()

        self.load_customers()

        self.load_products()

        # Close event
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        self.root.mainloop()

    # ======================================================
    #                    CREATE WIDGETS
    # ======================================================

    def create_widgets(self):

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        tk.Label(
            self.root,
            text="Billing Management",
            font=("Segoe UI", 22, "bold"),
            bg=self.background,
            fg=self.primary
        ).pack(pady=15)

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        form = tk.Frame(
            self.root,
            bg=self.background
        )

        form.pack(pady=5)

        # --------------------------------------------------
        # Customer
        # --------------------------------------------------

        tk.Label(
            form,
            text="Customer",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=7,
            sticky="e"
        )

        self.customer_combo = ttk.Combobox(
            form,
            width=35,
            state="readonly"
        )

        self.customer_combo.grid(
            row=0,
            column=1,
            padx=10,
            pady=7
        )

        # --------------------------------------------------
        # Staff ID
        # --------------------------------------------------

        tk.Label(
            form,
            text="Staff ID",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=7,
            sticky="e"
        )

        self.staff_id_entry = tk.Entry(
            form,
            width=20
        )

        self.staff_id_entry.grid(
            row=0,
            column=3,
            padx=10,
            pady=7
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
            pady=7,
            sticky="e"
        )

        self.product_combo = ttk.Combobox(
            form,
            width=35,
            state="readonly"
        )

        self.product_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=7
        )

        # --------------------------------------------------
        # Quantity
        # --------------------------------------------------

        tk.Label(
            form,
            text="Quantity",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=7,
            sticky="e"
        )

        self.quantity_entry = tk.Entry(
            form,
            width=20
        )

        self.quantity_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=7
        )

        # --------------------------------------------------
        # Buttons
        # --------------------------------------------------

        button_frame = tk.Frame(
            self.root,
            bg=self.background
        )

        button_frame.pack(pady=12)

        tk.Button(
            button_frame,
            text="Add To Bill",
            width=18,
            bg=self.button,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.add_to_bill
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Remove Item",
            width=18,
            bg=self.danger,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.remove_item
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Clear Bill",
            width=18,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.clear_bill
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        # --------------------------------------------------
        # Billing Table
        # --------------------------------------------------

        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "Product ID",
                "Product",
                "Quantity",
                "Price",
                "Total"
            ),
            show="headings",
            height=12
        )

        self.tree.heading(
            "Product ID",
            text="Product ID"
        )

        self.tree.heading(
            "Product",
            text="Product"
        )

        self.tree.heading(
            "Quantity",
            text="Quantity"
        )

        self.tree.heading(
            "Price",
            text="Price"
        )

        self.tree.heading(
            "Total",
            text="Total"
        )

        self.tree.column(
            "Product ID",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "Product",
            width=350
        )

        self.tree.column(
            "Quantity",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "Price",
            width=150,
            anchor="center"
        )

        self.tree.column(
            "Total",
            width=150,
            anchor="center"
        )

        self.tree.pack(
            fill="x",
            padx=20,
            pady=15
        )

        # ==================================================
        # Summary
        # ==================================================

        summary = tk.Frame(
            self.root,
            bg=self.background
        )

        summary.pack(pady=5)

        # --------------------------------------------------
        # Subtotal
        # --------------------------------------------------

        tk.Label(
            summary,
            text="Subtotal",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5
        )

        self.subtotal = tk.StringVar(
            value="0.00"
        )

        tk.Entry(
            summary,
            textvariable=self.subtotal,
            state="readonly",
            width=18,
            justify="center"
        ).grid(
            row=0,
            column=1,
            padx=10
        )

        # --------------------------------------------------
        # Discount
        # --------------------------------------------------

        tk.Label(
            summary,
            text="Discount (%)",
            font=("Segoe UI", 11),
            bg=self.background
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=5
        )

        self.discount = tk.Entry(
            summary,
            width=20,
            justify="center"
        )

        self.discount.grid(
            row=1,
            column=1,
            padx=10
        )

        # --------------------------------------------------
        # Final Amount
        # --------------------------------------------------

        tk.Label(
            summary,
            text="Final Amount",
            font=("Segoe UI", 11, "bold"),
            bg=self.background,
            fg=self.primary
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=5
        )

        self.final_amount = tk.StringVar(
            value="0.00"
        )

        tk.Entry(
            summary,
            textvariable=self.final_amount,
            state="readonly",
            width=18,
            justify="center",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=2,
            column=1,
            padx=10
        )

        # --------------------------------------------------
        # Generate Bill
        # --------------------------------------------------

        tk.Button(
            self.root,
            text="Generate Bill",
            width=25,
            bg=self.primary,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self.generate_bill
        ).pack(pady=15)

        # --------------------------------------------------
        # Discount calculation
        # --------------------------------------------------

        self.discount.bind(
            "<KeyRelease>",
            lambda event: self.calculate_total()
        )

    # ======================================================
    #                    LOAD CUSTOMERS
    # ======================================================

    def load_customers(self):

        try:

            customers = self.manager.get_all_customers()

            self.customer_map.clear()

            display_values = []

            for customer_id, customer_name in customers:

                display = f"{customer_id} - {customer_name}"

                self.customer_map[display] = customer_id

                display_values.append(display)

            self.customer_combo["values"] = display_values

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ======================================================
    #                    LOAD PRODUCTS
    # ======================================================

    def load_products(self):

        try:

            products = self.manager.get_all_products()

            self.product_map.clear()

            display_values = []

            for product_number, description, quantity, price in products:

                display = (
                    f"{product_number} - "
                    f"{description}"
                )

                self.product_map[display] = {
                    "product_number": product_number,
                    "description": description,
                    "stock": quantity,
                    "price": price
                }

                display_values.append(display)

            self.product_combo["values"] = display_values

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ======================================================
    #                    ADD TO BILL
    # ======================================================

    def add_to_bill(self):

        product_display = self.product_combo.get()

        quantity_text = self.quantity_entry.get().strip()

        if product_display == "":
            messagebox.showwarning(
                "Warning",
                "Please select a product."
            )
            return

        if quantity_text == "":
            messagebox.showwarning(
                "Warning",
                "Please enter quantity."
            )
            return

        try:

            quantity = int(quantity_text)

            if quantity <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Quantity",
                "Quantity must be a positive whole number."
            )

            return

        product = self.product_map.get(
            product_display
        )

        if not product:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        # --------------------------------------------------
        # Check stock
        # --------------------------------------------------

        current_product = self.manager.get_product(
            product["product_number"]
        )

        if current_product is None:

            messagebox.showerror(
                "Error",
                "Product not found in database."
            )

            return

        current_stock = int(
            current_product[2]
        )

        price = float(
            current_product[3]
        )

        if quantity > current_stock:

            messagebox.showerror(
                "Stock Error",
                f"Only {current_stock} units are available."
            )

            return

        # --------------------------------------------------
        # Check if product already exists in bill
        # --------------------------------------------------

        for row in self.tree.get_children():

            values = self.tree.item(row)["values"]

            existing_product_id = int(
                values[0]
            )

            if existing_product_id == int(
                product["product_number"]
            ):

                existing_quantity = int(
                    values[2]
                )

                new_quantity = (
                    existing_quantity + quantity
                )

                if new_quantity > current_stock:

                    messagebox.showerror(
                        "Stock Error",
                        f"Only {current_stock} units are available."
                    )

                    return

                total = price * new_quantity

                self.tree.item(
                    row,
                    values=(
                        product["product_number"],
                        product["description"],
                        new_quantity,
                        f"{price:.2f}",
                        f"{total:.2f}"
                    )
                )

                self.calculate_total()

                self.quantity_entry.delete(
                    0,
                    tk.END
                )

                return

        # --------------------------------------------------
        # Add new item
        # --------------------------------------------------

        total = price * quantity

        self.tree.insert(
            "",
            tk.END,
            values=(
                product["product_number"],
                product["description"],
                quantity,
                f"{price:.2f}",
                f"{total:.2f}"
            )
        )

        self.calculate_total()

        self.quantity_entry.delete(
            0,
            tk.END
        )

    # ======================================================
    #                    REMOVE ITEM
    # ======================================================

    def remove_item(self):

        selected = self.tree.focus()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an item to remove."
            )

            return

        self.tree.delete(
            selected
        )

        self.calculate_total()

    # ======================================================
    #                    CALCULATE TOTAL
    # ======================================================

    def calculate_total(self):

        subtotal = 0.0

        for row in self.tree.get_children():

            values = self.tree.item(row)["values"]

            subtotal += float(
                values[4]
            )

        self.subtotal.set(
            f"{subtotal:.2f}"
        )

        # --------------------------------------------------
        # Discount
        # --------------------------------------------------

        try:

            discount = float(
                self.discount.get() or 0
            )

            if discount < 0:
                discount = 0

            if discount > 100:
                discount = 100

        except ValueError:

            discount = 0

        final_amount = (
            subtotal -
            (subtotal * discount / 100)
        )

        self.final_amount.set(
            f"{final_amount:.2f}"
        )

    # ======================================================
    #                    GENERATE BILL
    # ======================================================

    def generate_bill(self):

        # --------------------------------------------------
        # Customer
        # --------------------------------------------------

        customer_display = (
            self.customer_combo.get()
        )

        if customer_display == "":

            messagebox.showwarning(
                "Warning",
                "Please select a customer."
            )

            return

        customer_id = self.customer_map.get(
            customer_display
        )

        if customer_id is None:

            messagebox.showerror(
                "Error",
                "Invalid customer selection."
            )

            return

        # --------------------------------------------------
        # Staff
        # --------------------------------------------------

        staff_text = (
            self.staff_id_entry.get().strip()
        )

        if staff_text == "":

            messagebox.showwarning(
                "Warning",
                "Please enter Staff ID."
            )

            return

        try:

            staff_id = int(staff_text)

        except ValueError:

            messagebox.showerror(
                "Invalid Staff ID",
                "Staff ID must be a number."
            )

            return

        # --------------------------------------------------
        # Items
        # --------------------------------------------------

        if len(
            self.tree.get_children()
        ) == 0:

            messagebox.showwarning(
                "Warning",
                "Please add at least one product."
            )

            return

        # --------------------------------------------------
        # Discount
        # --------------------------------------------------

        discount_text = (
            self.discount.get().strip()
        )

        if discount_text == "":
            discount_text = "0"

        try:

            discount = float(
                discount_text
            )

            if discount < 0 or discount > 100:

                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Discount",
                "Discount must be between 0 and 100."
            )

            return

        # --------------------------------------------------
        # Prepare items
        # --------------------------------------------------

        items = []

        for row in self.tree.get_children():

            values = self.tree.item(row)["values"]

            items.append({
                "product_number": int(values[0]),
                "description": values[1],
                "quantity": int(values[2]),
                "price": float(values[3])
            })

        # --------------------------------------------------
        # Create bill
        # --------------------------------------------------

        try:

            bill = self.manager.create_bill(
                customer_id,
                staff_id,
                items,
                discount
            )

            # ------------------------------------------------
            # Create invoice
            # ------------------------------------------------

            invoice = ""

            invoice += "=" * 55 + "\n"
            invoice += "                    STOCKFLOW\n"
            invoice += "                 BILLING INVOICE\n"
            invoice += "=" * 55 + "\n\n"

            invoice += (
                f"Bill ID      : {bill['bill_id']}\n"
            )

            invoice += (
                f"Customer     : {customer_display}\n"
            )

            invoice += (
                f"Staff ID     : {staff_id}\n\n"
            )

            invoice += "-" * 55 + "\n"

            invoice += (
                f"{'Product':<25}"
                f"{'Qty':<8}"
                f"{'Price':<10}"
                f"{'Total':<10}\n"
            )

            invoice += "-" * 55 + "\n"

            for item in items:

                item_total = (
                    item["quantity"] *
                    item["price"]
                )

                invoice += (
                    f"{item['description'][:24]:<25}"
                    f"{item['quantity']:<8}"
                    f"{item['price']:<10.2f}"
                    f"{item_total:<10.2f}\n"
                )

            invoice += "-" * 55 + "\n"

            invoice += (
                f"Subtotal       : ₹ {bill['subtotal']:.2f}\n"
            )

            invoice += (
                f"Discount       : {discount:.2f}%\n"
            )

            invoice += (
                f"Discount Amount: ₹ {bill['discount']:.2f}\n"
            )

            invoice += (
                f"Final Amount   : ₹ {bill['final_total']:.2f}\n"
            )

            invoice += "\n"
            invoice += "=" * 55 + "\n"
            invoice += "              Thank You!\n"
            invoice += "              Visit Again.\n"
            invoice += "=" * 55

            messagebox.showinfo(
                "Bill Generated Successfully",
                invoice
            )

            # ------------------------------------------------
            # Clear after successful billing
            # ------------------------------------------------

            self.clear_bill()

            # Refresh products so stock values are current
            self.load_products()

        except Exception as e:

            messagebox.showerror(
                "Billing Error",
                str(e)
            )

    # ======================================================
    #                    CLEAR BILL
    # ======================================================

    def clear_bill(self):

        for row in self.tree.get_children():

            self.tree.delete(row)

        self.customer_combo.set("")

        self.product_combo.set("")

        self.quantity_entry.delete(
            0,
            tk.END
        )

        self.discount.delete(
            0,
            tk.END
        )

        self.subtotal.set(
            "0.00"
        )

        self.final_amount.set(
            "0.00"
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
#                    RUN BILLING
# ==========================================================

if __name__ == "__main__":
    BillingGUI()