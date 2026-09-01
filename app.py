from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
from decimal import Decimal
from db import connect_db

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def close_db(conn, cur=None):
    try:
        if cur:
            cur.close()
    finally:
        if conn:
            conn.close()


def table_columns(cur, table_name):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
    """, (table_name,))
    return {row[0] for row in cur.fetchall()}


def json_number(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


@app.route("/")
def home():
    return jsonify({"success": True, "message": "StockFlow API is running successfully!"})


@app.route("/api/test-db", methods=["GET"])
def test_database():
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        return jsonify({"success": True, "message": "PostgreSQL database connected successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/register", methods=["POST"])
def register():
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")).strip()
        role = str(data.get("role", "")).strip()
        if not username or not password or not role:
            return jsonify({"success": False, "message": "Username, password and role are required."}), 400
        conn = connect_db()
        if not conn:
            return jsonify({"success": False, "message": "Database connection failed."}), 500
        cur = conn.cursor()
        cur.execute("SELECT staff_id FROM staff WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"success": False, "message": "Username already exists."}), 409
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute("""
            INSERT INTO staff (username, password, role)
            VALUES (%s, %s, %s) RETURNING staff_id
        """, (username, hashed, role))
        staff_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "message": "Staff registered successfully.",
                        "staff": {"staff_id": staff_id, "username": username, "role": role}}), 201
    except Exception as e:
        if conn: conn.rollback()
        print("Registration Error:", e)
        return jsonify({"success": False, "message": "Registration failed.", "error": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/login", methods=["POST"])
def login():
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")).strip()
        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required."}), 400
        conn = connect_db()
        if not conn:
            return jsonify({"success": False, "message": "Database connection failed."}), 500
        cur = conn.cursor()
        cur.execute("SELECT staff_id, username, password, role FROM staff WHERE username = %s", (username,))
        staff = cur.fetchone()
        if not staff or not bcrypt.checkpw(password.encode(), str(staff[2]).encode()):
            return jsonify({"success": False, "message": "Incorrect username or password."}), 401
        return jsonify({"success": True, "message": "Login successful.",
                        "staff": {"staff_id": staff[0], "username": staff[1], "role": staff[3]}})
    except Exception as e:
        print("Login Error:", e)
        return jsonify({"success": False, "message": "Login failed.", "error": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


# ========================= PRODUCTS =========================
@app.route("/api/products", methods=["GET", "POST"])
def products():
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        if request.method == "GET":
            cur.execute("""
                SELECT product_number, product_description, product_quantity,
                       product_price, product_weight
                FROM products ORDER BY product_number
            """)
            rows = cur.fetchall()
            data = [{"id": r[0], "description": r[1], "quantity": r[2],
                     "price": json_number(r[3]), "weight": json_number(r[4])} for r in rows]
            return jsonify({"success": True, "products": data})

        data = request.get_json(silent=True) or {}
        description = str(data.get("description", "")).strip()
        quantity = data.get("quantity")
        price = data.get("price")
        weight = data.get("weight", 0)
        if not description:
            return jsonify({"success": False, "message": "Product description is required."}), 400
        if quantity is None or price is None:
            return jsonify({"success": False, "message": "Quantity and price are required."}), 400
        quantity, price, weight = int(quantity), float(price), float(weight)
        if quantity < 0 or price < 0 or weight < 0:
            return jsonify({"success": False, "message": "Values cannot be negative."}), 400
        cur.execute("""
            INSERT INTO products
            (product_description, product_quantity, product_price, product_weight)
            VALUES (%s, %s, %s, %s) RETURNING product_number
        """, (description, quantity, price, weight))
        product_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "message": "Product added successfully.", "id": product_id}), 201
    except Exception as e:
        conn.rollback()
        print("Products Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/products/<int:product_id>", methods=["GET", "PUT", "DELETE"])
def product_detail(product_id):
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        if request.method == "GET":
            cur.execute("""
                SELECT product_number, product_description, product_quantity,
                       product_price, product_weight
                FROM products WHERE product_number = %s
            """, (product_id,))
            r = cur.fetchone()
            if not r:
                return jsonify({"success": False, "message": "Product not found."}), 404
            return jsonify({"success": True, "product": {"id": r[0], "description": r[1],
                "quantity": r[2], "price": json_number(r[3]), "weight": json_number(r[4])}})

        if request.method == "DELETE":
            cur.execute("DELETE FROM products WHERE product_number = %s RETURNING product_number", (product_id,))
            if not cur.fetchone():
                return jsonify({"success": False, "message": "Product not found."}), 404
            conn.commit()
            return jsonify({"success": True, "message": "Product deleted successfully."})

        data = request.get_json(silent=True) or {}
        description = str(data.get("description", "")).strip()
        quantity, price, weight = int(data.get("quantity")), float(data.get("price")), float(data.get("weight", 0))
        if not description or quantity < 0 or price < 0 or weight < 0:
            return jsonify({"success": False, "message": "Invalid product data."}), 400
        cur.execute("""
            UPDATE products SET product_description=%s, product_quantity=%s,
            product_price=%s, product_weight=%s WHERE product_number=%s
            RETURNING product_number
        """, (description, quantity, price, weight, product_id))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "Product not found."}), 404
        conn.commit()
        return jsonify({"success": True, "message": "Product updated successfully."})
    except Exception as e:
        conn.rollback()
        print("Product Detail Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


# ========================= CUSTOMERS =========================
@app.route("/api/customers", methods=["GET", "POST"])
def customers():
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        cols = table_columns(cur, "customers")
        if request.method == "GET":
            fields = ["customer_id", "customer_name", "customer_contact_number", "customer_gender", "customer_age", "customer_email", "customer_address"]
            fields = [f for f in fields if f in cols]
            if "customer_id" not in fields or "customer_name" not in fields:
                return jsonify({"success": False, "message": "Customers table structure is missing required columns."}), 500
            cur.execute(f"SELECT {', '.join(fields)} FROM customers ORDER BY customer_id")
            rows = cur.fetchall()
            out = []
            for r in rows:
                d = dict(zip(fields, r))
                out.append({"id": d.get("customer_id"), "name": d.get("customer_name", ""),
                            "phone": d.get("customer_contact_number", "") or "",
                            "gender": d.get("customer_gender", "") or "", "age": d.get("customer_age", "") or "",
                            "email": d.get("customer_email", "") or "", "address": d.get("customer_address", "") or "",
                            "status": "Active"})
            return jsonify({"success": True, "customers": out})

        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()
        if not name or not phone:
            return jsonify({"success": False, "message": "Customer name and phone are required."}), 400
        insert_map = {
            "customer_name": name, "customer_contact_number": phone,
            "customer_gender": str(data.get("gender", "")).strip(),
            "customer_age": data.get("age") or None,
            "customer_email": str(data.get("email", "")).strip(),
            "customer_address": str(data.get("address", "")).strip()
        }
        usable = [(k, v) for k, v in insert_map.items() if k in cols]
        if not usable:
            return jsonify({"success": False, "message": "Customers table has no usable columns."}), 500
        names = ", ".join(k for k, _ in usable)
        placeholders = ", ".join(["%s"] * len(usable))
        cur.execute(f"INSERT INTO customers ({names}) VALUES ({placeholders}) RETURNING customer_id",
                    tuple(v for _, v in usable))
        customer_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "message": "Customer added successfully.", "id": customer_id}), 201
    except Exception as e:
        conn.rollback()
        print("Customers Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/customers/<int:customer_id>", methods=["GET", "PUT", "DELETE"])
def customer_detail(customer_id):
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        cols = table_columns(cur, "customers")
        if request.method == "GET":
            fields = ["customer_id", "customer_name", "customer_contact_number", "customer_gender", "customer_age", "customer_email", "customer_address"]
            fields = [f for f in fields if f in cols]
            cur.execute(f"SELECT {', '.join(fields)} FROM customers WHERE customer_id=%s", (customer_id,))
            r = cur.fetchone()
            if not r: return jsonify({"success": False, "message": "Customer not found."}), 404
            d = dict(zip(fields, r))
            return jsonify({"success": True, "customer": {"id": d.get("customer_id"), "name": d.get("customer_name", ""),
                "phone": d.get("customer_contact_number", "") or "", "gender": d.get("customer_gender", "") or "",
                "age": d.get("customer_age", "") or "", "email": d.get("customer_email", "") or "",
                "address": d.get("customer_address", "") or "", "status": "Active"}})

        if request.method == "DELETE":
            cur.execute("DELETE FROM customers WHERE customer_id=%s RETURNING customer_id", (customer_id,))
            if not cur.fetchone(): return jsonify({"success": False, "message": "Customer not found."}), 404
            conn.commit()
            return jsonify({"success": True, "message": "Customer deleted successfully."})

        data = request.get_json(silent=True) or {}
        update_map = {
            "customer_name": str(data.get("name", "")).strip(),
            "customer_contact_number": str(data.get("phone", "")).strip(),
            "customer_gender": str(data.get("gender", "")).strip(),
            "customer_age": data.get("age") or None,
            "customer_email": str(data.get("email", "")).strip(),
            "customer_address": str(data.get("address", "")).strip()
        }
        usable = [(k, v) for k, v in update_map.items() if k in cols]
        if not update_map["customer_name"] or not update_map["customer_contact_number"]:
            return jsonify({"success": False, "message": "Customer name and phone are required."}), 400
        sets = ", ".join(f"{k}=%s" for k, _ in usable)
        cur.execute(f"UPDATE customers SET {sets} WHERE customer_id=%s RETURNING customer_id",
                    tuple(v for _, v in usable) + (customer_id,))
        if not cur.fetchone(): return jsonify({"success": False, "message": "Customer not found."}), 404
        conn.commit()
        return jsonify({"success": True, "message": "Customer updated successfully."})
    except Exception as e:
        conn.rollback()
        print("Customer Detail Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


# =========================== BILLING ===========================
@app.route("/api/billing", methods=["GET", "POST"])
def billing():
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        if request.method == "GET":
            billing_cols = table_columns(cur, "billing")
            date_col = next((c for c in ("bill_date", "created_at", "created_on", "date") if c in billing_cols), None)
            date_select = f"b.{date_col}" if date_col else "NULL"
            payment_select = "b.payment_method" if "payment_method" in billing_cols else "'Cash'"
            cur.execute(f"""
                SELECT b.bill_id, b.customer_id, COALESCE(c.customer_name, 'Walk-in Customer'),
                       b.subtotal, b.discount_percent, b.discount_amount, b.final_total,
                       {payment_select}, {date_select}
                FROM billing b LEFT JOIN customers c ON c.customer_id=b.customer_id
                ORDER BY b.bill_id DESC LIMIT 20
            """)
            rows = cur.fetchall()
            bills = [{"bill_id": r[0], "customer_id": r[1], "customer": r[2], "subtotal": json_number(r[3]),
                      "discount_percent": json_number(r[4]), "discount_amount": json_number(r[5]),
                      "final_total": json_number(r[6]), "payment_method": r[7] or "Cash",
                      "date": r[8].isoformat() if hasattr(r[8], "isoformat") else r[8],
                      "status": "Completed"} for r in rows]
            return jsonify({"success": True, "bills": bills})

        data = request.get_json(silent=True) or {}
        items = data.get("items") or []
        if not items:
            return jsonify({"success": False, "message": "Please add at least one product."}), 400
        customer_id = data.get("customer_id") or None
        staff_id = data.get("staff_id") or None
        discount_percent = float(data.get("discount_percent", 0) or 0)
        if discount_percent < 0 or discount_percent > 100:
            return jsonify({"success": False, "message": "Discount must be between 0 and 100."}), 400

        subtotal = 0.0
        checked_items = []
        for item in items:
            pid = int(item.get("product_number") or item.get("id"))
            qty = int(item.get("quantity"))
            if qty <= 0: raise ValueError("Quantity must be greater than zero.")
            cur.execute("SELECT product_description, product_quantity, product_price FROM products WHERE product_number=%s FOR UPDATE", (pid,))
            p = cur.fetchone()
            if not p: raise ValueError(f"Product ID {pid} was not found.")
            if qty > int(p[1]): raise ValueError(f"Insufficient stock for {p[0]}. Available stock: {p[1]}")
            price = float(p[2])
            subtotal += price * qty
            checked_items.append((pid, qty, price))

        discount_amount = subtotal * discount_percent / 100
        final_total = subtotal - discount_amount

        billing_cols = table_columns(cur, "billing")
        fields = ["customer_id", "staff_id", "subtotal", "discount_percent", "discount_amount", "final_total"]
        fields = [f for f in fields if f in billing_cols]
        values = {"customer_id": customer_id, "staff_id": staff_id, "subtotal": subtotal,
                  "discount_percent": discount_percent, "discount_amount": discount_amount, "final_total": final_total}
        if "customer_id" in fields and customer_id is None:
            # PostgreSQL allows NULL for walk-in only if the column is nullable.
            pass
        placeholders = ", ".join(["%s"] * len(fields))
        cur.execute(f"INSERT INTO billing ({', '.join(fields)}) VALUES ({placeholders}) RETURNING bill_id",
                    tuple(values[f] for f in fields))
        bill_id = cur.fetchone()[0]

        item_cols = table_columns(cur, "billing_items")
        for pid, qty, price in checked_items:
            item_values = {"bill_id": bill_id, "product_number": pid, "quantity": qty, "price": price, "total": price * qty}
            item_fields = [f for f in ["bill_id", "product_number", "quantity", "price", "total"] if f in item_cols]
            cur.execute(f"INSERT INTO billing_items ({', '.join(item_fields)}) VALUES ({', '.join(['%s']*len(item_fields))})",
                        tuple(item_values[f] for f in item_fields))
            cur.execute("UPDATE products SET product_quantity=product_quantity-%s WHERE product_number=%s", (qty, pid))

        conn.commit()
        return jsonify({"success": True, "message": "Bill completed successfully.", "bill": {
            "bill_id": bill_id, "subtotal": subtotal, "discount": discount_amount, "final_total": final_total}}), 201
    except Exception as e:
        conn.rollback()
        print("Billing Error:", e)
        return jsonify({"success": False, "message": str(e)}), 400
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/billing/<int:bill_id>", methods=["GET"])
def billing_detail(bill_id):
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.bill_id, b.customer_id, COALESCE(c.customer_name,'Walk-in Customer'),
                   b.subtotal, b.discount_percent, b.discount_amount, b.final_total
            FROM billing b LEFT JOIN customers c ON c.customer_id=b.customer_id
            WHERE b.bill_id=%s
        """, (bill_id,))
        bill = cur.fetchone()
        if not bill:
            return jsonify({"success": False, "message": "Bill not found."}), 404
        cur.execute("""
            SELECT bi.product_number, p.product_description, bi.quantity, bi.price, bi.total
            FROM billing_items bi JOIN products p ON p.product_number=bi.product_number
            WHERE bi.bill_id=%s ORDER BY bi.product_number
        """, (bill_id,))
        items = [{"product_number": r[0], "name": r[1], "quantity": r[2], "price": json_number(r[3]), "total": json_number(r[4])} for r in cur.fetchall()]
        return jsonify({"success": True, "bill": {"bill_id": bill[0], "customer_id": bill[1], "customer": bill[2],
            "subtotal": json_number(bill[3]), "discount_percent": json_number(bill[4]),
            "discount_amount": json_number(bill[5]), "final_total": json_number(bill[6]), "items": items}})
    except Exception as e:
        print("Bill Detail Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    conn = connect_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        total_products = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM customers")
        total_customers = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products WHERE product_quantity <= 5")
        low_stock = cur.fetchone()[0]

        billing_cols = table_columns(cur, "billing")
        date_col = next((c for c in ("bill_date", "created_at", "created_on", "date") if c in billing_cols), None)
        if date_col:
            cur.execute(f"SELECT COALESCE(SUM(final_total),0) FROM billing WHERE DATE({date_col}) = CURRENT_DATE",)
        else:
            cur.execute("SELECT COALESCE(SUM(final_total),0) FROM billing WHERE FALSE")
        today_sales = json_number(cur.fetchone()[0])

        cur.execute("""
            SELECT b.bill_id, COALESCE(c.customer_name,'Walk-in Customer'), b.final_total
            FROM billing b LEFT JOIN customers c ON c.customer_id=b.customer_id
            ORDER BY b.bill_id DESC LIMIT 5
        """)
        sales = [{"bill_id": r[0], "customer": r[1], "amount": json_number(r[2]), "status": "Completed"} for r in cur.fetchall()]
        cur.execute("""
            SELECT product_number, product_description, product_quantity
            FROM products WHERE product_quantity <= 5
            ORDER BY product_quantity, product_description LIMIT 10
        """)
        low = [{"id": r[0], "description": r[1], "quantity": r[2]} for r in cur.fetchall()]
        return jsonify({"success": True, "total_products": total_products, "total_customers": total_customers,
                        "today_sales": today_sales, "low_stock": low_stock, "sales": sales, "low_stock_items": low})
    except Exception as e:
        print("Dashboard Error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        close_db(conn, locals().get("cur"))


# ========================= SUPPLIERS =========================

@app.route("/api/suppliers", methods=["GET", "POST"])
@app.route("/api/supplier", methods=["GET", "POST"])
def suppliers():
    conn = connect_db()

    if not conn:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:
        cur = conn.cursor()

        # ================= GET SUPPLIERS =================
        if request.method == "GET":

            cur.execute("""
                SELECT
                    supplier_id,
                    supplier_name,
                    supplier_email,
                    product_name,
                    minimum_stock
                FROM suppliers
                ORDER BY supplier_id
            """)

            rows = cur.fetchall()

            suppliers_list = []

            for r in rows:
                suppliers_list.append({
                    "supplier_id": r[0],
                    "supplier_name": r[1],
                    "supplier_email": r[2],
                    "product_name": r[3],
                    "product_number": r[3],
                    "minimum_stock": r[4]
                })

            return jsonify(suppliers_list), 200

        # ================= ADD SUPPLIER =================

        data = request.get_json(silent=True) or {}

        supplier_name = str(
            data.get("supplier_name", "")
        ).strip()

        supplier_email = str(
            data.get("supplier_email", "")
        ).strip()

        # Your database uses product_name.
        # Accept both names so the existing frontend works.
        product_name = str(
            data.get("product_name")
            or data.get("product_number")
            or ""
        ).strip()

        minimum_stock = data.get("minimum_stock")

        if not supplier_name:
            return jsonify({
                "success": False,
                "message": "Supplier name is required."
            }), 400

        if not supplier_email:
            return jsonify({
                "success": False,
                "message": "Supplier email is required."
            }), 400

        if not product_name:
            return jsonify({
                "success": False,
                "message": "Product name is required."
            }), 400

        if minimum_stock is None:
            return jsonify({
                "success": False,
                "message": "Minimum stock is required."
            }), 400

        minimum_stock = int(minimum_stock)

        if minimum_stock < 0:
            return jsonify({
                "success": False,
                "message": "Minimum stock cannot be negative."
            }), 400

        cur.execute("""
            INSERT INTO suppliers
            (
                supplier_name,
                supplier_email,
                product_name,
                minimum_stock
            )
            VALUES (%s, %s, %s, %s)
            RETURNING supplier_id
        """, (
            supplier_name,
            supplier_email,
            product_name,
            minimum_stock
        ))

        supplier_id = cur.fetchone()[0]

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Supplier added successfully.",
            "supplier_id": supplier_id
        }), 201

    except Exception as e:

        conn.rollback()

        print("Suppliers Error:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        close_db(conn, locals().get("cur"))


# ================= SUPPLIER DETAIL =================

@app.route("/api/suppliers/<int:supplier_id>",
           methods=["GET", "PUT", "DELETE"])
@app.route("/api/supplier/<int:supplier_id>",
           methods=["GET", "PUT", "DELETE"])
def supplier_detail(supplier_id):

    conn = connect_db()

    if not conn:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    try:

        cur = conn.cursor()

        # ================= GET ONE SUPPLIER =================

        if request.method == "GET":

            cur.execute("""
                SELECT
                    supplier_id,
                    supplier_name,
                    supplier_email,
                    product_name,
                    minimum_stock
                FROM suppliers
                WHERE supplier_id = %s
            """, (supplier_id,))

            r = cur.fetchone()

            if not r:
                return jsonify({
                    "success": False,
                    "message": "Supplier not found."
                }), 404

            return jsonify({
                "supplier_id": r[0],
                "supplier_name": r[1],
                "supplier_email": r[2],
                "product_name": r[3],
                "product_number": r[3],
                "minimum_stock": r[4]
            }), 200

        # ================= DELETE =================

        if request.method == "DELETE":

            cur.execute("""
                DELETE FROM suppliers
                WHERE supplier_id = %s
                RETURNING supplier_id
            """, (supplier_id,))

            deleted = cur.fetchone()

            if not deleted:
                return jsonify({
                    "success": False,
                    "message": "Supplier not found."
                }), 404

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Supplier deleted successfully."
            }), 200

        # ================= UPDATE =================

        data = request.get_json(silent=True) or {}

        supplier_name = str(
            data.get("supplier_name", "")
        ).strip()

        supplier_email = str(
            data.get("supplier_email", "")
        ).strip()

        product_name = str(
            data.get("product_name")
            or data.get("product_number")
            or ""
        ).strip()

        minimum_stock = data.get("minimum_stock")

        if not supplier_name or not supplier_email or not product_name:
            return jsonify({
                "success": False,
                "message": "All supplier details are required."
            }), 400

        minimum_stock = int(minimum_stock)

        if minimum_stock < 0:
            return jsonify({
                "success": False,
                "message": "Minimum stock cannot be negative."
            }), 400

        cur.execute("""
            UPDATE suppliers
            SET
                supplier_name = %s,
                supplier_email = %s,
                product_name = %s,
                minimum_stock = %s
            WHERE supplier_id = %s
            RETURNING supplier_id
        """, (
            supplier_name,
            supplier_email,
            product_name,
            minimum_stock,
            supplier_id
        ))

        updated = cur.fetchone()

        if not updated:
            return jsonify({
                "success": False,
                "message": "Supplier not found."
            }), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Supplier updated successfully."
        }), 200

    except Exception as e:

        conn.rollback()

        print("Supplier Detail Error:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        close_db(conn, locals().get("cur"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
