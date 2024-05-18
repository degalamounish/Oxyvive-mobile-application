# -------------------service provider main-----------------------
import base64
import json
from datetime import datetime
from anvil.tables import app_tables
from kivy.core.window import Window
from kivy.graphics import Ellipse, Color, Rectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen

from server import Server



class Customers(BoxLayout):
    pass
class ServiceProviderMain(MDScreen):
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ServiceProviderMain, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.server = Server()
        now = datetime.now()
        date = now.date()
        print(date)
        self.ids.extra_info2.text = str(date)
        self.load_customers(date)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("main_sc", "right")

    def service_button(self, button):
        if not self.menu:
            cities = ["Settings", "Notification"]
            items = [
                {
                    "text": city,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=city: self.select_city(x),
                } for city in cities
            ]

            # Use the first button from right_action_items as the caller

            self.menu = MDDropdownMenu(
                caller=button,
                items=items,
                width_mult=3,
                elevation=2,

                max_height=dp(100),

            )
        else:
            self.menu.dismiss()

        self.menu.open()

    def select_city(self, option):
        # Callback function when a city is selected
        if option == 'Settings':
            self.settings()
        elif option == 'Notification':
            self.notification_button_action()

        self.menu.dismiss()

    def settings(self):
        print("Settings")

    def notification_button_action(self):
        print("Notification")

    def sign_out_button_action(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "login"

    customer_list = ObjectProperty(None)

    def load_customers(self, date):
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            user_id = user_info.get('id', '')

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading user_data.json: {e}")

        # Assuming you have an endpoint to fetch data
        data = app_tables.book_slot.search(book_date=date, serviceProvider_id=user_id)
        if not data:
            self.show_alert("No bookings yet on this date")
            return

        customers_list = []
        for row in data:
            customer_details = app_tables.users.get(id=row['user_id'])
            customer = {}
            customer["name"] = customer_details['username']
            customer["email"] = customer_details['email']
            customer["phone"] = customer_details['phone']
            customer["slot_time"] = row['book_time']
            customer["service"] = row['service_type']
            profile_data = customer_details['profile'].get_bytes()
            profile_data = base64.b64encode(profile_data).decode('utf-8')

            customer["image"] = profile_data
            customer["date"] = row['book_date']
            customers_list.append(customer)
        print(customers_list)
        self.update_customer_list(customers_list)

    def update_customer_list(self, customers):
        self.customer_list.clear_widgets()
        for customer in customers:
            # layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))

            layout = Customers()
            self.customer_list.add_widget(layout)
            print(customer)

    def show_alert(self, message):
        popup = Popup(title='Alert', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_date_picker(self, arg):
        date_dialog = MDDatePicker(size_hint=(None, None), size=(150, 150))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        self.ids.extra_info2.text = ''

    def on_save(self, instance, value, date_range):
        self.ids.extra_info2.text = str(value)
        date = value
        print('Second time loading customers')
        self.load_customers(date)

    # click Cancel
    def on_cancel(self, instance, value):
        # print("cancel")
        instance.dismiss()


class ProfileImage(Image):
    source = StringProperty('images/hospital.png')  # Default image source

    def __init__(self, **kwargs):
        super(ProfileImage, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False

        # Apply the rounded shape
        with self.canvas.before:
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def on_size(self, *args):
        # Update the shape when the widget size changes
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size



