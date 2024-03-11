import sqlite3
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRoundFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen


class ServicesList(MDScreen):

    def __init__(self, **kwargs):
        super(ServicesList, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.name = 'list_content'
        self.table_name = None
        self.org_column_name = None

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("service_register_form2", "right")

    def load_data(self, table_name):
        self.table_name = table_name
        self.org_column_name = self.get_organization_column_name(table_name)
        initial_data = self.fetch_initial_data(table_name)

        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(1, .6),
            use_pagination=True,
            pagination_menu_pos="center",
            elevation=0,
            padding='0dp',
            check=True,
            column_data=[
                (self.org_column_name, dp(45)),
                ("City", dp(30)),
            ],
            row_data=initial_data,
        )

        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 1.2, 'center_y': .2},
            size_hint=(.9, .2),
            padding="14dp",
            spacing="14dp",
        )

        button_box.add_widget(
            MDIconButton(
                icon='trash-can-outline',
                text='Delete',
                on_release=self.on_button_press,
            )
        )

        layout = MDFloatLayout(pos_hint={"center_y": 0.465})
        layout.add_widget(self.data_tables)
        layout.add_widget(button_box)
        self.add_widget(layout)

    def confirm_action(self, instance):
        print("Confirmation button pressed")
        self.manager.push_replacement("service_register_form2", "right")

    def on_button_press(self, instance_button):
        try:
            {
                "Delete": self.delete_checked_rows,
            }[instance_button.text]()
        except KeyError:
            pass

    def fetch_initial_data(self, table_name):
        # Connect to your database and fetch data
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute(f"SELECT {self.org_column_name}, District FROM {table_name}")
        db_row_data = cursor.fetchall()

        connection.close()

        return [list(map(str, row)) for row in db_row_data]

    def get_organization_column_name(self, table_name):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        connection.close()
        if columns:
            return columns[0][1]  # First column name
        else:
            return "Organization Name"

    def delete_checked_rows(self):
        def deselect_rows(*args):
            self.data_tables.table_data.select_all("normal")

        checked_rows = self.data_tables.get_row_checks()

        # Connect to the database and delete selected rows
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        for checked_row in checked_rows:
            organization_name = checked_row[0]  # Assuming organization_name is the first column
            cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.org_column_name}=?", (organization_name,))

        connection.commit()
        connection.close()

        # Remove the deleted rows from the data_tables
        for checked_row in checked_rows:
            if checked_row in self.data_tables.row_data:
                self.data_tables.row_data.remove(checked_row)

        Clock.schedule_once(deselect_rows)



