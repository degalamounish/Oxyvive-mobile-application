import base64
import json
import os

import anvil
from anvil.tables import app_tables
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, DictProperty
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen

from server import Server


class NavigationDrawerScreen(MDScreen):
    pass


class CustomImageTile(MDSmartTile):

    def on_release(self, *args):
        print("next screen")
        pass


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class HeroItem(MDHeroFrom):
    text = StringProperty()
    text2 = StringProperty()
    tag = StringProperty()
    manager = ObjectProperty()
    id = ObjectProperty()
    details = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.tile.ids.image.ripple_duration_in_fast = 0.05

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
        # self.server = Server()
        anvil.server.connect("server_XTGZL46YXWDMB56CRKF5RIZS-ZQQ676TIQE64OWT6")
    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = f"{user_info['username']}"
        self.ids.email.text = f"{user_info['email']}"
        profile_texture = base64.b64decode(user_info['profile'])
        profile_image_path = "profile_image.png"
        with open(profile_image_path, "wb") as profile_image_file:
            profile_image_file.write(profile_texture)
        self.ids.image.source = profile_image_path
    def on_pre_enter(self):
        self.server = Server()
        self.change()

        self.on_b1()
        self.on_b2()
        self.on_b3()
        images = ['images/1.jpg','images/2.png', 'images/3.webp','images/gym.png']
        for i in images:
            environment_img = CustomImageTile(
                source=i
            )
            self.ids.box3.add_widget(environment_img)

    def on_b1(self):

        # Clear existing widgets in the container
        self.ids.box.clear_widgets()
        oxiclinics = app_tables.oxiclinics.search()
        print(oxiclinics)
        print('on_b1')

        for i, row in enumerate(oxiclinics):
            try:
                oxiclinics_image = row['oxiclinics_image'].get_bytes()
                oxiclinics_image = base64.b64encode(oxiclinics_image).decode('utf-8')
                profile_texture = base64.b64decode(oxiclinics_image)

                # Generate a dynamic file path for each image to prevent overwriting
                profile_image_path = f"oxiclinic_image_{i}.png"

                # Save the image to a file
                with open(profile_image_path, "wb") as profile_image_file:
                    profile_image_file.write(profile_texture)
            except (KeyError, AttributeError):
                # Handle the case where 'image' is missing or is None
                profile_image_path = ''

            hero_item = HeroItem(
                text=f"{profile_image_path if profile_image_path else ''}",
                tag=f"{row['oxiclinics_id']}",
                manager=self.manager,
                text2=f"{row['oxiclinics_Name']}",
                details=row


            )
            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box.add_widget(hero_item)

    def on_b2(self):
        self.ids.box1.clear_widgets()
        oxiwheels = app_tables.oxiwheels.search()
        print('on_b2')

        for i, row in enumerate(oxiwheels):
            try:
                oxiwheels_image = row['oxiwheels_image'].get_bytes()
                oxiwheels_image = base64.b64encode(oxiwheels_image).decode('utf-8')
                profile_texture = base64.b64decode(oxiwheels_image)

                # Generate a dynamic file path for each image to prevent overwriting
                profile_image_path = f"oxiwheels_image_{i}.png"

                # Save the image to a file
                with open(profile_image_path, "wb") as profile_image_file:
                    profile_image_file.write(profile_texture)
            except (KeyError, AttributeError):
                # Handle the case where 'image' is missing or is None
                profile_image_path = ''

            hero_item = HeroItem(
                text=f"{profile_image_path if profile_image_path else ''}",
                tag=f"{row['oxiwheels_id']}",
                manager=self.manager,
                text2=f"{row['oxiwheels_Name']}",


            )

            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box1.add_widget(hero_item)

    def on_b3(self):
        self.ids.box2.clear_widgets()
        oxigyms = app_tables.oxigyms.search()
        print('on_b3')

        for i, row in enumerate(oxigyms):
            try:
                oxigyms_image = row['oxigyms_image'].get_bytes()
                oxigyms_image = base64.b64encode(oxigyms_image).decode('utf-8')
                profile_texture = base64.b64decode(oxigyms_image)

                # Generate a dynamic file path for each image to prevent overwriting
                profile_image_path = f"oxigyms_image_{i}.png"

                # Save the image to a file
                with open(profile_image_path, "wb") as profile_image_file:
                    profile_image_file.write(profile_texture)
            except (KeyError, AttributeError):
                # Handle the case where 'image' is missing or is None
                profile_image_path = ''

            hero_item = HeroItem(
                text=f"{profile_image_path if profile_image_path else ''}",
                tag=f"{row['oxigyms_id']}",
                manager=self.manager,
                text2=f"{row['oxigyms_Name']}"
            )
            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box2.add_widget(hero_item)

    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = user_info['username']
        self.ids.email.text = user_info['email']

    def logout(self):
        self.manager.current_heroes = []
        self.manager.push_replacement("login", "right")
        self.ids.nav_drawer.set_state("close")
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
        self.ids.nav_drawer.set_state("close")

    def location_screen(self):
        self.manager.push("location")

    def book_now(self, organization_name, organization_address):
        print(organization_name, organization_address)
        organization_info = {'organization_name': organization_name, 'organization_address': organization_address}
        with open("organization_data.json", "w") as json_file:
            json.dump(organization_info, json_file)
        self.manager.push("hospital_booking")
