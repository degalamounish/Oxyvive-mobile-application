import json
from kivymd.app import MDApp
from kivy.core.window import Window
from libs.uix.root import Root

Window.size = (320, 580)


class ShotApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Shot"

        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.softinput_mode = "below_target"

    def build(self):
        self.root = Root()
        self.root.push("main_sc")

    def on_start(self):
        with open("logged_in_data.json", "r") as json_file:
            logged_in_data = json.load(json_file)
        if logged_in_data["logged_in"] == True:
            self.root.load_screen("client_services")
            self.root.current = "client_services"
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)

        else:
            self.root.load_screen("main_sc")
            self.root.current = "main_sc"

# Run the app
if __name__ == '__main__':
    ShotApp().run()
