#-------------------service provider main-----------------------
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

# Builder.load_file("../kv/service_provider_main_page.kv")
class ServiceProviderMain(MDScreen):
    menu = ObjectProperty(None)

    # def __init__(self, **kwargs):
    #     super(ServiceProviderMain, self).__init__(**kwargs)
    #     Window.bind(on_keyboard=self.on_keyboard)
    #
    # def on_keyboard(self, instance, key, scancode, codepoint, modifier):
    #     if key == 27:  # Keycode for the back button on Android
    #         self.on_back_button()
    #         return True
    #     return False
    #
    # def on_back_button(self):
    #     self.manager.push_replacement("main_sc", "right")
    def service_button(self,button):
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

                max_height = dp(100),

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
class ServiceProfile(MDScreen):
    pass

class ServiceNotification(MDScreen):
    pass



class ServiceSlotAdding(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceSlotAdding, self).__init__(**kwargs)
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
            row_data=[("1", "A1", "01-01-2024", ([1, 0, 0, 1],'pedding'))],
        )

        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 0.5},
            adaptive_size=True,
            padding="24dp",
            spacing="24dp",
        )

        for button_text in ["Add Slot",  "Delete Checked Slots"]:
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

class ServiceSupport(MDScreen):

    pass
