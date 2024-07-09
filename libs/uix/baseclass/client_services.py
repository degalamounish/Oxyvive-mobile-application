import base64
import io
import json
import os

import anvil
from PIL.Image import Image
from anvil.tables import app_tables
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, DictProperty
from kivy.uix import image
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen

from server import Server

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image


import json
import base64
import io
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture
from PIL import Image

class Profile_screen(Screen):
    scroll_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Profile_screen, self).__init__(**kwargs)

    def on_kv_post(self, base_widget):
        print("IDs dictionary:", self.ids)  # Debugging line
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        if 'username' in self.ids:
            self.ids.username.text = user_info.get('username', '')
        else:
            print("Username ID not found")
        if 'phone' in self.ids:
            self.ids.phone.text = str(user_info.get('phone', ''))
        else:
            print("Email ID not found")

    # def on_pre_enter(self, *args):
    #     print("on_pre_enter called")
    #     self.change()
    #
    #
    # def change(self):



    def go_back(self):
        self.manager.current = 'client_services'

    def notifications(self):
        self.manager.load_screen("menu_notification")
        self.manager.push_replacement("menu_notification")

    def profile(self):
        self.manager.load_screen("menu_profile")
        self.manager.push_replacement("menu_profile")

    def Bookings(self):
        self.manager.load_screen("menu_bookings")
        self.manager.push_replacement("menu_bookings")

    def Reports(self):
        self.manager.load_screen("menu_reports")
        self.manager.push_replacement("menu_reports")

    def Support(self):
        self.manager.load_screen("menu_support")
        self.manager.push_replacement("menu_support")

    def Log_out(self):
        self.manager.push_replacement("login", "right")
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            user_info.update({
                'username': "",
                'email': "",
                'phone': "",
                'pincode': "",
                'password': ""
            })
            with open("user_data.json", "w") as json_file:
                json.dump(user_info, json_file)

            logged_in_data = {'logged_in': False}
            with open("logged_in_data.json", "w") as json_file:
                json.dump(logged_in_data, json_file)
        except FileNotFoundError:
            print("user_data.json file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

class NavigationDrawerScreen(MDScreen):
    pass


class CustomImageTile(MDSmartTile):

    def on_release(self, *args):
        print("next screen")
        pass


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

    def on_focus(self):
        pass


class HeroItem(MDHeroFrom):
    text = StringProperty()
    text2 = StringProperty()
    tag = StringProperty()
    manager = ObjectProperty()
    id = ObjectProperty()
    details = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ids.tile.ids.image.ripple_duration_in_fast = 0.05

    def on_transform_in(self, instance_hero_widget, duration):
        print('in')
        Animation(
            radius=[0, 0, 0, 0],
            box_radius=[0, 0, 0, 0],
            duration=duration,
        ).start(instance_hero_widget)

    def on_transform_out(self, instance_hero_widget, duration):
        print('out')
        Animation(
            radius=[10, 10, 10, 10],
            box_radius=[0, 0, 10, 10],
            duration=duration,
        ).start(instance_hero_widget)

    def on_release(self):
        def switch_screen(*args):
            self.manager.current_heroes = [self.tag]
            self.manager.load_screen("servicer_details")
            screen = self.manager.get_screen("servicer_details")
            screen.ids.hero_to.tag = self.tag  # Access hero_to through ids
            # Extract the table identifier and ID from the tag
            table_identifier = self.tag[:2]

            # Check and fetch the description from the appropriate table
            if table_identifier == 'OC':
                discription_row = app_tables.oxiclinics.get(oxiclinics_id=self.tag)
                if discription_row:
                    discription = discription_row['oxiclinics_discription']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'
            elif table_identifier == 'OW':
                discription_row = app_tables.oxiwheels.get(oxiwheels_id=self.tag)
                if discription_row:
                    discription = discription_row['oxiwheels_discrption']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'
            elif table_identifier == 'OG':
                discription_row = app_tables.oxigyms.get(oxigyms_id=self.tag)
                if discription_row:
                    discription = discription_row['oxigyms_discrption']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'

            print(discription)

            screen.ids.discrptions.text = discription
            self.manager.push("servicer_details")

        Clock.schedule_once(switch_screen, 0.2)


class Client_services(MDScreen):
    def __init__(self, **kwargs):
        super(Client_services, self).__init__(**kwargs)

        self.server = Server()
        # self.change()

    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = f"{user_info['username']}"
        self.ids.email.text = f"{user_info['email']}"
        try:
            profile_texture = base64.b64decode(user_info['profile'])
        except:
            # Load the image
            image_path = 'images/profile.jpg'
            # image = Image.open(image_path)

            # Convert the image to a byte array
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            profile_texture=img_byte_arr
        profile_image_path = "profile_image.png"
        with open(profile_image_path, "wb") as profile_image_file:
            profile_image_file.write(profile_texture)
        self.ids.image.source = profile_image_path

    def on_pre_enter(self):

        # self.change()
        images = ['images/1.jpg', 'images/2.png', 'images/3.webp', 'images/gym.png']
        for i in images:
            environment_img = CustomImageTile(
                source=i
            )
            # self.ids.box3.add_widget(environment_img)

    def logout(self):
        self.manager.current_heroes = []
        self.ids.bottom_nav.switch_tab('home screen')
        self.manager.push_replacement("login", "right")
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        user_info['username'] = ""
        user_info['email'] = ""
        user_info['phone'] = ""
        user_info['pincode'] = ""
        user_info['password'] = ""
        with open("user_data.json", "w") as json_file:
            json.dump(user_info, json_file)
        logged_in_data = {'logged_in': False}
        with open("logged_in_data.json", "w") as json_file:
            json.dump(logged_in_data, json_file)

    def home(self):
        self.ids.bottom_nav.switch_tab('home screen')

    def location_screen(self):
        self.manager.current_heroes = []
        self.manager.load_screen("client_location")
        self.manager.get_screen("client_location")
        self.manager.push_replacement("client_location")

    def book_now(self, organization_name, organization_address):
        print(organization_name, organization_address)
        organization_info = {'organization_name': organization_name, 'organization_address': organization_address}
        with open("organization_data.json", "w") as json_file:
            json.dump(organization_info, json_file)
        self.manager.push("hospital_booking")

    def switch_to_service_screen(self):
        self.ids.bottom_nav.switch_tab('service_screen')