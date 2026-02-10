import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import threading

class NotificationService:
    """
    Handles push notifications for the nutrition tracking system.
    Supports both immediate and scheduled notifications.
    """
    
    def __init__(self):
        self.notification_queue = []
        self.user_preferences = {}
        self.notification_history = []
        self.running = False
        self.background_thread = None
        
        # Load notification templates
        self.templates = {
            'meal_reminder': {
                'title': 'Time to Eat! 🍽️',
                'body': 'Don\'t forget to log your {meal_type}.',
                'data': {'type': 'meal_reminder', 'action': 'log_meal'}
            },
            'water_reminder': {
                'title': 'Stay Hydrated! 💧',
                'body': 'Time to drink some water. Stay hydrated throughout the day!',
                'data': {'type': 'water_reminder', 'action': 'log_water'}
            },
            'exercise_reminder': {
                'title': 'Time to Move! 🏃‍♂️',
                'body': 'Get active! Your body will thank you.',
                'data': {'type': 'exercise_reminder', 'action': 'log_exercise'}
            },
            'calorie_goal': {
                'title': 'Calorie Goal Update',
                'body': 'You\'ve reached {percentage}% of your daily calorie goal.',
                'data': {'type': 'calorie_update', 'action': 'view_dashboard'}
            },
            'nutrition_tip': {
                'title': 'Nutrition Tip 💡',
                'body': '{tip}',
                'data': {'type': 'nutrition_tip', 'action': 'view_tip'}
            },
            'achievement': {
                'title': 'Achievement Unlocked! 🏆',
                'body': 'Congratulations! {achievement_message}',
                'data': {'type': 'achievement', 'action': 'view_achievements'}
            },
            'weekly_summary': {
                'title': 'Weekly Summary 📊',
                'body': 'Check out your nutrition summary for this week!',
                'data': {'type': 'weekly_summary', 'action': 'view_summary'}
            },
            'food_suggestion': {
                'title': 'Food Suggestion 🥗',
                'body': 'Based on your goals, consider adding {food_name} to your diet.',
                'data': {'type': 'food_suggestion', 'action': 'view_suggestion'}
            }
        }
        
        # Nutrition tips database
        self.nutrition_tips = [
            "Drink a glass of water before meals to help control appetite.",
            "Include protein in every meal to stay full longer.",
            "Choose whole fruits over fruit juice for more fiber.",
            "Eat a variety of colorful vegetables for different nutrients.",
            "Plan your meals ahead to avoid unhealthy choices.",
            "Read nutrition labels to make informed food choices.",
            "Cook at home more often to control ingredients.",
            "Practice mindful eating - eat slowly and enjoy your food.",
            "Include healthy fats like avocado and nuts in your diet.",
            "Don't skip breakfast - it jumpstarts your metabolism."
        ]
        
        # WebPush configuration (for browser notifications)
        self.webpush_config = {
            'vapid_public': 'YOUR_VAPID_PUBLIC_KEY',
            'vapid_private': 'YOUR_VAPID_PRIVATE_KEY'
        }
    
    def start_background_scheduler(self):
        """Start the background scheduler for timed notifications"""
        self.running = True
        self.background_thread = threading.Thread(target=self._run_scheduler)
        self.background_thread.daemon = True
        self.background_thread.start()
        print("Notification scheduler started")
    
    def stop_background_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        print("Notification scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        # Schedule daily notifications
        schedule.every().day.at("08:00").do(self._send_morning_reminders)
        schedule.every().day.at("12:00").do(self._send_lunch_reminders)
        schedule.every().day.at("18:00").do(self._send_dinner_reminders)
        schedule.every().day.at("20:00").do(self._send_evening_summary)
        
        # Schedule hourly water reminders (during waking hours)
        for hour in range(9, 21):
            schedule.every().day.at(f"{hour:02d}:00").do(self._send_water_reminders)
        
        # Schedule weekly summary on Sunday evening
        schedule.every().sunday.at("19:00").do(self._send_weekly_summaries)
        
        # Schedule random nutrition tips (3 times a day)
        schedule.every().day.at("10:00").do(self._send_nutrition_tips)
        schedule.every().day.at("15:00").do(self._send_nutrition_tips)
        schedule.every().day.at("19:30").do(self._send_nutrition_tips)
        
        # Run the scheduler
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def register_user(self, user_id: str, push_token: str, preferences: Dict = None):
        """Register a user for push notifications"""
        if preferences is None:
            preferences = {
                'meal_reminders': True,
                'water_reminders': True,
                'exercise_reminders': True,
                'calorie_updates': True,
                'nutrition_tips': True,
                'achievements': True,
                'weekly_summary': True,
                'quiet_hours': {'start': '22:00', 'end': '07:00'}
            }
        
        self.user_preferences[user_id] = {
            'push_token': push_token,
            'preferences': preferences,
            'last_notification': None,
            'notification_count': 0
        }
        
        print(f"User {user_id} registered for notifications")
    
    def unregister_user(self, user_id: str):
        """Unregister a user from push notifications"""
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
            print(f"User {user_id} unregistered from notifications")
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user notification preferences"""
        if user_id in self.user_preferences:
            self.user_preferences[user_id]['preferences'].update(preferences)
            print(f"Preferences updated for user {user_id}")
    
    def send_notification(self, user_id: str, notification_type: str, data: Dict = None):
        """Send an immediate notification to a user"""
        if user_id not in self.user_preferences:
            print(f"User {user_id} not registered for notifications")
            return False
        
        # Check if user wants this type of notification
        prefs = self.user_preferences[user_id]['preferences']
        if not prefs.get(notification_type, True):
            print(f"User {user_id} has disabled {notification_type} notifications")
            return False
        
        # Check quiet hours
        if self._in_quiet_hours(user_id):
            print(f"Skipping notification for user {user_id} during quiet hours")
            return False
        
        # Get template
        template = self.templates.get(notification_type, {})
        if not template:
            print(f"Unknown notification type: {notification_type}")
            return False
        
        # Format notification
        title = template['title']
        body = template['body']
        
        if data:
            for key, value in data.items():
                if isinstance(value, str):
                    body = body.replace(f'{{{key}}}', value)
        
        notification_data = {
            'title': title,
            'body': body,
            'data': template['data'].copy(),
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'type': notification_type
        }
        
        if data:
            notification_data['data'].update(data)
        
        # Add to queue for processing
        self.notification_queue.append(notification_data)
        
        # Store in history
        self.notification_history.append(notification_data)
        
        # Limit history size
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        print(f"Notification queued for user {user_id}: {title}")
        return True
    
    async def process_queue(self):
        """Process the notification queue (async)"""
        while self.notification_queue:
            notification = self.notification_queue.pop(0)
            await self._send_push_notification(notification)
    
    async def _send_push_notification(self, notification: Dict):
        """Send push notification to user's device"""
        user_id = notification['user_id']
        
        if user_id not in self.user_preferences:
            return
        
        push_token = self.user_preferences[user_id]['push_token']
        
        # Simulate sending notification (in real app, integrate with FCM/APNS/WebPush)
        print(f"Sending push notification to {user_id}: {notification['title']}")
        print(f"  Body: {notification['body']}")
        
        # In a real implementation, you would:
        # 1. For iOS: Use APNs (Apple Push Notification Service)
        # 2. For Android: Use FCM (Firebase Cloud Messaging)
        # 3. For Web: Use WebPush API
        
        # Update user's last notification
        self.user_preferences[user_id]['last_notification'] = notification['timestamp']
        self.user_preferences[user_id]['notification_count'] += 1
    
    def _in_quiet_hours(self, user_id: str) -> bool:
        """Check if current time is within user's quiet hours"""
        if user_id not in self.user_preferences:
            return False
        
        prefs = self.user_preferences[user_id]['preferences']
        if 'quiet_hours' not in prefs:
            return False
        
        quiet_hours = prefs['quiet_hours']
        current_time = datetime.now().time()
        start_time = datetime.strptime(quiet_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(quiet_hours['end'], '%H:%M').time()
        
        if start_time < end_time:
            return start_time <= current_time <= end_time
        else:
            return current_time >= start_time or current_time <= end_time
    
    def _send_morning_reminders(self):
        """Send morning reminders to all users"""
        current_hour = datetime.now().hour
        
        for user_id in self.user_preferences:
            # Only send if user wants meal reminders
            if self.user_preferences[user_id]['preferences'].get('meal_reminders', True):
                self.send_notification(
                    user_id,
                    'meal_reminder',
                    {'meal_type': 'breakfast'}
                )
            
            # Send nutrition tip
            if self.user_preferences[user_id]['preferences'].get('nutrition_tips', True):
                tip = self._get_random_tip()
                self.send_notification(
                    user_id,
                    'nutrition_tip',
                    {'tip': tip}
                )
    
    def _send_lunch_reminders(self):
        """Send lunch reminders to all users"""
        for user_id in self.user_preferences:
            if self.user_preferences[user_id]['preferences'].get('meal_reminders', True):
                self.send_notification(
                    user_id,
                    'meal_reminder',
                    {'meal_type': 'lunch'}
                )
    
    def _send_dinner_reminders(self):
        """Send dinner reminders to all users"""
        for user_id in self.user_preferences:
            if self.user_preferences[user_id]['preferences'].get('meal_reminders', True):
                self.send_notification(
                    user_id,
                    'meal_reminder',
                    {'meal_type': 'dinner'}
                )
    
    def _send_water_reminders(self):
        """Send water reminders to all users"""
        current_hour = datetime.now().hour
        
        # Only send during reasonable hours (9 AM to 9 PM)
        if 9 <= current_hour <= 21:
            for user_id in self.user_preferences:
                if self.user_preferences[user_id]['preferences'].get('water_reminders', True):
                    self.send_notification(user_id, 'water_reminder')
    
    def _send_evening_summary(self):
        """Send evening summary to all users"""
        for user_id in self.user_preferences:
            # Check if user has logged meals today
            # In a real app, you would check the database
            self.send_notification(
                user_id,
                'weekly_summary',
                {'time_period': 'today'}
            )
    
    def _send_weekly_summaries(self):
        """Send weekly summaries to all users"""
        for user_id in self.user_preferences:
            if self.user_preferences[user_id]['preferences'].get('weekly_summary', True):
                self.send_notification(
                    user_id,
                    'weekly_summary',
                    {'time_period': 'this week'}
                )
    
    def _send_nutrition_tips(self):
        """Send random nutrition tips to all users"""
        for user_id in self.user_preferences:
            if self.user_preferences[user_id]['preferences'].get('nutrition_tips', True):
                tip = self._get_random_tip()
                self.send_notification(
                    user_id,
                    'nutrition_tip',
                    {'tip': tip}
                )
    
    def _get_random_tip(self) -> str:
        """Get a random nutrition tip"""
        import random
        return random.choice(self.nutrition_tips)
    
    def send_calorie_update(self, user_id: str, calories_consumed: float, calorie_goal: float):
        """Send calorie goal update notification"""
        if calories_consumed <= 0 or calorie_goal <= 0:
            return
        
        percentage = (calories_consumed / calorie_goal) * 100
        
        # Only send at certain milestones
        milestones = [50, 75, 90, 100, 110]
        for milestone in milestones:
            if percentage >= milestone and percentage < milestone + 5:
                self.send_notification(
                    user_id,
                    'calorie_goal',
                    {
                        'percentage': f'{milestone}',
                        'calories_consumed': str(calories_consumed),
                        'calorie_goal': str(calorie_goal)
                    }
                )
                break
    
    def send_achievement(self, user_id: str, achievement: str):
        """Send achievement notification"""
        self.send_notification(
            user_id,
            'achievement',
            {'achievement_message': achievement}
        )
    
    def send_food_suggestion(self, user_id: str, food_name: str, reason: str = None):
        """Send food suggestion notification"""
        data = {'food_name': food_name}
        if reason:
            data['reason'] = reason
        
        self.send_notification(
            user_id,
            'food_suggestion',
            data
        )
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get notification history for a user"""
        user_history = [
            n for n in self.notification_history 
            if n['user_id'] == user_id
        ]
        return user_history[-limit:]
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get notification statistics for a user"""
        if user_id not in self.user_preferences:
            return {}
        
        user_notifications = self.get_notification_history(user_id, limit=1000)
        
        stats = {
            'total_notifications': len(user_notifications),
            'last_notification': self.user_preferences[user_id].get('last_notification'),
            'preferences': self.user_preferences[user_id]['preferences'],
            'recent_types': {}
        }
        
        # Count by type for last 30 notifications
        recent = user_notifications[-30:]
        for notification in recent:
            n_type = notification['type']
            stats['recent_types'][n_type] = stats['recent_types'].get(n_type, 0) + 1
        
        return stats

# Global notification service instance
notification_service = NotificationService()

# Start the service when module is imported
notification_service.start_background_scheduler()

# Cleanup on exit
import atexit
atexit.register(notification_service.stop_background_scheduler)