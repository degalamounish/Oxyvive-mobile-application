from kivy.core.window import Window
from kivymd.uix.screen import MDScreen



class Booking(MDScreen):
    def __init__(self, **kwargs):
        super(Booking, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.booking_back()
            return True
        return False

    def booking_back(self):
        self.manager.push_replacement("client_services","right")
        screen = self.manager.get_screen('client_services')
        screen.ids.nav_drawer.set_state("close")
