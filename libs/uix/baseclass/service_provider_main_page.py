# -------------------service provider main-----------------------
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Ellipse
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen


# Builder.load_file("../kv/service_provider_main_page.kv")
class ServiceProviderMain(MDScreen):
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ServiceProviderMain, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("main_sc", "right")

    def service_button(self, button):
        if not self.menu:
            cities = ["Settings", "Notification"]
            items = [
                {
                    "text": city,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=city: self.select_city(x),
                } for city in cities
            ]

            # Use the first button from right_action_items as the caller

            self.menu = MDDropdownMenu(
                caller=button,
                items=items,
                width_mult=3,
                elevation=2,

                max_height=dp(100),

            )
        else:
            self.menu.dismiss()

        self.menu.open()

    def select_city(self, option):
        # Callback function when a city is selected
        if option == 'Settings':
            self.settings()
        elif option == 'Notification':
            self.notification_button_action()

        self.menu.dismiss()

    def settings(self):
        print("Settings")

    def notification_button_action(self):
        print("Notification")

    def sign_out_button_action(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "login"

class ProfileCard(MDFloatLayout, CommonElevationBehavior):
    pass

class ServiceProfile(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceProfile, self).__init__(**kwargs)
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

    edit_mode = False

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        edit_icon = self.ids.edit_button.icon
        if self.edit_mode:
            edit_icon = "check"
        else:
            edit_icon = "pencil"

        self.ids.edit_button.icon = edit_icon


class ServiceNotification(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceNotification, self).__init__(**kwargs)
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


class ServiceSlotAdding(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceSlotAdding, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=True,
            check=True,
            column_data=[
                ("No.", dp(30)),
                ("Slot No", dp(40)),
                ("Applied Date", dp(40)),
                ("Status", dp(40)),
            ],
            row_data=[("1", "A1", "01-01-2024", ([1, 0, 0, 1], 'pedding'))],
        )

        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 0.5},
            adaptive_size=True,
            padding="24dp",
            spacing="24dp",
        )

        for button_text in ["Add Slot", "Delete Checked Slots"]:
            button_box.add_widget(
                MDRaisedButton(
                    text=button_text, on_release=self.on_button_press
                )
            )

        layout = MDFloatLayout()  # root layout
        layout.add_widget(self.data_tables)
        layout.add_widget(button_box)
        self.add_widget(layout)

    def on_button_press(self, instance_button):
        try:
            {
                "Add Slot": self.add_row,
                "Delete Checked Slots": self.delete_checked_rows,
            }[instance_button.text]()
        except KeyError:
            pass

    def add_row(self):
        last_num_row = int(self.data_tables.row_data[-1][0])
        new_row_data = (
            str(last_num_row + 1),
            "C1",
            "03-03-2024",
            ([1, 1, 0, 0], 'in progress')
        )
        self.data_tables.row_data.append(list(new_row_data))

    def delete_checked_rows(self):
        def deselect_rows(*args):
            self.data_tables.table_data.select_all("normal")

        checked_rows = self.data_tables.get_row_checks()
        for checked_row in checked_rows:
            if checked_row in self.data_tables.row_data:
                self.data_tables.row_data.remove(checked_row)

        Clock.schedule_once(deselect_rows)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("servicer_dashboard", 'right')
        screen = self.manager.get_screen('servicer_dashboard')
        screen.ids.nav_drawer.set_state("close")


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


class ProfileImage(Image):
    source = StringProperty('images/hospital.png')  # Default image source

    def __init__(self, **kwargs):
        super(ProfileImage, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False

        # Apply the rounded shape
        with self.canvas.before:
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def on_size(self, *args):
        # Update the shape when the widget size changes
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size
