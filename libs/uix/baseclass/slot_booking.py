import sqlite3
from datetime import datetime, timedelta

from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.modalview import ModalView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
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


class CButton(MDFlatButton):
    label_text = StringProperty("")
    slot_time = None

    def __init__(self, **kwargs):
        super(CButton, self).__init__(**kwargs)

        self.CButton_pressed = False
        self.default_md_bg_color = self.md_bg_color  # Store the default background color
        self.default_line_color = self.line_color  # Store the default line color

    def Slot_Timing(self, slot_timing):
        CButton.slot_time = slot_timing
        # Reset the colors of all buttons to their default state
        for button in self.parent.children:
            if isinstance(button, CButton):
                button.md_bg_color = button.default_md_bg_color
                button.line_color = button.default_line_color

        # Set the colors of the current button
        self.md_bg_color = (1, 0, 0, 0.1)  # Set background color
        self.line_color = (1, 0, 0, 0.5)  # Set line color
        self.CButton_pressed = True
        print(f"Selected time: {slot_timing}")


class CustomModalView(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = 'rgba(0, 0, 0, 0.2)'
        self.overlay_color = (0, 0, 0, .5)
        self.size_hint = (None, None)
        self.attach_to = TaskSchedulerScreen()
        self.height = dp(300)
        self.update_width()  # Set initial width
        self.update_position()  # Set initial position


        Window.bind(on_resize=self.on_window_resize)  # Bind resize event

    def on_window_resize(self, instance, width, height):
        self.update_width()
        self.update_position()

    def update_width(self):
        self.width = Window.width

    def update_position(self):
        self.pos = (0, 0)  # Position the modal view at the bottom of the screen

    def open(self, *args):
        self.update_position()
        return super().open(*args)

    def display_time_slots(self, time_slots):
        self.ids.time_slot_box.clear_widgets()
        for slot in time_slots:
            button = CButton(text=slot)
            button.bind(on_press=self.on_button_press)
            self.ids.time_slot_box.add_widget(button)

    def on_button_press(self, instance):
        instance.Slot_Timing(instance.text)

    def dismiss_modal(self):
        self.dismiss()

    def payment_screen(self):
        pass


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
        self.selected_date = datetime.now().date()
        self.current_date_button = None
        self.custom_modal_view = None
        self.time_slots = ['9am - 11am', '11am - 1pm', '1pm - 3pm', '3pm - 5pm', '5pm - 7pm', '7pm - 9pm']

    def on_enter(self, *args):
        self.update_date()
        self.update_date_labels()
        self.filter_time_slots()

    def back_screen(self):
        self.custom_modal_view.ids.time_slot_box.clear_widgets()
        self.hide_modal_view()
        self.manager.push_replacement('available_services')

    def update_date(self):
        now = datetime.now()
        day_name = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")

        self.ids.day_label.text = day_name
        self.ids.date_label.text = date_str

    def update_date_labels(self):
        self.now = datetime.now()
        date_box = self.ids.date_box
        date_box.clear_widgets()

        for i in range(8):  # Current day + next 7 days

            date = self.now + timedelta(days=i)
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
        # Convert button text to a datetime.date object using current year and month
        try:
            day = int(instance.text.split('\n')[1])
            self.selected_date = datetime(self.now.year, self.now.month, day).date()
        except ValueError:
            self.selected_date = None
            print("Error parsing selected date.")

        # Example output
        print(f"Selected Date: {self.selected_date}")

    def show_add_task_dialog(self, value):
        if value:
            self.show_modal_view()
        else:
            pass

        pass

    def show_modal_view(self):
        if not self.custom_modal_view:
            self.custom_modal_view = CustomModalView()

        filtered_slots = self.filter_time_slots()
        self.custom_modal_view.display_time_slots(filtered_slots)

        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.custom_modal_view)
        self.custom_modal_view.open()

    def hide_modal_view(self):
        if self.custom_modal_view:
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(on_complete=lambda *x: self.custom_modal_view.dismiss())
            anim.start(self.custom_modal_view)

    def filter_time_slots(self):
        now = datetime.now()
        filtered_slots = []
        if self.selected_date == now.date():
            current_time = now.time()
            for slot in self.time_slots:
                start_time_str, end_time_str = slot.split(' - ')
                start_time = datetime.strptime(start_time_str, '%I%p').time()
                if start_time > current_time:
                    filtered_slots.append(slot)
        else:
            filtered_slots = self.time_slots
        return filtered_slots

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
