import json
import os
from datetime import datetime

from anvil import BlobMedia
from anvil.tables import app_tables
from kivy.metrics import dp
# import anvil.server
# from anvil.tables import app_tables
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix import label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import OneLineAvatarListItem, MDList
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex
from plyer import filechooser


class CustomPopup(Popup):
    icon_left = StringProperty("calendar")  # Assign a default icon name
    icon_left_color = ListProperty([1, 1, 1, 1])  # Adjust color as needed
    target_widget = ObjectProperty(None)  # Reference to the target widget

    def save_value(self, value):
        # Update the target widget's text
        if self.target_widget:
            if isinstance(self.target_widget, Label):
                self.target_widget.text = value
            elif isinstance(self.target_widget, TextInput):
                self.target_widget.text = value
        self.dismiss()

    def cancel_value(self):
        self.dismiss()

class Tab(BoxLayout, MDTabsBase):
    pass

class Profile(Screen):
    dialog = None  # To store the general value input dialog
    blood_group_dialog = None  # To store the blood group selection dialog
    current_label = None  # To store the current label being edited
    manager = ObjectProperty(None)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blood_group_dialog = None
        self.dialog = None
        self.current_label = None

    def show_popup(self, label):
        self.current_label = label

        # Check if the label is for Blood group
        self.current_label = label

        # Check if the label is for Blood group
        if label.id == "blood_group_label":
            if self.current_label is None:
                print("Error: Current label is None in show_popup.")
                return
            self.show_blood_group_popup()
        else:
            self.show_value_input_popup(label.text)

    def go_back(self):
        self.manager.current = 'client_services'

    def notifications(self):
        self.manager.current = 'menu_notification'




    def show_Blood_popup(self):
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        menu_items = [
            {
                "text": group,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=group: self.set_item(x),
            } for group in blood_groups
        ]

        # Create a box layout for buttons
        box_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp')

        # Create save button
        save_button = Button(text='Save', size_hint_x=None, width='100dp', background_color=get_color_from_hex('#CC0000'))
        save_button.bind(on_release=lambda instance: dropdown_item.dismiss())
        save_button.bind(on_release=lambda instance: self.set_item(self.ids.blood_group_label.text))

        # Create cancel button
        cancel_button = Button(text='Cancel', size_hint_x=None, width='100dp',background_color=get_color_from_hex('#FF0000'))
        cancel_button.bind(on_release=lambda instance: dropdown_item.dismiss())

        box_layout.add_widget(save_button)
        box_layout.add_widget(cancel_button)

        dropdown_item = MDDropdownMenu(
            caller=self.ids.blood_group_label,
            items=menu_items,
            width_mult=4,
            width=250  # Adjust width as needed
        )
        dropdown_item.add_widget(box_layout)
        dropdown_item.open()

    def set_item(self, text_item):
        if self.ids.blood_group_label:
            self.ids.blood_group_label.text = text_item
    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def show_value_input_popup(self, initial_text):
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
            # Adjust dialog size
            self.dialog.size_hint = (None, None)
            self.dialog.size = (dp(300), dp(200))  # Example size, adjust as needed

        self.dialog.content_cls.text = initial_text
        self.dialog.open()

    def clear_text(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.text = ""

    def save_value(self, *args):
        if self.dialog and self.current_label:
            new_value = self.dialog.content_cls.text
            self.current_label.text = new_value
            self.close_dialog()

    def choose_profile_picture(self):
        filters = [("*.jpg;*.jpeg;*.png")]
        filechooser.open_file(filters=filters, on_selection=self.handle_selection)

    def handle_selection(self, selection):
        self.selection = selection
        if selection:
            selected_file = selection[0]
            self.ids.profile_image.source = selected_file
            print(f"Selected file: {selected_file}")  # Debug print

    def on_selection(self, *a, **k):
        App.get_running_app().root.ids.result.text = str(self.selection)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=lambda instance, value, date_range: self.set_date(value))
        date_dialog.open()

    def set_date(self, date):
        self.ids.dob.text = str(date)
    def on_enter(self, *args):
        self.change()

    def change(self):
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
                print(f"User Info: {user_info}")  # Print user info for debugging

                self.ids.username.text = f"{user_info.get('username')}"
                self.ids.email.text = f"{user_info.get('email')}"
                self.ids.phone.text = f"{user_info.get('phone')}"
                self.ids.pincode.text = f"{user_info.get('pincode')}"
                print(user_info.get('email'))

                details = dict(app_tables.oxi_users.get(oxi_id=user_info.get('id')))
                print(f"Details: {details}")  # Print details for debugging

                if details:
                    oxi_profile = details.get('oxi_profile')
                    if oxi_profile:
                        current_dir = os.getcwd()
                        image_path = os.path.join(current_dir, 'profile_image.png')
                        with open(image_path, 'wb') as img_file:
                            img_file.write(oxi_profile.get_bytes())
                        self.ids.profile_image.source = image_path
                    else:
                        print("Profile image not found in the database.")
                    self.ids.address.text = details.get('oxi_address')
                    self.ids.state.text = details.get('oxi_state')
                    self.ids.country.text = details.get('oxi_country')
                    self.ids.city.text = details.get('oxi_city')
                    self.ids.gender.text = details.get('oxi_gender')
                    self.ids.allergies.text = details.get('oxi_allergies')
                    self.ids.current_medications.text = details.get('oxi_current_medications')
                    self.ids.past_medications.text = details.get('oxi_past_medications')
                    self.ids.chronic_diseases.text = details.get('oxi_chronic_diseases')
                    self.ids.injuries.text = details.get('oxi_injuries')
                    self.ids.surgeries.text = details.get('oxi_surgeries')
                    self.ids.smoking_habits.text = details.get('oxi_smoking_habits')
                    self.ids.alcohol_consumption.text = details.get('oxi_alcohol_consumption')
                    self.ids.activity_level.text = details.get('oxi_activity_level')
                    self.ids.food_preference.text = details.get('oxi_food_preference')
                    self.ids.occupation.text = details.get('oxi_occupation')
                    self.ids.height.text = str(details.get('oxi_height'))
                    self.ids.weight.text = str(details.get('oxi_weight'))
                    self.ids.dob.text = str(details.get('oxi_dob'))
                    self.ids.blood_group_label.text = details.get('oxi_blood_group_label')
                else:
                    print("No details found for the user.")
                    self.clear_fields()

        except FileNotFoundError:
            print("Error: 'user_data.json' file not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from 'user_data.json': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def clear_fields(self):
        self.ids.address.text = ''
        self.ids.state.text = ''
        self.ids.country.text = ''
        self.ids.city.text = ''
        self.ids.gender.text = ''
        self.ids.allergies.text = ''
        self.ids.current_medications.text = ''
        self.ids.past_medications.text = ''
        self.ids.chronic_diseases.text = ''
        self.ids.injuries.text = ''
        self.ids.surgeries.text = ''
        self.ids.smoking_habits.text = ''
        self.ids.alcohol_consumption.text = ''
        self.ids.activity_level.text = ''
        self.ids.food_preference.text = ''
        self.ids.occupation.text = ''
        self.ids.height.text = ''
        self.ids.weight.text = ''
        self.ids.dob.text = ''
        self.ids.blood_group_label.text = ''

    def save_data(self):
        try:
            # Fetch the values from your UI elements
            address = self.ids.address.text
            city = self.ids.city.text
            state = self.ids.state.text
            date_format = "%Y-%m-%d"
            date_object = datetime.strptime(self.ids.dob.text, date_format)
            dob = date_object.date()
            country = self.ids.country.text
            gender = self.ids.gender.text
            height_f = self.ids.height.text
            weight_f = self.ids.weight.text

            # Ensure height and weight are not empty before converting to int
            if not height_f:
                raise ValueError("Height field is empty")
            height = int(height_f)

            if not weight_f:
                raise ValueError("Weight field is empty")
            weight = int(weight_f)

            blood_group_label = self.ids.blood_group_label.text
            allergies = self.ids.allergies.text
            current_medications = self.ids.current_medications.text
            past_medications = self.ids.past_medications.text
            chronic_diseases = self.ids.chronic_diseases.text
            injuries = self.ids.injuries.text
            surgeries = self.ids.surgeries.text
            smoking_habits = self.ids.smoking_habits.text
            alcohol_consumption = self.ids.alcohol_consumption.text
            activity_level = self.ids.activity_level.text
            food_preference = self.ids.food_preference.text
            occupation = self.ids.occupation.text
            blood_group = self.ids.blood_group_label.text
            image_path = self.ids.profile_image.source if 'profile_image' in self.ids else None

            # Debug print to check image path
            print(f"Image path: {image_path}")

            image_media = None
            if image_path and os.path.isfile(image_path):
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                    image_media = BlobMedia('image/png', image_data, name='profile_image.png')
            else:
                print("Image path is not valid or image does not exist.")

            # Debug print statements to check values
            print(f"address: {address}, city: {city}, state: {state}, dob: {dob}")
            print(f"country: {country}, gender: {gender}, height: {height}, weight: {weight}")
            print(f"blood_group_label: {blood_group_label}, allergies: {allergies}")
            print(f"current_medications: {current_medications}, past_medications: {past_medications}")
            print(f"chronic_diseases: {chronic_diseases}, injuries: {injuries}, surgeries: {surgeries}")
            print(f"smoking_habits: {smoking_habits}, alcohol_consumption: {alcohol_consumption}")
            print(f"activity_level: {activity_level}, food_preference: {food_preference}, occupation: {occupation}")

            # Assuming 'oxi_users' is a data table in Anvil
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            row_to_update = app_tables.oxi_users.get(oxi_id=user_info.get('id'))

            if row_to_update is not None:
                # Update the fields
                row_to_update['oxi_address'] = address
                row_to_update['oxi_city'] = city
                row_to_update['oxi_state'] = state
                row_to_update['oxi_dob'] = dob
                row_to_update['oxi_country'] = country
                row_to_update['oxi_gender'] = gender
                row_to_update['oxi_height'] = height
                row_to_update['oxi_weight'] = weight
                row_to_update['oxi_blood_group_label'] = blood_group_label
                row_to_update['oxi_allergies'] = allergies
                row_to_update['oxi_current_medications'] = current_medications
                row_to_update['oxi_past_medications'] = past_medications
                row_to_update['oxi_chronic_diseases'] = chronic_diseases
                row_to_update['oxi_injuries'] = injuries
                row_to_update['oxi_surgeries'] = surgeries
                row_to_update['oxi_smoking_habits'] = smoking_habits
                row_to_update['oxi_alcohol_consumption'] = alcohol_consumption
                row_to_update['oxi_activity_level'] = activity_level
                row_to_update['oxi_food_preference'] = food_preference
                row_to_update['oxi_occupation'] = occupation
                row_to_update['oxi_blood_group_label'] = blood_group
                if image_media:
                    row_to_update['oxi_profile'] = image_media
                else:
                    print("Error: No image saved")

                row_to_update.save()


                print("Data updated successfully in Anvil database")
            else:
                print("Record not found for oxi_id = 1")

            # Save to JSON file

        except ValueError as e:
            print(f"ValueError: {e}")
        except AttributeError as e:
            print(f"AttributeError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def back(self):
        self.manager.push_replacement("client_services", "right")
        screen = self.manager.get_screen('client_services')
        # screen.nav_drawer.set_state("close")

