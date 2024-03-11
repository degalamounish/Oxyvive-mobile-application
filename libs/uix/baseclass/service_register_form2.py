import json
import re
import sqlite3

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
                    id=id,
                    name=name,
                    email=email,
                    password=password,
                    phone=int(phone),
                    address=address,
                    Oxiclinics_Name=Oxiclinics_Name,
                    established_year=established_year,
                    District=District,
                    State=State,
                    pincode=int(pincode),
                    address_2=address_2,
                    capsules=int(capsules),
                    medical_licence=medical_licence,
                    building_licence=building_licence)

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
                    id=id,
                    name=name,
                    email=email,
                    password=password,
                    phone=int(phone),
                    address=address,
                    Oxiwheels_Name=Oxiwheels_Name,
                    model_year=model_year,
                    District=District,
                    State=State,
                    pincode=int(pincode),
                    address_2=address_2,
                    capsules=int(capsules),
                    vehicle_rc=vehicle_rc,
                    driving_licence=driving_licence)
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

                app_tables.oxigyms.add_row(id=id, name=name, email=email, password=password, phone=int(phone),
                                           address=address, Oxigyms_Name=Oxigyms_Name,
                                           established_year=established_year, District=District, State=State,
                                           pincode=int(pincode), address_2=address_2, capsules=int(capsules),
                                           gym_licence=gym_licence, building_licence=building_licence)

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
