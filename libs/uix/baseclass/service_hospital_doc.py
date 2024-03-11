import json
import sqlite3

from kivy.app import App
from kivy.core.window import Window

from form_validation import BaseRegistrationScreen


class HospitalServiceDoc(BaseRegistrationScreen):
    def __init__(self, **kwargs):
        super(HospitalServiceDoc, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            super().doc_reset_field()
            return True
        return False

    def file_manager_open(self, field_id):
        super().file_manager_open(field_id)

    def submit(self, classname):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        screen_to_clear = self.manager.get_screen(classname)
        doc1 = self.file_data1
        doc2 = self.file_data2
        # with open('service_register_data.json', 'r') as file:
        #     register_data = json.load(file)
        # service_provider_id = register_data['id']
        # print(service_provider_id)
        data = screen_to_clear.form_data()
        if doc1 is not None and doc2 is not None:
            data.append(doc1)
            data.append(doc2)
            # data.append(service_provider_id)
            self.file_data1 = None
            self.file_name1 = None
            self.ids.file_path.text = 'None selected'

            self.file_data2 = None
            self.file_name2 = None
            self.ids.file_path2.text = 'None selected'

            print("Data:", data)

            try:
                cursor.execute('''INSERT INTO oxiclinic (Oxiclinics_Name, established_year, District, State, pincode, 
                address, capsules, doc1, doc2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
                conn.commit()
                print("Data inserted successfully")  # Print success message
            except sqlite3.Error as e:

                conn.rollback()
            self.manager.push_replacement("service_register_form2", "right")
            self.ids.hint_label.text = ""
            if screen_to_clear:
                screen_to_clear.reset_fields()
        else:
            self.ids.hint_label.text = "Both documents are required"
        cursor.close()
        conn.close()
