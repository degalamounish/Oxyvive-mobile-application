from kivy.core.window import Window

from form_validation import BaseRegistrationScreen


class HospitalService(BaseRegistrationScreen):
    def __init__(self, **kwargs):
        super(HospitalService, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            super().on_back_button()
            return True
        return False

    def validate_content(self):
        super().validate_content('oxiclinic')