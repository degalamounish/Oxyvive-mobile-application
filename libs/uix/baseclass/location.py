from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen


class Location(MDScreen):
    def __init__(self, **kwargs):
        super(Location, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("client_services","right")

    def fetch_pincode(self):
        pincode = self.ids.pincode.text
        if not pincode or len(pincode) != 6:
            self.ids.pincode.error = True
            self.ids.pincode.helper_text = "Invalid Pincode (6 digits required)"
        else:
            self.ids.pincode.error = False
            self.ids.pincode.helper_text = ""
            self.ids.pincode.text = ""
            app = MDApp.get_running_app()
            app.root.transition.direction = "right"
            app.root.current = "client_services"

    def get_location(self):
        try:
            pincode = 560092
            self.ids.pincode.text = pincode
        except Exception:
            self.show_validation_dialog("Error fetching pincode Please type manually")

    def show_validation_dialog(self, message):
        # Create the dialog asynchronously
        Clock.schedule_once(lambda dt: self._create_dialog(message), 0)

    def _create_dialog(self, message):
        dialog = MDDialog(
            text=f"{message}",
            elevation=0,
        )
        dialog.open()
