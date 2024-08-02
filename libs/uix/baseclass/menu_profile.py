import json
import os
from datetime import datetime
from anvil import BlobMedia
from anvil.tables import app_tables
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from plyer import filechooser
from plyer.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission


class CustomPopup(Popup):
    icon_left = StringProperty("calendar")
    icon_left_color = ListProperty([1, 1, 1, 1])
    target_widget = ObjectProperty(None)

    def save_value(self, value):
        if self.target_widget:
            if isinstance(self.target_widget, Label):
                self.target_widget.text = value
            elif isinstance(self.target_widget, TextInput):
                self.target_widget.text = value
        self.dismiss()

    def cancel_value(self):
        self.dismiss()


class Profile(Screen):
    dialog = None
    current_label = None
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Profile screen initialized.")

    def go_back(self):
        self.manager.current = 'client_services'

    def notifications(self):
        self.manager.current = 'menu_notification'

    def show_value_input_popup(self, initial_text):
        print(f"Showing value input popup with initial text: {initial_text}")
        if not self.dialog:
            content_cls = MDTextField(
                hint_text=initial_text,
                text=initial_text,
                mode="rectangle",
                size_hint_y=None,
                height="30dp",
                foreground_color=(1, 0, 0, 1),
            )
            content_cls.bind(on_touch_down=self.clear_text)
            self.dialog = MDDialog(
                title="Enter Value",
                type="custom",
                content_cls=content_cls,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.close_dialog,
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        md_bg_color=(1, 0, 0, 1),
                    ),
                    MDRaisedButton(
                        text="SAVE",
                        on_release=self.save_value,
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        md_bg_color=(1, 0, 0, 1),
                    ),
                ],
            )
            self.dialog.size_hint = (None, None)
            self.dialog.size = (dp(300), dp(200))

        self.dialog.content_cls.text = initial_text
        self.dialog.open()

    def clear_text(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.text = ""

    def save_value(self, *args):
        print("Saving value from dialog.")
        if self.dialog and self.current_label:
            new_value = self.dialog.content_cls.text
            self.current_label.text = new_value
            self.close_dialog()

    def choose_profile_picture(self):
        filters = ["*.jpg", "*.jpeg", "*.png"]
        filechooser.open_file(on_selection=self.on_file_selection, filters=filters)

    def on_file_selection(self, selection):
        if not selection:
            print("No file selected")
            self.show_validation_dialog("No file selected. Please select a file.")
            return
        selected_file = selection[0]
        print(f"Selected file path: {selected_file}")
        if isinstance(selected_file, str):
            self.ids.profile_image.source = selected_file
        else:
            print(f"Invalid file path type: {type(selected_file)}")
            self.show_validation_dialog("Invalid file path. Please select a different file.")

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=lambda instance, value, date_range: self.set_date(value))
        date_dialog.open()

    def set_date(self, date):
        self.ids.dob.text = str(date)

    def on_enter(self, *args):
        self.load_user_data()

    def load_user_data(self):
        print("Loading user data.")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_user_file_path = os.path.join(script_dir, "user_data.json")
            with open(json_user_file_path, 'r') as file:
                user_info = json.load(file)
                self.ids.username.text = f"{user_info.get('username')}"
                self.ids.email.text = f"{user_info.get('email')}"
                self.ids.phone.text = f"{user_info.get('phone')}"
                self.ids.email.disabled = True
                self.ids.phone.disabled = True

                details = dict(app_tables.oxi_users.get(oxi_id=user_info.get('id')))
                if details:
                    oxi_profile = details.get('oxi_profile')
                    if oxi_profile:
                        current_dir = os.getcwd()
                        image_path = os.path.join(current_dir, 'profile_image.png')
                        with open(image_path, 'wb') as img_file:
                            img_file.write(oxi_profile.get_bytes())
                        self.ids.profile_image.source = image_path
                    self.ids.address.text = details.get('oxi_address')
                    self.ids.state.text = details.get('oxi_state')
                    self.ids.country.text = details.get('oxi_country')
                    self.ids.city.text = details.get('oxi_city')
                    self.ids.dob.text = str(details.get('oxi_dob'))
                else:
                    self.clear_fields()
        except FileNotFoundError:
            print("Error: 'user_data.json' file not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from 'user_data.json': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading user data: {e}")

    def clear_fields(self):
        self.ids.address.text = ''
        self.ids.state.text = ''
        self.ids.country.text = ''
        self.ids.city.text = ''
        self.ids.dob.text = ''

    def save_data(self):
        print("Saving data to the database.")
        try:
            # Debugging: Print the values being accessed
            print(f"Address: {self.ids.address.text}")
            print(f"City: {self.ids.city.text}")
            print(f"State: {self.ids.state.text}")
            print(f"DOB: {self.ids.dob.text}")
            print(f"Country: {self.ids.country.text}")
            print(f"Profile Image Source: {self.ids.profile_image.source}")

            address = self.ids.address.text
            city = self.ids.city.text
            state = self.ids.state.text
            date_format = "%Y-%m-%d"
            dob = datetime.strptime(self.ids.dob.text, date_format).date()
            country = self.ids.country.text
            image_path = self.ids.profile_image.source

            image_media = None
            if image_path and os.path.isfile(image_path):
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                    image_media = BlobMedia('image/png', image_data, name='profile_image.png')

            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_user_file_path = os.path.join(script_dir, "user_data.json")
            with open(json_user_file_path, 'r') as file:
                user_info = json.load(file)
            row_to_update = app_tables.oxi_users.get(oxi_id=user_info.get('id'))

            if row_to_update:
                row_to_update['oxi_address'] = address
                row_to_update['oxi_city'] = city
                row_to_update['oxi_state'] = state
                row_to_update['oxi_dob'] = dob
                row_to_update['oxi_country'] = country
                if image_media:
                    row_to_update['oxi_profile'] = image_media
                print("Data updated successfully in Anvil database")
            else:
                print("Record not found for oxi_id")
        except ValueError as e:
            print(f"ValueError: {e}")
        except AttributeError as e:
            print(f"AttributeError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving data: {e}")

    def back(self):
        self.manager.current = "client_services"

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss(force=True)
