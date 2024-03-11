import json

from kivy.core.window import Window
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


class ProfileCard(MDFloatLayout, CommonElevationBehavior):
    pass

class Profile(MDScreen):
    def __init__(self, **kwargs):
        super(Profile, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.profile_back()
            return True

        return False
    def on_pre_enter(self):
        self.change()

    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = f"Username : {user_info['username']}"
        self.ids.email.text = f"Email : {user_info['email']}"
        self.ids.phone.text = f"Phone no : {user_info['phone']}"
        self.ids.pincode.text = f"Pincode : {user_info['pincode']}"

    def profile_back(self):
        self.manager.push_replacement("client_services","right")
        screen = self.manager.get_screen('client_services')
        screen.ids.nav_drawer.set_state("close")
