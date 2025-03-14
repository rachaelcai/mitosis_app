import random
import time
import datetime
import sqlite3

EX_DB = "rachcai_test/weekly_log.db"

def generate_fake_data():
    start_time = datetime.datetime(2025, 3, 5)
    end_time = datetime.datetime(2025, 3, 13)
    
    conn = sqlite3.connect(EX_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS rht_table (
                    rh real, 
                    t real,  
                    bat real, 
                    timing timestamp);''')
    
    current_time = start_time
    while current_time <= end_time:
        hour = current_time.hour
        
        # Set temperature range based on time of day
        if 6 <= hour < 18:
            temp = round(random.uniform(23, 30), 2)  # Daytime temperature
        else:
            temp = round(random.uniform(15, 22), 2)  # Nighttime temperature
        
        rh = round(random.uniform(40, 70), 2)  # Humidity between 40-70%
        
        # Battery voltage decreases over 24 hours, then resets
        time_since_midnight = (current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        bat = round(4.2 - (0.7 * (time_since_midnight / 86400)), 2)  # Decrease from 4.2V to ~3.5V
        
        c.execute('''INSERT INTO rht_table (rh, t, bat, timing) 
                     VALUES (?, ?, ?, ?);''',
                  (rh, temp, bat, current_time))
        
        current_time += datetime.timedelta(minutes=5)
    
    conn.commit()
    conn.close()
    print("Fake data generation complete.")

generate_fake_data()