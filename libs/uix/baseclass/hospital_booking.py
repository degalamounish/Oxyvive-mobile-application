import json

from kivy.core.window import Window
from kivymd.uix.screen import MDScreen


class BookingInfo(MDScreen):
    def __init__(self, **kwargs):
        super(BookingInfo, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_pre_enter(self):
        self.change()
    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        with open('organization_data.json', 'r') as file:
            organization_info = json.load(file)
        organization_info['organization_name'] = ""
        organization_info['organization_address'] = ""
        with open('organization_data.json', "w") as json_file:
            json.dump(organization_info, json_file)
        self.manager.push_replacement("client_services","right")

    def change(self):
        try:
            with open('organization_data.json', 'r') as file:
                organization_info = json.load(file)
            self.ids.organization_name.text = organization_info.get('organization_name', '')
            self.ids.organization_address.text = organization_info.get('organization_address', '')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading user_data.json: {e}")