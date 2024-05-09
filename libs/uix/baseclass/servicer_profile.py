import base64
import json
from io import BytesIO

from kivy.atlas import CoreImage
from kivy.core.window import Window
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


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
