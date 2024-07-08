import json
import random
import string
import webbrowser
from datetime import datetime

import razorpay
from anvil.tables import app_tables
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
import anvil
from kivymd.uix.textfield import MDTextField
from server import Server


class Payment(MDScreen):
    servicer_id = None
    date = None
    time_left = None

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)

        self.confirm_cancel_dialog = None
        self.payment_id_field = None
        self.dialog = None
        self.tax = None
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

    def razor_pay(self):
        client = razorpay.Client(auth=('rzp_test_kOpS7Ythlfb1Ho', 'OzPZyPbsOV0AlADilk4wkgv9'))

        # Create an order
        order_amount = 5000  # Amount in paise (e.g., 50000 paise = 500 INR)
        order_currency = 'INR'
        order_receipt = 'order_rcptid_12'

        order_data = {
            'amount': order_amount,
            'currency': order_currency,
            'receipt': order_receipt,
            'payment_capture': 1  # Automatically capture payment when order is created
        }
        try:
            order = client.order.create(data=order_data)
            # Get the order ID
            order_id = order['id']
            # client.payment.launch(order_id)

            # Construct the payment URL
            payment_url = f"https://rzp_test_kOpS7Ythlfb1Ho.api.razorpay.com/v1/checkout/{order_id}"
            self.open_payment_gateway(payment_url)
            self.show_validation_dialog("Payment Successful")
            anvil.server.connect("server_UY47LMUKBDUJMU4EA3RKLXCC-LP5NLIEYMCLMZ4NU")

        except Exception as e:
            print("An error occurred while creating the order:", str(e))

    def open_payment_gateway(self):
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
                    oxi_payment_id=self.payment_id_field.text
                )
                self.show_validation_dialog("Your slot is successfully booked. You will receive an instant response from Oxivive.")
            else:
                self.show_validation_dialog("No internet connection")

        except Exception as e:
            print(e)
            self.show_validation_dialog("Error processing user data")

    def payment_id(self):
        Clock.schedule_once(lambda dt: self.payment_id_dialog(), 0)
        print(f"Opening Razorpay payment gateway")
        website_url = 'http://razorpay.me/@oxivivelifecareprivatelimited'
        webbrowser.open(website_url)

    def payment_id_dialog(self):
        self.payment_id_field = MDTextField(
            hint_text="Payment ID",
            mode="rectangle"
        )

        self.dialog = MDDialog(
            title="Enter Payment ID",
            type="custom",
            content_cls=self.payment_id_field,
            auto_dismiss=False,  # Prevent dismissing on outside click
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.confirm_cancel_dialog_open
                ),
                MDFlatButton(
                    text="OK",
                    on_release=self.validate_and_print_payment_id
                ),
            ],
        )
        self.dialog.open()

    def confirm_cancel_dialog_open(self, *args):
        if not self.confirm_cancel_dialog:
            self.confirm_cancel_dialog = MDDialog(
                title="Cancel Confirmation",
                text="If you paid, paste the Payment ID. Otherwise, click OK to cancel your booking.",
                auto_dismiss=False,  # Prevent dismissing on outside click
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.dismiss_confirm_cancel_dialog
                    ),
                    MDFlatButton(
                        text="OK",
                        on_release=self.close_dialog
                    ),
                ],
            )
        self.confirm_cancel_dialog.open()

    def dismiss_confirm_cancel_dialog(self, *args):
        if self.confirm_cancel_dialog:
            self.confirm_cancel_dialog.dismiss()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        if self.confirm_cancel_dialog:
            self.confirm_cancel_dialog.dismiss()

    def validate_and_print_payment_id(self, *args):
        payment_id = self.payment_id_field.text
        if not payment_id.strip():
            alert_dialog = MDDialog(
                title="Alert",
                text="Please enter Payment ID. Without entering Payment ID, your slot is not booked.",
                auto_dismiss=False,  # Prevent dismissing on outside click
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: alert_dialog.dismiss()
                    )
                ]
            )
            alert_dialog.open()
        else:
            print(f"Payment ID entered: {payment_id}")
            self.dialog.dismiss()
            self.open_payment_gateway()
    def show_validation_dialog(self, message):
        # Create the dialog asynchronously
        Clock.schedule_once(lambda dt: self._create_dialog(message), 0)

    def _create_dialog(self, message):
        dialog = MDDialog(
            text=f"{message}",
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def servicer_details(self):
        details = app_tables.oxiclinics.get(oxiclinics_id=self.servicer_id)

        if not details:
            details = app_tables.oxiwheels.get(oxiwheels_id=self.servicer_id)
            if not details:
                details = app_tables.oxigyms.get(oxigyms_id=self.servicer_id)

        if not details:
            print("Service ID not found in any table")
            return

        # Convert details to a dictionary
        details = dict(details)

        # Display the details based on which table the details were found in
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
