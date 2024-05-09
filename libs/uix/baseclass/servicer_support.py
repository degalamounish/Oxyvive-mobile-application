from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen


class ServiceSupport(MDScreen):

    def __init__(self, **kwargs):
        super(ServiceSupport, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")

    def show_customer_support_dialog(self):
        dialog = MDDialog(
            title="Contact Client Support",
            text="Call Client Support at: +1-800-123-4567",
            elevation=0
        )
        dialog.open()

    def show_doctor_dialog(self):
        dialog = MDDialog(
            title="Call On-Call Client Support",
            text="Call On-Call Client Support at: +1-888-765-4321",
            elevation=0
        )
        dialog.open()

    def submit_ticket(self):
        title = self.ids.issue_title.text
        description = self.ids.issue_description.text

        # if not title or not description:
        #     screen.ids.issue_title.error = "Please fill in all fields."
        #     return

        # Perform ticket submission logic here
        print(f"Ticket submitted:\nTitle: {title}\nDescription: {description}")

    def clear_text_input(self):
        self.ids.issue_title.text = ''
        self.ids.issue_description.text = ''

    def show_ticket_popup(self):
        submitted_text = self.ids.issue_title.text
        # Create and show the popup
        ticket_popup = MDDialog(
            title="Ticket Raised",
            elevation=0,
            text=f"Ticket with content '{submitted_text}' has been raised.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    md_bg_color=(1, 0, 0, 1),
                    theme_text_color="Custom",  # Use custom text color
                    text_color=(1, 1, 1, 1),  # White text color
                    font_size="13sp",  # Set the font size
                    on_release=lambda *args: ticket_popup.dismiss()
                ),
            ],
        )
        ticket_popup.open()
        self.ids.issue_title.text = ''
        self.ids.issue_description.text = ''

    # dialog box
    def show_validation_dialog(self, message):
        # Display a dialog for invalid login or sign up
        dialog = MDDialog(
            text=message,
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()
