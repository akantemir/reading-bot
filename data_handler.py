import json
from datetime import datetime, timedelta
import logging
from config import DATA_FILE

logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self):
        self.data_file = DATA_FILE
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info(f"Creating new data file: {self.data_file}")
            return {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_reading_day(self, user_id):
        user_id = str(user_id)
        today = datetime.now().strftime('%Y-%m-%d')
        if user_id not in self.data:
            self.data[user_id] = []
        if today not in self.data[user_id]:
            self.data[user_id].append(today)
            self.save_data()
            return True
        return False
    
    def get_weekly_stats(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            return []
        
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        weekly_dates = []
        
        for i in range(7):
            date_str = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
            if date_str in self.data[user_id]:
                weekly_dates.append(date_str)
        
        return weekly_dates
    
    def get_monthly_stats(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            return []
        
        today = datetime.now()
        month_start = today.replace(day=1)
        monthly_dates = []
        
        for date_str in self.data[user_id]:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj.year == today.year and date_obj.month == today.month:
                monthly_dates.append(date_str)
        
        return sorted(monthly_dates)
    
    def get_longest_streak(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data or not self.data[user_id]:
            return 0
        
        sorted_dates = sorted(self.data[user_id])
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            current_date = datetime.strptime(sorted_dates[i], '%Y-%m-%d')
            prev_date = datetime.strptime(sorted_dates[i-1], '%Y-%m-%d')
            
            if (current_date - prev_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
