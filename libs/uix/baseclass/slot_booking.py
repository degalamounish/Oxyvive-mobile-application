import sqlite3
from datetime import datetime, timedelta

from anvil.tables import app_tables
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.modalview import ModalView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
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
    selected_slots = []

    def __init__(self, **kwargs):
        super(CButton, self).__init__(**kwargs)
        self.CButton_pressed = False
        self.selected = False
        self.default_md_bg_color = self.md_bg_color  # Store the default background color
        self.default_line_color = self.line_color  # Store the default line color

    def Slot_Timing(self, slot_timing):
        # CButton.slot_time = slot_timing
        # CButton.selected_slots = [slot_timing]
        # Reset the colors of all buttons to their default state
        for button in self.parent.children:
            if isinstance(button, CButton):
                button.md_bg_color = button.default_md_bg_color
                button.line_color = button.default_line_color

        # Set the colors of the current button
        self.md_bg_color = (1, 0, 0, 0.1)  # Set background color
        self.line_color = (1, 0, 0, 0.5)  # Set line color
        slot_time = self.text
        CButton.slot_time = slot_time
        CButton.selected_slots = [slot_time]
        self.CButton_pressed = True
        print(f"Selected time: {CButton.slot_time}")
        print('slots :', CButton.selected_slots)



class CustomModalView2(ModalView):
    manager = ObjectProperty()
    date = StringProperty()
    servicer_id = StringProperty()

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

    def display_time_slots(self, time_slots, booked_slots):
        self.ids.time_slot_box.clear_widgets()
        for slot in time_slots:
            button_disabled = slot in booked_slots
            button_color = (0.7, 0.7, 0.7, 1) if button_disabled else (1, 1, 1, 1)
            button = CButton(text=slot, disabled=button_disabled, md_bg_color=button_color)
            button.bind(on_release=self.on_button_release)  # Use on_release event for touch-based interaction
            self.ids.time_slot_box.add_widget(button)

    def on_button_release(self, instance):
        instance.Slot_Timing(instance.text)

    def dismiss_modal(self):
        self.dismiss()
        CButton.selected_slots = []

    from datetime import datetime, timedelta

    from datetime import datetime, timedelta

    def generate_datetime(self, date_str, time_slot):
        # Parse the date string
        date = datetime.strptime(date_str, '%Y-%m-%d')

        # Parse the start time from the time slot
        start_time_str = time_slot.split(' - ')[0]
        start_time = datetime.strptime(start_time_str, '%I%p').time()

        # Combine the parsed date and start time
        combined_datetime = datetime.combine(date, start_time)

        return combined_datetime

    def format_date_and_time_left(self, selected_date, selected_slot):
        # Convert the selected date to the desired string format
        formatted_date = selected_date.strftime('%a, %d %b %I:%M %p')

        # Combine selected date and slot start time to create a datetime object
        slot_start = self.generate_datetime(selected_date.strftime('%Y-%m-%d'), selected_slot)

        # Calculate time left from the current time
        now = datetime.now()
        if slot_start < now:
            slot_start += timedelta(days=1)  # If the slot is earlier in the day, assume it's for the next day

        time_left = slot_start - now
        hours, remainder = divmod(time_left.total_seconds(), 3600)
        minutes = remainder // 60
        time_left_str = f'in {int(hours)} hours and {int(minutes)} minutes'

        return formatted_date, time_left_str

    # Example usage

    def payment_screen(self):
        self.dismiss()
        self.manager.load_screen('payment_page')
        screen = self.manager.get_screen('payment_page')
        selected_slots_str = "\n".join(filter(None, CButton.selected_slots))
        print(selected_slots_str)
        date_str = self.date  # Example date string
        selected_slot = selected_slots_str

        selected_date = self.generate_datetime(date_str, selected_slot)
        formatted_date, time_left_str = self.format_date_and_time_left(selected_date, selected_slot)
        print("Formatted Date:", formatted_date)
        print("Time Left:", time_left_str)
        print(str(self.date))
        screen.servicer_id = self.servicer_id
        screen.ids.slot_time.text = formatted_date
        screen.ids.time_left.text = time_left_str
        self.manager.push_replacement('payment_page')
        CButton.selected_slots = []


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
            pos_hint_y = 1 - (start_hour - 9) / 12  # Assuming 7 AM start
            self.pos_hint = {"x": 0, "top": pos_hint_y}


class TaskSchedulerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_date = datetime.now().date()
        self.current_date_button = None
        self.custom_modal_view = None
        self.time_slots = ['9am - 11am', '11am - 1pm', '1pm - 3pm', '3pm - 5pm', '5pm - 7pm', '7pm - 9pm']
        self.servicer_id = 'OC28857'  # Assuming a fixed servicer_id for demonstration

    def on_enter(self, *args):
        self.update_date()
        self.update_date_labels()
        self.selected_date = datetime.now().date()
        self.filter_time_slots()
        self.added_task()

    def back_screen(self):
        self.ids.task_layout.clear_widgets()
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
        self.added_task()

    def show_add_task_dialog(self, value):
        if value:
            self.show_modal_view()
        else:
            self.hide_modal_view()

    def show_modal_view(self):
        if not self.custom_modal_view:
            self.custom_modal_view = CustomModalView2(manager=self.manager)

        filtered_slots = self.filter_time_slots()
        self.custom_modal_view.display_time_slots(filtered_slots, self.hiding_slots)
        self.custom_modal_view.date = str(self.selected_date)
        self.custom_modal_view.servicer_id = self.servicer_id

        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.custom_modal_view)
        self.custom_modal_view.open()

    def hide_modal_view(self):
        if self.custom_modal_view:
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(on_complete=lambda *x: self.custom_modal_view.dismiss())
            anim.start(self.custom_modal_view)

    def get_booked_slots(self):
        servicer_id = self.servicer_id
        selected_date_str = self.selected_date
        booked_slots = app_tables.oxi_book_slot.search(serviceProvider_id=servicer_id, oxi_book_date=selected_date_str)
        return [slot['book_time'] for slot in booked_slots]

    def filter_time_slots(self):
        now = datetime.now()
        filtered_slots = []
        self.hiding_slots = []
        booked_slots = self.get_booked_slots()

        if self.selected_date == now.date():
            current_time = now.time()
            for slot in self.time_slots:
                start_time_str, end_time_str = slot.split(' - ')
                start_time = datetime.strptime(start_time_str, '%I%p').time()
                if start_time > current_time and slot not in booked_slots:
                    filtered_slots.append(slot)
                else:
                    self.hiding_slots.append(slot)
        else:
            for slot in self.time_slots:
                if slot in booked_slots:
                    self.hiding_slots.append(slot)
                else:
                    filtered_slots.append(slot)

        print('hidden slots', self.hiding_slots)
        print('filtered slots', filtered_slots)
        return self.time_slots

    def added_task(self, *args):
        self.ids.task_layout.clear_widgets()
        servicer_id = self.servicer_id
        selected_date_str = self.selected_date
        booked_slots = app_tables.oxi_book_slot.search(serviceProvider_id=servicer_id, oxi_book_date=selected_date_str)
        for task in booked_slots:
            client_name = task['username']
            print(client_name)
            time_slot = task['book_time']
            start_time, end_time = self.convert_time_slot(time_slot)
            print('start time :', start_time, 'end time :', end_time)

            description = 'abcdefghijklmnop'

            task_card = TaskCard(
                title=client_name,
                start_time=str(start_time),
                end_time=str(end_time),
                description=description,
                md_bg_color=(1, 0, 0, 0.5),  # Light Green
            )

            task_card.update_position()

            self.ids.task_layout.add_widget(task_card)

    def convert_time_slot(self, time_slot):
        start_time_str, end_time_str = time_slot.split(' - ')
        start_time = datetime.strptime(start_time_str, '%I%p').strftime('%I:%M %p')
        end_time = datetime.strptime(end_time_str, '%I%p').strftime('%I:%M %p')
        return start_time, end_time
