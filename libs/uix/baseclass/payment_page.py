import json
import webbrowser

import razorpay
from anvil.tables import app_tables
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
import anvil
from server import Server


class Payment(MDScreen):
    servicer_id = None
    date = None
    time_left = None

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
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
        self.ids.session_date.text = ''
        self.ids.session_time.text = ''
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
            # self.ids.user_name.text = user_info.get('username', '')
            # self.ids.session_date.text = user_info.get('slot_date', '')
            # self.ids.session_time.text = user_info.get('slot_time', '')
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
            # with open('user_data.json', 'r') as file:
            #     user_info = json.load(file)
            # email = user_info.get('email', '')
            # user_name = user_info.get('username', '')
            # book_date = user_info.get('slot_date', '')
            # book_time = user_info.get('slot_time', '')
            # user = app_tables.users.get(email=email)
            # user_id = user['id']
            # row = app_tables.book_slot.search()
            # slot_id = len(row) + 1
            # app_tables.book_slot.add_row(
            #     slot_id=slot_id,
            #     user_id=user_id,
            #     username=user_name,
            #     book_date=book_date,
            #     book_time=book_time
            # )
        except Exception as e:
            print("An error occurred while creating the order:", str(e))

    def open_payment_gateway(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        email = user_info.get('email', '')
        user_name = user_info.get('username', '')
        book_date = user_info.get('slot_date', '')
        book_time = user_info.get('slot_time', '')

        try:
            if self.server.is_connected():
                user = app_tables.oxi_users.get(oxi_email=email)
                user_id = user['oxi_id']
                row = app_tables.oxi_book_slot.search()
                slot_id = len(row) + 1
                app_tables.oxi_book_slot.add_row(
                    oxi_serviceProvider_id=slot_id,
                    oxi_client_id=user_id,
                    oxi_service_type=user_name,
                    oxi_book_date=book_date,
                    oxi_book_time=book_time
                )
            else:
                self.show_validation_dialog("No internet connection")

        except Exception as e:
            print(e)
            self.show_validation_dialog("Error processing user data")
        # Replace this with actual code to open the payment gateway URL
        print(f"Opening Razorpay payment gateway")
        website_url = 'https://rzp.io/l/iJyrLCI'
        webbrowser.open(website_url)
        # # Create the Razorpay checkout URL
        # razorpay_key_id = 'rzp_test_kOpS7Ythlfb1Ho'
        # razorpay_checkout_url = f'https://checkout.razorpay.com/v1/checkout.js?key={razorpay_key_id}'
        # webbrowser(razorpay_checkout_url)

        # Open the Razorpay checkout in a WebView
        # webbrowser.create_window('Razorpay Checkout', razorpay_checkout_url, width=800, height=600, resizable=True)
        #
        # # payment_page page logic
        # layout = BoxLayout(orientation='vertical')
        #
        # # Create a WebView to display the Razorpay payment page
        # webview = WebView(url='payment_url', size_hint=(1, 1))
        # layout.add_widget(webview)
        #
        # # Add a back button
        # back_button = Button(text='Back to App', size_hint=(1, 0.1))
        # back_button.bind(on_press=self.back_to_app)
        # layout.add_widget(back_button)
        #

    # def open_payment_gateway(self, payment_url):
    #     # Replace this with actual code to open the payment gateway URL
    #     print(f"Opening Razorpay payment gateway: {payment_url}")
    #
    #     # payment_page page logic
    #     layout = BoxLayout(orientation='vertical')
    #
    #     # Create a WebView to display the Razorpay payment page
    #     webview = WebView(url='payment_url', size_hint=(1, 1))
    #     layout.add_widget(webview)
    #
    #     # Add a back button
    #     back_button = Button(text='Back to App', size_hint=(1, 0.1))
    #     back_button.bind(on_press=self.back_to_app)
    #     layout.add_widget(back_button)

    # return layout

    # def on_pay_button_pressed(self, instance):
    #     client = razorpay.Client(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")
    #
    #     order = client.order.create(amount=10000, currency="INR")
    #
    #     client.payment.launch(order_id=order["id"])
    #
    #     client.payment.on("success", self.on_payment_success)
    #
    # def on_payment_success(self, payment):
    #     self.label.text = "Payment successful!"

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
        
