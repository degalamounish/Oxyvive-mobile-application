import logging
from datetime import datetime, timedelta

from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from plyer import notification


class Notification(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.notifications = []

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.notification_back()
            return True
        return False

    def notification_back(self):
        self.manager.push_replacement("client_services", "right")

    def show_notification(self, title, message):
        self.notifications.append(message)
        self.update_notification_list()
        self.push_device_notification(title, message)

    def update_notification_list(self):
        notification_list = self.ids.notification_list
        notification_list.clear_widgets()
        for notification in self.notifications:
            card = MDCard(orientation='vertical', size_hint_y=None, height="130dp", padding='20dp',
                          pos_hint={'center_x': 0.5, 'center_y': 0.5}, elevation=2)
            card.add_widget(MDLabel(text=notification, halign="center"))
            card.add_widget(MDRaisedButton(text="Mark as Read", on_release=self.mark_as_read))
            notification_list.add_widget(card)

    def mark_as_read(self, instance):
        card = instance.parent
        self.notifications.remove(card.children[1].text)
        card.parent.remove_widget(card)

    def push_device_notification(self, title, message):
        logging.info(f"Pushing device notification: {title} - {message}")

        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Oxivive",
                # app_icon="images/shot-icon.png",
                timeout=5,
                ticker="New Notification",
                toast=True
            )
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")

    def schedule_notifications(self, appointment_time):
        now = datetime.now()
        day_before = appointment_time - timedelta(days=1)
        two_hours_before = appointment_time - timedelta(hours=2)

        if day_before > now:
            delay = (day_before - now).total_seconds()
            Clock.schedule_once(lambda dt: self.show_notification("Reminder",
                                                                  "Your appointment is tomorrow at " + appointment_time.strftime(
                                                                      "%Y-%m-%d %H:%M")), delay)

        if two_hours_before > now:
            delay = (two_hours_before - now).total_seconds()
            Clock.schedule_once(lambda dt: self.show_notification("Reminder",
                                                                  "Your appointment is in 2 hours at " + appointment_time.strftime(
                                                                      "%Y-%m-%d %H:%M")), delay)
