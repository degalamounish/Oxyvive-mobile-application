# -------------------service provider main-----------------------
import base64
import json
from datetime import datetime
from io import BytesIO

from anvil.tables import app_tables
from kivy.atlas import CoreImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Ellipse, Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen

from server import Server


# Builder.load_file("../kv/service_provider_main_page.kv")
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

            layout = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=("290dp", "200dp"),
                elevation=2,
                md_bg_color=(1, 1, 1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )

            inner_grid = GridLayout(cols=1, pos_hint={'center_x': 0.5, 'center_y': 0.5})

            box_layout = BoxLayout(size_hint_y=None, height=dp(50), padding="5dp", spacing="5dp",
                                   pos_hint={'center_x': 0.5})
            with box_layout.canvas.before:
                Color(1, 0, 0, 1)
                Rectangle(pos=box_layout.pos, size=box_layout.size)

            image = Image(
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                pos_hint={'center_x': 0.5},
                source='images/hospital.png'
            )

            labels_layout = BoxLayout(orientation='vertical', padding="5dp", spacing="10dp", pos_hint={'center_x': 0.5})

            pat_username = Label(
                text=f"{customer['name']}",
                font_name='Roboto',
                color=(1, 1, 1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.3}
            )

            pat_email = Label(

                text=f"{customer['email']}",
                color=(1, 1, 1, 1),
                font_name='Roboto',
                font_size='12sp',
                pos_hint={'center_x': 0.5, 'center_y': 0.1}
            )

            box_layout.add_widget(image)
            labels_layout.add_widget(pat_username)
            labels_layout.add_widget(pat_email)

            inner_grid.add_widget(box_layout)
            inner_grid.add_widget(labels_layout)

            layout.add_widget(inner_grid)
            # layout.add_widget(card)

            additional_labels = BoxLayout(
                orientation='vertical',
                pos_hint={'center_x': 0.5},
                padding=dp(2),
                spacing=dp(7)
            )

            labels = [
                f"Name : {customer['name']}",
                f" Phone : {customer['phone']}",
                f" Slot Time : {customer['slot_time']}",
                f" Slot Date : {customer['email']}",
                f"Service Type :{customer['service']}"
            ]

            for text in labels:
                label = Label(
                    text=text,
                    font_name='Roboto',
                    color=(0, 0, 0, 1),
                    size_hint_x=0.5,
                    size_hint_y=None,
                    height=dp(20),
                    pos_hint={'center_x': 0.5, 'center_y': .5}
                )
                additional_labels.add_widget(label)

            layout.add_widget(additional_labels)
            self.customer_list.add_widget(layout)

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


class ProfileCard(MDFloatLayout, CommonElevationBehavior):
    pass


class ServiceProfile(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceProfile, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.details()


    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")

    edit_mode = False

    def details(self):
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            self.ids.text_input1.text = user_info.get('id', '')
            self.ids.text_input2.text = user_info.get('username', '')
            self.ids.text_input3.text = user_info.get('email', '')
            self.ids.text_input4.text = user_info.get('phone', '')
            self.ids.text_input5.text = user_info.get('address', '')
            image_data = user_info.get('profile','')
            image_data_binary = base64.b64decode(image_data)
            profile_texture_io = BytesIO(image_data_binary)
            profile_texture_obj = CoreImage(profile_texture_io, ext='png').texture
            self.ids.selected_image1.texture = profile_texture_obj


        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading user_data.json: {e}")


class ServiceNotification(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceNotification, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")


class ServiceSlotAdding(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceSlotAdding, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=True,
            check=True,
            column_data=[
                ("No.", dp(30)),
                ("Slot No", dp(40)),
                ("Applied Date", dp(40)),
                ("Status", dp(40)),
            ],
            row_data=[("1", "A1", "01-01-2024", ([1, 0, 0, 1], 'padding'))],
        )

        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 0.5},
            adaptive_size=True,
            padding="24dp",
            spacing="24dp",
        )

        for button_text in ["Add Slot", "Delete Checked Slots"]:
            button_box.add_widget(
                MDRaisedButton(
                    text=button_text, on_release=self.on_button_press
                )
            )

        layout = MDFloatLayout()  # root layout
        layout.add_widget(self.data_tables)
        layout.add_widget(button_box)
        self.add_widget(layout)

    def on_button_press(self, instance_button):
        try:
            {
                "Add Slot": self.add_row,
                "Delete Checked Slots": self.delete_checked_rows,
            }[instance_button.text]()
        except KeyError:
            pass

    def add_row(self):
        last_num_row = int(self.data_tables.row_data[-1][0])
        new_row_data = (
            str(last_num_row + 1),
            "C1",
            "03-03-2024",
            ([1, 1, 0, 0], 'in progress')
        )
        self.data_tables.row_data.append(list(new_row_data))

    def delete_checked_rows(self):
        def deselect_rows(*args):
            self.data_tables.table_data.select_all("normal")

        checked_rows = self.data_tables.get_row_checks()
        for checked_row in checked_rows:
            if checked_row in self.data_tables.row_data:
                self.data_tables.row_data.remove(checked_row)

        Clock.schedule_once(deselect_rows)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")


class ServiceSupport(MDScreen):

    def __init__(self, **kwargs):
        super(ServiceSupport, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")

    def show_customer_support_dialog(self):
        dialog = MDDialog(
            title="Contact Client Support",
            text="Call Client Support at: +1-800-123-4567",
            elevation=0
        )
        dialog.open()

    def show_doctor_dialog(self):
        dialog = MDDialog(
            title="Call On-Call Client Support",
            text="Call On-Call Client Support at: +1-888-765-4321",
            elevation=0
        )
        dialog.open()

    def submit_ticket(self):
        title = self.ids.issue_title.text
        description = self.ids.issue_description.text

        # if not title or not description:
        #     screen.ids.issue_title.error = "Please fill in all fields."
        #     return

        # Perform ticket submission logic here
        print(f"Ticket submitted:\nTitle: {title}\nDescription: {description}")

    def clear_text_input(self):
        self.ids.issue_title.text = ''
        self.ids.issue_description.text = ''

    def show_ticket_popup(self):
        submitted_text = self.ids.issue_title.text
        # Create and show the popup
        ticket_popup = MDDialog(
            title="Ticket Raised",
            elevation=0,
            text=f"Ticket with content '{submitted_text}' has been raised.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    md_bg_color=(1, 0, 0, 1),
                    theme_text_color="Custom",  # Use custom text color
                    text_color=(1, 1, 1, 1),  # White text color
                    font_size="13sp",  # Set the font size
                    on_release=lambda *args: ticket_popup.dismiss()
                ),
            ],
        )
        ticket_popup.open()
        self.ids.issue_title.text = ''
        self.ids.issue_description.text = ''

    # dialog box
    def show_validation_dialog(self, message):
        # Display a dialog for invalid login or sign up
        dialog = MDDialog(
            text=message,
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()


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
