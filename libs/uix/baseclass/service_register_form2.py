import json
import re
import sqlite3
import string
import random

import anvil
from anvil.tables import app_tables
from kivymd.toast import toast

from server import Server
from anvil import BlobMedia

from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen


class HorizontalLineWidget(MDBoxLayout):
    pass


class ServiceRegisterForm2(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceRegisterForm2, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.server = Server()
        # anvil.server.connect("server_VL2UZDSYOLIQMHPWT2MEQGTG-3VWJQYM6QFUZ2UGR")

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("service_register_form1", "right")

    def is_all_tables_empty(self, tables):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            for table_name in tables:
                # Execute SQL to check if the table has any rows
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]

                if count > 0:
                    return False  # At least one table is not empty

            return True  # All tables are empty

        except sqlite3.Error as e:
            print("Error checking if tables are empty:", e)
            return False

        finally:
            conn.close()

    def data_manager(self):
        conn = sqlite3.connect("users.db")
        cursor1 = conn.cursor()
        cursor2 = conn.cursor()
        cursor3 = conn.cursor()
        with open('service_register_data.json', 'r') as file:
            register_data = json.load(file)
            basic_data = [register_data['id'], register_data['name'], register_data['email'], register_data['password'],
                          register_data['phone'], register_data['address']]
            # print(data)
        try:

            cursor2.execute('''SELECT * FROM oxiclinic ''')
            cursor1.execute('''SELECT * FROM oxiwheel ''')
            cursor3.execute('''SELECT * FROM oxigym ''')
            oxiwheel = cursor1.fetchall()
            oxiclinic = cursor2.fetchall()
            oxigym = cursor3.fetchall()
            # print(oxiclinic)
            # print(oxiwheel)
            # print(oxigym)

            for row in oxiclinic:
                data = []
                for j in basic_data:
                    data.append(j)
                for i, item in enumerate(row):
                    data.append(item)
                # print("1---------------------------", data)
                id = data[0]
                name = data[1]
                email = data[2]
                password = data[3]
                phone = data[4]
                address = data[5]
                Oxiclinics_Name = data[6]
                established_year = data[7]
                State = data[9]
                District = data[8]
                pincode = data[10]
                address_2 = data[11]
                capsules = data[12]
                medical_licence = BlobMedia(content_type="application/octet-stream", name='medical_licence',
                                            content=data[13])
                building_licence = BlobMedia(content_type="application/octet-stream", name='building_licence',
                                             content=data[14])
                app_tables.oxiclinics.add_row(
                    oxi_id=id,
                    oxi_name=name,
                    oxi_email=email,
                    oxi_password=password,
                    oxi_phone=int(phone),
                    oxi_address=address,
                    oxiclinics_Name=Oxiclinics_Name,
                    oxiclinics_established_year=established_year,
                    oxiclinics_District=District,
                    oxiclinics_State=State,
                    oxiclinics_pincode=int(pincode),
                    oxiclinics_address=address_2,
                    oxiclinics_capsules=int(capsules),
                    oxiclinics_medical_licence=medical_licence,
                    oxiclinics_building_licence=building_licence,
                    oxiclinics_id=self.generate_unique_oxiclinic_id())

            # ------------------------------------------------------------
            for row in oxiwheel:
                data = []
                for j in basic_data:
                    data.append(j)
                for i, item in enumerate(row):
                    data.append(item)

                id = data[0]
                name = data[1]
                email = data[2]
                password = data[3]
                phone = data[4]
                address = data[5]
                Oxiwheels_Name = data[6]
                model_year = data[7]
                State = data[9]
                District = data[8]
                pincode = data[10]
                address_2 = data[11]
                capsules = data[12]
                vehicle_rc = BlobMedia(content_type="application/octet-stream", name='vehicle_rc', content=data[13])
                driving_licence = BlobMedia(content_type="application/octet-stream", name='driving_licence',
                                            content=data[14])
                app_tables.oxiwheels.add_row(
                    oxi_id=id,
                    oxi_name=name,
                    oxi_email=email,
                    oxi_password=password,
                    oxi_phone=int(phone),
                    oxi_address=address,
                    oxiwheels_Name=Oxiwheels_Name,
                    oxiwheels_model_year=model_year,
                    oxiwheels_District=District,
                    oxiwheels_State=State,
                    oxiwheels_pincode=int(pincode),
                    oxiwheels_address=address_2,
                    oxiwheels_capsules=int(capsules),
                    oxiwheels_vehicle_rc=vehicle_rc,
                    oxiwheels_driving_licence=driving_licence,
                    oxiwheels_id=self.generate_unique_oxiwheels_id())
            # -------------------------------------------------------------------
            for row in oxigym:
                data = []
                for j in basic_data:
                    data.append(j)
                for i, item in enumerate(row):
                    data.append(item)

                id = data[0]
                name = data[1]
                email = data[2]
                password = data[3]
                phone = data[4]
                address = data[5]
                Oxigyms_Name = data[6]
                established_year = data[7]
                State = data[9]
                District = data[8]
                pincode = data[10]
                address_2 = data[11]
                capsules = data[12]
                gym_licence = BlobMedia(content_type="application/octet-stream", name='gym_licence', content=data[13])
                building_licence = BlobMedia(content_type="application/octet-stream", name='building_licence',
                                             content=data[14])

                app_tables.oxigyms.add_row(oxi_id=id, oxi_name=name, oxi_email=email, oxi_password=password, oxi_phone=int(phone),
                                           oxi_address=address, oxigyms_Name=Oxigyms_Name,
                                           oxigyms_established_year=established_year, oxigyms_District=District, oxigyms_State=State,
                                           oxigyms_pincode=int(pincode), oxigyms_address=address_2, oxigyms_capsules=int(capsules),
                                           oxigyms_licence=gym_licence, oxigyms_building_licence=building_licence,oxigyms_id=self.generate_unique_oxigyms_id())

        except sqlite3.Error as e:
            print("Error inserting data:", e)
        conn.rollback()
        # cursor1.close()
        cursor2.close()
        # cursor3.close()
        conn.close()

    def delete_all_rows_from_all_tables(self):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            tables = ['oxiclinic', 'oxiwheel', 'oxigym']
            # Delete all rows from each table
            for table in tables:
                table_name = table
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"All rows deleted from table '{table_name}'")

            # Commit the transaction
            conn.commit()

        except sqlite3.Error as e:
            print("Error deleting rows from tables:", e)

        finally:
            conn.close()

    def register(self):
        print("registered")
        tables = ['oxiclinic', 'oxiwheel', 'oxigym']
        if self.is_all_tables_empty(tables):
            toast("Please add at least one service type.", duration=2)
        else:
            self.data_manager()
            print('data inserted to anvil')
            self.delete_all_rows_from_all_tables()
            print('deleted local data')
            self.manager.push_replacement("login", "right")

    def generate_unique_oxiclinic_id(self):
        prefix = "OC"
        while True:
            random_numbers = ''.join(random.choices(string.digits, k=5))
            code = prefix + random_numbers

            # Check if the code already exists in the data table
            existing_rows = app_tables.oxiclinics.get(oxiclinics_id=code)
            if not existing_rows:
                # If the code does not exist, return it
                return code

    def generate_unique_oxigyms_id(self):
        prefix = "OG"
        while True:
            random_numbers = ''.join(random.choices(string.digits, k=5))
            code = prefix + random_numbers

            # Check if the code already exists in the data table
            existing_rows = app_tables.oxigyms.get(oxigyms_id=code)
            if not existing_rows:
                # If the code does not exist, return it
                return code

    def generate_unique_oxiwheels_id(self):
        prefix = "OW"
        while True:
            random_numbers = ''.join(random.choices(string.digits, k=5))
            code = prefix + random_numbers

            # Check if the code already exists in the data table
            existing_rows = app_tables.oxiwheels.get(oxiwheels_id=code)
            if not existing_rows:
                # If the code does not exist, return it
                return code