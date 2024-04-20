import sqlite3
import os
import json 
from logs.udr_logger import UdrLogger
from constant import db_location,db_directory
logger_ = UdrLogger()

class UserDatabase:
    _instance = None

    db_location = db_location
    db_directory = db_directory
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(UserDatabase, cls).__new__(cls)
            cls._instance._init_database()
        return cls._instance

    def _init_database(self):
        #Always make the path absolute
        self.db_location = os.path.abspath(self.db_location)

        # Create the directory if it doesn't exist
        if not os.path.exists(self.db_directory):
            os.makedirs(self.db_directory)

            # Set read and write permissions to the directory
            os.chmod(self.db_directory, 0o700)
        # Create a table to store user information
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                password_update BOOLEAN NOT NULL DEFAULT 0
            )
        ''')

        # Create a table to store the current login user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL
            )
        ''')

        # Create a table to store user settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                is_lockdown BOOLEAN,
                ssh_enable BOOLEAN,
                ip_manual BOOLEAN,
                dns_manual BOOLEAN
            )
        ''')

        # Create a table to store user settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS default_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT,
                password TEXT
            )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interface_name TEXT UNIQUE,
            selected_interface TEXT,
            create_on DATETIME,
            update_on DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS udr_site_user_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create the sb_site_user_master table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS udr_site_user_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                username TEXT DEFAULT NULL,
                password TEXT DEFAULT NULL,
                full_name TEXT DEFAULT NULL,
                description TEXT DEFAULT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        connection.commit()
        connection.close()

    def update_status_for_all(self):
        conn = sqlite3.connect(self.db_location)
        cursor = conn.cursor()

        try:
            # Step 1: Select all users and their current statuses
            cursor.execute('SELECT id, status FROM udr_site_user_master')
            users = cursor.fetchall()

            # Step 2: Update the status for all users in udr_site_user_master
            cursor.execute('UPDATE udr_site_user_master SET status = ?', (0,))

            # Step 3: Log each status change in the status_log table
            for user_id, status in users:
                # Check if the user ID already exists in the status_log table
                cursor.execute('SELECT 1 FROM udr_site_user_status WHERE id = ?', (user_id,))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO udr_site_user_status (id, status) VALUES (?, ?)',
                                (user_id, status))

            conn.commit()
        except Exception as e:
            logger_.log_error(f"error in changing user status for UI {str(e)}")
        finally:
            conn.close()
    
    def revert_status(self):
        conn = sqlite3.connect(self.db_location)
        cursor = conn.cursor()

        try:
            # Step 1: Fetch user_id and old_status from status_log
            cursor.execute('SELECT id, status FROM udr_site_user_status')
            changes = cursor.fetchall()

            # Step 2: Update the udr_site_user_master based on the fetched logs
            for user_id, old_status in changes:
                cursor.execute('UPDATE udr_site_user_master SET status = ? WHERE id = ?', (old_status, user_id))

            # Step 3: Delete all records from status_log after updates
            cursor.execute('DELETE FROM udr_site_user_status')

            # Commit the transaction if all operations were successful
            conn.commit()
        except Exception as e:
            # Roll back any changes if an error occurs
            conn.rollback()
            logger_.log_error(f"error in changing user status for UI {str(e)}")
        finally:
            # Ensure the connection is closed after the operation
            conn.close()
    def add_user(self, username, password, password_update=False):
        # Add a user to the database
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, password, password_update) VALUES (?, ?, ?)',
                       (username, password, password_update))
        connection.commit()
        connection.close()

    def update_default_setting(self, hostname, password):
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        # Attempt to fetch any existing row from the table
        cursor.execute('SELECT id FROM default_settings LIMIT 1')
        row = cursor.fetchone()

        if row is not None:
            # If there is an existing row, update it
            update_query = '''
                UPDATE default_settings
                SET hostname = ?, password = ?
                WHERE id = ?
            '''
            # Use the fetched id to update the specific row
            cursor.execute(update_query, (hostname, password, row[0]))
        else:
            # If there are no rows in the table, insert a new one
            insert_query = '''
                INSERT INTO default_settings (hostname, password)
                VALUES (?, ?)
            '''
            cursor.execute(insert_query, (hostname, password))
    
    def get_default_settings(self):
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        # Prepare the SELECT statement
        select_query = 'SELECT hostname, password FROM default_settings'

        # Execute the query
        cursor.execute(select_query)

        # Fetch the result
        result = cursor.fetchone()  # This fetches the first row of the results if there are any rows

        if result:
            hostname, password = result
            return hostname, password
        else:
            return None, None



    def change_password(self, username, new_password):
        # Change a user's password
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET password = ?, password_update = 1 WHERE username = ?', (new_password, username))
        connection.commit()
        connection.close()

    def default_settings(self, hostname_value, password_value):
        # Check if any entry exists in the default_settings table
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM default_settings
        ''')
        existing_entry_count = cursor.fetchone()[0]

        # If no entry exists, insert the new entry into the default_settings table
        if existing_entry_count == 0:
            cursor.execute('''
                INSERT INTO default_settings (hostname, password) VALUES (?, ?)
            ''', (hostname_value, password_value))

    def is_password_updated(self, username):
        # Check if the password is updated for a specific user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('SELECT password_update FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        connection.close()

        # If the user is found, return the value of password_update
        # If the user is not found, return None
        return result[0] if result else None

    def get_user_details(self, username):
        # Get details of a specific user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('SELECT id, username, password, password_update FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        connection.close()

        # If the user is found, return a tuple with user details
        # If the user is not found, return None
        return result if result else None

    def select_all_users(self):
        # Get details of all users
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('SELECT id, username, password, password_update FROM users')
        result = cursor.fetchall()
        connection.close()

        # Return a list of tuples containing details of all users
        return result

    def get_current_login(self):
        # Get the current login user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('SELECT username FROM current_login LIMIT 1')
        result = cursor.fetchone()
        connection.close()

        # If the current login user is found, return the username
        # If not found, return None
        return result[0] if result else None

    def update_current_login(self, username):
        # Update or insert the current login user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM current_login')  # Clear the current_login table
        cursor.execute('INSERT INTO current_login (username) VALUES (?)', (username,))
        connection.commit()
        connection.close()
    
    def logout(self):
        # Clear the current login user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM current_login')
        connection.commit()
        connection.close()

    def update_user_settings(self, username, is_lockdown=None, ssh_enable=None, ip_manual=None, dns_manual=None):
        # Update or insert user settings
        # ip_manual BOOLEAN,
        # dns_manual BOOLEAN,
        logger_.log_info("user name value {}".format(username))
        if len(username.strip()) ==0:
            return False 
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()

        
        # Check if the user exists
        cursor.execute('SELECT 1 FROM user_settings WHERE username = ?', (username,))
        user_exists = cursor.fetchone() is not None
        logger_.log_info("Update value of user")
        if user_exists:
            # Update non-None values
            update_values = {}
            if is_lockdown is not None:
                update_values['is_lockdown'] = is_lockdown
            if ssh_enable is not None:
                update_values['ssh_enable'] = ssh_enable
            if ip_manual is not None:
                update_values['ip_manual'] = ip_manual
            if dns_manual is not None:
                update_values['dns_manual'] = dns_manual
            logger_.log_info("user values {}".format(json.dumps(update_values)))
            if update_values:
                update_query = 'UPDATE user_settings SET '
                update_query += ', '.join(f'{key} = ?' for key in update_values)
                update_query += ' WHERE username = ?'

                update_params = tuple(update_values[key] for key in update_values)
                update_params += (username,)
                logger_.log_info("user values  update_params{}".format(json.dumps(update_params)))
                cursor.execute(update_query, update_params)

        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO user_settings (username, is_lockdown, ssh_enable, ip_manual, dns_manual)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, is_lockdown, ssh_enable, ip_manual, dns_manual))

        connection.commit()
        connection.close()



    def get_user_settings(self, username):
        # Get user settings for a specific user
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT is_lockdown, ssh_enable, ip_manual, dns_manual FROM user_settings WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        connection.close()

        # If user settings are found, return a tuple with is_lockdown and ssh_enable
        # If not found, return None
        return result if result else None
        
    
    def add_interface(self,interface_name, selected_interface):
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        cursor.execute('''
        INSERT INTO interfaces (interface_name, selected_interface, create_on, update_on)
        VALUES (?, ?, COALESCE(
            (SELECT create_on FROM interfaces WHERE interface_name = ?),
            CURRENT_TIMESTAMP),
            CURRENT_TIMESTAMP)
        ON CONFLICT(interface_name) 
        DO UPDATE SET
            selected_interface = excluded.selected_interface,
            update_on = CURRENT_TIMESTAMP
    ''', (interface_name, selected_interface, interface_name))
        connection.commit()
        connection.close()

    
    def get_interfaces_data(self,interface_name):
        connection = sqlite3.connect(self.db_location)
        cursor = connection.cursor()
        query = '''
        SELECT * FROM interfaces
        WHERE interface_name = ?
        '''
        cursor.execute(query, (interface_name,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    
