import sqlite3
from datetime import datetime, timedelta

from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.screen import MDScreen

# Create the BookSlot table if it doesn't exist

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS BookSlot (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        book_date TEXT NOT NULL,
        book_time TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()


class AddTask(MDBoxLayout):
    manager = ObjectProperty()

    def show_start_time_picker(self):
        screen = self.manager.get_screen('slot_booking')
        screen.show_start_time_picker()

    def show_end_time_picker(self):
        screen = self.manager.get_screen('slot_booking')
        screen.show_end_time_picker()

    def add_task(self):
        screen = self.manager.get_screen('slot_booking')
        screen.add_task()


class TaskCard(MDCard):
    description = StringProperty()
    title = StringProperty()
    time = StringProperty()
    start_time = StringProperty()
    end_time = StringProperty()

    def update_position(self):
        if self.start_time and self.end_time:
            start_dt = datetime.strptime(self.start_time, "%I:%M %p")
            end_dt = datetime.strptime(self.end_time, "%I:%M %p")
            duration = (end_dt - start_dt).seconds / 3600  # duration in hours

            self.height = dp(100) * duration

            start_hour = start_dt.hour + start_dt.minute / 60
            pos_hint_y = 1 - (start_hour - 7) / 12  # Assuming 7 AM start
            self.pos_hint = {"x": 0, "top": pos_hint_y}


class TaskSchedulerScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.current_date_button = None

    def on_enter(self, *args):
        self.update_date()
        self.update_date_labels()

    def back_screen(self):
        self.manager.push_replacement('available_services')

    def update_date(self):
        now = datetime.now()
        day_name = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")

        self.ids.day_label.text = day_name
        self.ids.date_label.text = date_str

    def update_date_labels(self):
        now = datetime.now()
        date_box = self.ids.date_box
        date_box.clear_widgets()

        for i in range(8):  # Current day + next 7 days

            date = now + timedelta(days=i)
            date_button = MDRaisedButton(
                text=date.strftime("%a\n%d"),
                halign="center",
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                pos_hint={"center_y": .5},
                md_bg_color=(1, 1, 1, 1) if i != 0 else (1, 0, 0, 1),  # Default today button in red
                text_color=(0, 0, 0, 1),
                on_release=self.on_date_button_press
            )
            if i == 0:
                self.current_date_button = date_button  # Set today button as the current button
            date_box.add_widget(date_button)

    def on_date_button_press(self, instance):
        # Reset previous button color to white
        if self.current_date_button:
            self.current_date_button.md_bg_color = (1, 1, 1, 1)

        # Set new button color to red
        instance.md_bg_color = (1, 0, 0, 1)
        self.current_date_button = instance  # Update the current button reference

    def show_add_task_dialog(self):
        self.dialog = MDDialog(
            title="Add session",
            type="custom",
            content_cls=AddTask(manager=self.manager),
        )
        self.dialog.open()

    def show_start_time_picker(self, *args):
        self.dialog.content_cls.ids.end_time.text=''
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_start_time_save)
        time_dialog.open()

    def on_start_time_save(self, instance, time):
        if self.is_valid_time(time):
            self.dialog.content_cls.ids.start_time.text = time.strftime("%I:%M %p")
        else:
            self.show_invalid_time_alert()

    def show_end_time_picker(self, *args):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_end_time_save)
        time_dialog.open()

    def on_end_time_save(self, instance, time):
        start_time_str = self.dialog.content_cls.ids.start_time.text
        if not start_time_str:
            self.show_invalid_time_alert("Please select the start time first.")
            return

        start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
        if self.is_valid_time(time) and self.is_time_range_valid(start_time, time):
            self.dialog.content_cls.ids.end_time.text = time.strftime("%I:%M %p")
        else:
            self.show_invalid_time_alert("End time must be after start time and within the range 7 PM.")

    def is_valid_time(self, time):
        start_time = datetime.strptime('07:00 AM', '%I:%M %p').time()
        end_time = datetime.strptime('07:00 PM', '%I:%M %p').time()
        return start_time <= time <= end_time

    def is_time_range_valid(self, start_time, end_time):
        return start_time < end_time <= datetime.strptime('07:00 PM', '%I:%M %p').time()

    def show_invalid_time_alert(self, message="Please select a time between 7 AM and 7 PM."):
        invalid_time_dialog = MDDialog(
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: invalid_time_dialog.dismiss()
                ),
            ],
        )
        invalid_time_dialog.open()

    def add_task(self, *args):
        content = self.dialog.content_cls
        task_title = content.ids.task_title.text
        start_time = content.ids.start_time.text
        end_time = content.ids.end_time.text
        task_description = content.ids.task_description.text

        # Validate input fields
        if not task_title:
            self.show_invalid_time_alert("Please enter the task title.")
            return
        if not start_time:
            self.show_invalid_time_alert("Please select the start time.")
            return
        if not end_time:
            self.show_invalid_time_alert("Please select the end time.")
            return
        if not task_description:
            self.show_invalid_time_alert("Please enter the task description.")
            return
        task_card = TaskCard(
            title=task_title,
            start_time=start_time,
            end_time=end_time,
            description=task_description,
            md_bg_color=(1, 0, 0, 0.5),  # Light Green
        )

        task_card.update_position()

        self.ids.task_layout.add_widget(task_card)

        self.dialog.dismiss()
