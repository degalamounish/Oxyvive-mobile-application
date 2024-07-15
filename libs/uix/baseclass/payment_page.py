import json
import random
import string
import time
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import urlparse, parse_qs

import anvil
import razorpay
import requests
import webview
from anvil.tables import app_tables
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from server import Server


class Payment(MDScreen):
    servicer_id = None
    date = None
    time_left = None

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        self.razorpay_payment_id = None
        self.dialog = None
        self.tax = None
        self.data_stored = False  # Flag to prevent storing data multiple times
        self.dialog_opened = False  # Flag to prevent showing dialog multiple times
        Window.bind(on_keyboard=self.on_keyboard)
        self.server = Server()

    def on_pre_enter(self):
        self.change()
        self.servicer_details()

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push("slot_booking", "right")
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        user_info['slot_date'] = ""
        user_info['slot_time'] = ""
        with open("user_data.json", "w") as json_file:
            json.dump(user_info, json_file)

    def change(self):
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading user_data.json: {e}")

    def store_booked_data(self):
        if self.data_stored:
            return
        self.data_stored = True  # Set the flag to indicate data is stored

        with open('booking_data.json', 'r') as file:
            booking_data = json.load(file)
        oxi_id = booking_data.get('user_id', '')
        servicer_id = booking_data.get('servicer_id', '')
        book_date = booking_data.get('book_date', '')
        book_time = booking_data.get('book_time', '')
        date_time = booking_data.get('date_time', '')

        try:
            if self.server.is_connected():
                slot_id = self.generate_random_code()
                date_object = datetime.strptime(book_date, '%Y-%m-%d').date()
                app_tables.oxi_book_slot.add_row(
                    oxi_book_id=slot_id,
                    oxi_servicer_id=servicer_id,
                    oxi_id=oxi_id,
                    oxi_book_date=date_object,
                    oxi_book_time=book_time,
                    oxi_date_time=date_time,
                    oxi_payment_id=self.razorpay_payment_id
                )
                self.show_validation_dialog(
                    "Your slot is successfully booked. You will receive an instant response from Oxivive.")
            else:
                self.show_validation_dialog("No internet connection")
        except Exception as e:
            print(e)
            self.show_validation_dialog("Error processing user data")

    def show_validation_dialog(self, message):
        if self.dialog_opened:
            return
        self.dialog_opened = True  # Set the flag to indicate dialog is shown
        Clock.schedule_once(lambda dt: self._create_dialog(message), 0)

    def _create_dialog(self, message):
        dialog = MDDialog(
            text=f"{message}",
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self._close_dialog(dialog))],
        )
        dialog.open()

    def _close_dialog(self, dialog):
        dialog.dismiss()
        self.dialog_opened = False  # Reset the flag after closing dialog

    def servicer_details(self):
        details = app_tables.oxiclinics.get(oxiclinics_id=self.servicer_id)
        if not details:
            details = app_tables.oxiwheels.get(oxiwheels_id=self.servicer_id)
            if not details:
                details = app_tables.oxigyms.get(oxigyms_id=self.servicer_id)
        if not details:
            print("Service ID not found in any table")
            return
        details = dict(details)
        if 'oxiclinics_address' in details:
            self.ids.service_name.text = details.get('oxiclinics_Name', 'N/A')
            self.ids.service_type.text = 'OxiClinic'
            self.ids.service_address.text = details.get('oxiclinics_address', 'N/A')
        elif 'oxiwheels_address' in details:
            self.ids.service_name.text = details.get('oxiwheels_Name', 'N/A')
            self.ids.service_type.text = 'OxiWheel'
            self.ids.service_address.text = details.get('oxiwheels_address', 'N/A')
        elif 'oxigyms_address' in details:
            self.ids.service_name.text = details.get('oxigyms_Name', 'N/A')
            self.ids.service_type.text = 'OxiGym'
            self.ids.service_address.text = details.get('oxigyms_address', 'N/A')
        else:
            self.ids.service_address.text = 'N/A'

    def view_bill(self):
        scroll_view = self.ids.scroll_view
        bill_card = self.ids.bill
        scroll_view.scroll_to(bill_card)

    def generate_random_code(self):
        prefix = "BI"
        random_numbers = ''.join(random.choices(string.digits, k=5))
        code = prefix + random_numbers
        return code

    def initiate_payment(self):
        print("Initiating payment...")
        amount = 999  # Amount in INR (sub-units, e.g., 100 INR = 10000 paisa)
        api_key = 'rzp_test_41ch2lqayiGZ9X'
        api_secret = 'CPEd7kVR1d215BH12bIoJb63'

        try:
            response = requests.post(
                'https://api.razorpay.com/v1/orders',
                auth=(api_key, api_secret),
                data=json.dumps({
                    'amount': amount * 100,  # Amount in paisa
                    'currency': 'INR',
                    'receipt': 'order_rcptid_12',
                    'payment_capture': '1'
                }),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            order_data = response.json()
            print(f"Order created successfully. Order ID: {order_data['id']}")
            order_id = order_data['id']
            self.update_html_file(order_id, amount * 100)
            self.serve_and_open_html()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    def update_html_file(self, order_id, amount):
        print(f"Updating HTML file with order ID: {order_id} and amount: {amount}")
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Razorpay Checkout</title>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        </head>
        <body>
        <script>
            var options = {{
                "key": "rzp_test_41ch2lqayiGZ9X",
                "amount": "{amount}",
                "currency": "INR",
                "name": "Oxivive",
                "description": "Test Transaction",
                "order_id": "{order_id}",
                "handler": function (response) {{
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', 'http://localhost:9000/success?payment_id=' + response.razorpay_payment_id, true);
                    xhr.send();
                    alert("Payment successful! Payment ID: " + response.razorpay_payment_id);
                    window.location.href = "http://localhost:9000/success";
                }},
                "prefill": {{
                    "name": "Your Name",
                    "email": "your.email@example.com",
                    "contact": "9999999999"
                }},
                "theme": {{
                    "color": "#3399cc"
                }}
            }};
            var rzp1 = new Razorpay(options);
            rzp1.on('payment.failed', function (response) {{
                alert("Payment failed! Error: " + response.error.reason);
            }});
            rzp1.open();
        </script>
        </body>
        </html>
        """
        with open("checkout.html", "w") as file:
            file.write(html_content)
        print("HTML file updated successfully.")

    def serve_and_open_html(self):
        def serve(app):
            class CustomHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.app = app
                    super().__init__(*args, **kwargs)

                def do_GET(self):
                    if self.path.startswith('/success'):
                        parsed_url = urlparse(self.path)
                        query_params = parse_qs(parsed_url.query)
                        payment_id = query_params.get('payment_id', [''])[0]
                        if payment_id:
                            print(f"Payment successful! Payment ID: {payment_id}")
                            self.app.razorpay_payment_id = payment_id
                        print("Success page requested.")
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(b"""
                            <!DOCTYPE html>
                                <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <title>Oxivive Payment Success</title>
                                    </head>
                                    <body>
                                        <h1>Payment Successful!</h1>
                                    </body>
                                </html>
                            """)
                        print("Sending response to success page request.")
                        print("Shutting down the server and switching to success screen.")
                        shutdown_thread = Thread(target=self.app.shutdown_and_switch)
                        shutdown_thread.start()
                    else:
                        print(f"Serving file: {self.path}")
                        super().do_GET()

            httpd = HTTPServer(('localhost', 9000), CustomHandler)
            print("Local server started. Serving at http://localhost:9000/checkout.html")
            httpd.serve_forever()

        server_thread = Thread(target=serve, args=(self,))
        server_thread.daemon = True
        server_thread.start()
        print("Opening Razorpay checkout page...")
        webview.create_window('Razorpay Checkout', url="http://localhost:9000/checkout.html", width=800, height=600,
                              resizable=True, js_api=True)
        webview.start()

    def shutdown_and_switch(self):
        time.sleep(1)
        print("Server shutdown initiated.")
        self.switch_to_success_screen()

    def switch_to_success_screen(self):
        self.store_booked_data()
        self.manager.push_replacement('client_services')
        print("Switched to success screen.")
