import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db import connect_db


# ==========================================================
#                    EMAIL CONFIGURATION
# ==========================================================

SENDER_EMAIL = os.getenv("STOCKFLOW_EMAIL")
APP_PASSWORD = os.getenv("STOCKFLOW_APP_PASSWORD")


# ==========================================================
#                    EMAIL ALERT
# ==========================================================

class EmailAlert:

    def __init__(self):

        self.conn = connect_db()

        if not self.conn:
            raise Exception(
                "Database connection failed in EmailAlert"
            )

        self.cur = self.conn.cursor()

    # ======================================================
    #                    SEND EMAIL
    # ======================================================

    def send_email(
        self,
        receiver_email,
        supplier_name,
        product_name,
        current_stock,
        minimum_stock
    ):

        try:

            # ------------------------------------------------
            # Check Email Configuration
            # ------------------------------------------------

            if not SENDER_EMAIL or not APP_PASSWORD:

                print("Email configuration is missing.")

                print(
                    "Set STOCKFLOW_EMAIL and "
                    "STOCKFLOW_APP_PASSWORD."
                )

                return False

            # ------------------------------------------------
            # Check Receiver
            # ------------------------------------------------

            if not receiver_email:

                print(
                    "Supplier email address is empty."
                )

                return False

            # ------------------------------------------------
            # Email Subject
            # ------------------------------------------------

            subject = "StockFlow - Low Stock Alert"

            # ------------------------------------------------
            # Email Body
            # ------------------------------------------------

            body = f"""
Dear {supplier_name},

This is an automated notification from StockFlow.

The following product has reached its minimum stock level.

Product: {product_name}

Current Stock: {current_stock}

Minimum Stock: {minimum_stock}

Please arrange a new supply as soon as possible.

Thank you,
StockFlow Inventory System
"""

            # ------------------------------------------------
            # Create Email
            # ------------------------------------------------

            message = MIMEMultipart()

            message["From"] = SENDER_EMAIL
            message["To"] = receiver_email
            message["Subject"] = subject

            message.attach(
                MIMEText(body, "plain")
            )

            # ------------------------------------------------
            # Connect to Gmail
            # ------------------------------------------------

            with smtplib.SMTP(
                "smtp.gmail.com",
                587
            ) as server:

                server.starttls()

                server.login(
                    SENDER_EMAIL,
                    APP_PASSWORD
                )

                server.sendmail(
                    SENDER_EMAIL,
                    receiver_email,
                    message.as_string()
                )

            print(
                "Low stock email sent successfully."
            )

            return True

        except Exception as e:

            print(
                "Email Error:",
                e
            )

            return False

    # ======================================================
    #                    CHECK STOCK
    # ======================================================

    def check_stock(self, product_number):

        try:

            self.cur.execute(
                """
                SELECT
                    p.product_description,
                    p.product_quantity,
                    s.supplier_name,
                    s.supplier_email,
                    s.minimum_stock
                FROM products p
                JOIN suppliers s
                    ON p.product_description = s.product_name
                WHERE p.product_number = %s
                """,
                (product_number,)
            )

            data = self.cur.fetchone()

            # ------------------------------------------------
            # No Supplier Found
            # ------------------------------------------------

            if not data:

                print(
                    f"No supplier information found "
                    f"for product {product_number}."
                )

                return False

            # ------------------------------------------------
            # Extract Information
            # ------------------------------------------------

            product_name = data[0]
            current_stock = data[1]
            supplier_name = data[2]
            supplier_email = data[3]
            minimum_stock = data[4]

            print(
                f"Product: {product_name}"
            )

            print(
                f"Current Stock: {current_stock}"
            )

            print(
                f"Minimum Stock: {minimum_stock}"
            )

            # ------------------------------------------------
            # Low Stock Check
            # ------------------------------------------------

            if current_stock <= minimum_stock:

                print(
                    f"Low stock detected for "
                    f"{product_name}."
                )

                return self.send_email(
                    supplier_email,
                    supplier_name,
                    product_name,
                    current_stock,
                    minimum_stock
                )

            # ------------------------------------------------
            # Stock Is Sufficient
            # ------------------------------------------------

            print(
                f"Stock level is sufficient for "
                f"{product_name}."
            )

            return True

        except Exception as e:

            print(
                "Stock Check Error:",
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
#                    TEST EMAIL ALERT
# ==========================================================

if __name__ == "__main__":

    try:

        alert = EmailAlert()

        # --------------------------------------------------
        # Change 101 to an EXISTING product number
        # in your products table.
        # --------------------------------------------------

        alert.check_stock(101)

        alert.close()

    except Exception as e:

        print(
            "Email Alert Error:",
            e
        )