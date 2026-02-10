const cron = require('node-cron');
const { db } = require('./database');
const webPushService = require('./webpush');
const axios = require('axios');

class NotificationScheduler {
    constructor() {
        this.tasks = new Map();
        this.initScheduler();
    }
    
    initScheduler() {
        console.log('Initializing notification scheduler...');
        
        // Schedule morning reminders (8:00 AM)
        cron.schedule('0 8 * * *', () => {
            this.sendMorningReminders();
        });
        
        // Schedule lunch reminders (12:00 PM)
        cron.schedule('0 12 * * *', () => {
            this.sendLunchReminders();
        });
        
        // Schedule dinner reminders (6:00 PM)
        cron.schedule('0 18 * * *', () => {
            this.sendDinnerReminders();
        });
        
        // Schedule water reminders (every 2 hours from 9 AM to 9 PM)
        for (let hour = 9; hour <= 21; hour += 2) {
            cron.schedule(`0 ${hour} * * *`, () => {
                this.sendWaterReminders();
            });
        }
        
        // Schedule evening summary (8:00 PM)
        cron.schedule('0 20 * * *', () => {
            this.sendEveningSummaries();
        });
        
        // Schedule weekly summary (Sunday at 7:00 PM)
        cron.schedule('0 19 * * 0', () => {
            this.sendWeeklySummaries();
        });
        
        // Schedule nutrition tips (3 times a day)
        cron.schedule('0 10 * * *', () => {
            this.sendNutritionTips();
        });
        
        cron.schedule('0 15 * * *', () => {
            this.sendNutritionTips();
        });
        
        cron.schedule('0 19 * * *', () => {
            this.sendNutritionTips();
        });
        
        console.log('Notification scheduler initialized');
    }
    
    async sendMorningReminders() {
        console.log('Sending morning reminders...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                // Check if user wants meal reminders
                const preferences = user.notificationPreferences || {};
                if (preferences.mealReminders !== false) {
                    await this.sendNotificationToUser(user.id, {
                        title: 'Good Morning! 🌅',
                        body: 'Time to log your breakfast. Start your day with a nutritious meal!',
                        icon: '/icons/breakfast.png',
                        badge: '/icons/badge.png',
                        data: {
                            type: 'meal_reminder',
                            mealType: 'breakfast',
                            timestamp: new Date().toISOString(),
                            action: 'log_meal',
                            url: '/log-meal?type=breakfast'
                        }
                    });
                }
                
                // Send daily nutrition tip
                if (preferences.nutritionTips !== false) {
                    const tip = this.getRandomNutritionTip();
                    await this.sendNotificationToUser(user.id, {
                        title: 'Nutrition Tip 💡',
                        body: tip,
                        icon: '/icons/tip.png',
                        data: {
                            type: 'nutrition_tip',
                            timestamp: new Date().toISOString(),
                            action: 'view_tip'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending morning reminders:', error);
        }
    }
    
    async sendLunchReminders() {
        console.log('Sending lunch reminders...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.mealReminders !== false) {
                    await this.sendNotificationToUser(user.id, {
                        title: 'Lunch Time! 🥗',
                        body: 'Don\'t forget to log your lunch. Keep your energy up!',
                        icon: '/icons/lunch.png',
                        data: {
                            type: 'meal_reminder',
                            mealType: 'lunch',
                            timestamp: new Date().toISOString(),
                            action: 'log_meal',
                            url: '/log-meal?type=lunch'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending lunch reminders:', error);
        }
    }
    
    async sendDinnerReminders() {
        console.log('Sending dinner reminders...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.mealReminders !== false) {
                    await this.sendNotificationToUser(user.id, {
                        title: 'Dinner Time! 🍽️',
                        body: 'Time to log your dinner. Finish your day strong!',
                        icon: '/icons/dinner.png',
                        data: {
                            type: 'meal_reminder',
                            mealType: 'dinner',
                            timestamp: new Date().toISOString(),
                            action: 'log_meal',
                            url: '/log-meal?type=dinner'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending dinner reminders:', error);
        }
    }
    
    async sendWaterReminders() {
        console.log('Sending water reminders...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.waterReminders !== false) {
                    await this.sendNotificationToUser(user.id, {
                        title: 'Stay Hydrated! 💧',
                        body: 'Time to drink some water. Staying hydrated helps with energy and focus!',
                        icon: '/icons/water.png',
                        data: {
                            type: 'water_reminder',
                            timestamp: new Date().toISOString(),
                            action: 'log_water',
                            url: '/log-water'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending water reminders:', error);
        }
    }
    
    async sendEveningSummaries() {
        console.log('Sending evening summaries...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.dailySummary !== false) {
                    // Get today's food logs
                    const today = new Date().toISOString().split('T')[0];
                    const foodLogs = await db.find('user_foods.json', { userId: user.id });
                    const todayLogs = foodLogs.filter(log => 
                        log.timestamp && log.timestamp.startsWith(today)
                    );
                    
                    // Calculate totals
                    const totalCalories = todayLogs.reduce((sum, log) => sum + (log.calories || 0), 0);
                    const totalMeals = todayLogs.filter(log => log.mealType).length;
                    
                    await this.sendNotificationToUser(user.id, {
                        title: 'Daily Summary 📊',
                        body: `Today: ${totalCalories} calories, ${totalMeals} meals logged.`,
                        icon: '/icons/summary.png',
                        data: {
                            type: 'daily_summary',
                            timestamp: new Date().toISOString(),
                            calories: totalCalories,
                            meals: totalMeals,
                            action: 'view_dashboard',
                            url: '/dashboard'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending evening summaries:', error);
        }
    }
    
    async sendWeeklySummaries() {
        console.log('Sending weekly summaries...');
        
        try {
            const users = await db.readFile('users.json');
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.weeklySummary !== false) {
                    // Get this week's food logs
                    const oneWeekAgo = new Date();
                    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                    
                    const foodLogs = await db.find('user_foods.json', { userId: user.id });
                    const weeklyLogs = foodLogs.filter(log => 
                        log.timestamp && new Date(log.timestamp) >= oneWeekAgo
                    );
                    
                    // Calculate weekly totals
                    const totalCalories = weeklyLogs.reduce((sum, log) => sum + (log.calories || 0), 0);
                    const avgDailyCalories = Math.round(totalCalories / 7);
                    
                    await this.sendNotificationToUser(user.id, {
                        title: 'Weekly Summary 📈',
                        body: `This week: ${totalCalories} total calories (avg ${avgDailyCalories}/day)`,
                        icon: '/icons/weekly.png',
                        data: {
                            type: 'weekly_summary',
                            timestamp: new Date().toISOString(),
                            totalCalories,
                            avgDailyCalories,
                            action: 'view_weekly_summary',
                            url: '/weekly-summary'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending weekly summaries:', error);
        }
    }
    
    async sendNutritionTips() {
        console.log('Sending nutrition tips...');
        
        try {
            const users = await db.readFile('users.json');
            const tip = this.getRandomNutritionTip();
            
            for (const user of users) {
                const preferences = user.notificationPreferences || {};
                if (preferences.nutritionTips !== false) {
                    await this.sendNotificationToUser(user.id, {
                        title: 'Nutrition Tip 💡',
                        body: tip,
                        icon: '/icons/tip.png',
                        data: {
                            type: 'nutrition_tip',
                            timestamp: new Date().toISOString(),
                            tip: tip,
                            action: 'view_tip'
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error sending nutrition tips:', error);
        }
    }
    
    async sendNotificationToUser(userId, payload) {
        try {
            // Check quiet hours
            const user = await db.findOne('users.json', { id: userId });
            if (user && user.notificationPreferences) {
                const quietHours = user.notificationPreferences.quietHours;
                if (quietHours && this.isInQuietHours(quietHours)) {
                    console.log(`Skipping notification for user ${userId} during quiet hours`);
                    return;
                }
            }
            
            // Send via WebPush
            const result = await webPushService.sendNotification(userId, payload);
            
            // Log the notification
            await this.logNotification(userId, {
                ...payload,
                sentAt: new Date().toISOString(),
                deliveryResult: result
            });
            
        } catch (error) {
            console.error(`Error sending notification to user ${userId}:`, error);
        }
    }
    
    isInQuietHours(quietHours) {
        if (!quietHours || !quietHours.start || !quietHours.end) {
            return false;
        }
        
        const now = new Date();
        const currentTime = now.getHours() * 60 + now.getMinutes();
        
        const startTime = this.timeToMinutes(quietHours.start);
        const endTime = this.timeToMinutes(quietHours.end);
        
        if (startTime <= endTime) {
            return currentTime >= startTime && currentTime <= endTime;
        } else {
            return currentTime >= startTime || currentTime <= endTime;
        }
    }
    
    timeToMinutes(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    }
    
    getRandomNutritionTip() {
        const tips = [
            "Drink a glass of water before meals to help control appetite.",
            "Include protein in every meal to stay full longer.",
            "Choose whole fruits over fruit juice for more fiber.",
            "Eat a variety of colorful vegetables for different nutrients.",
            "Plan your meals ahead to avoid unhealthy choices.",
            "Read nutrition labels to make informed food choices.",
            "Cook at home more often to control ingredients.",
            "Practice mindful eating - eat slowly and enjoy your food.",
            "Include healthy fats like avocado and nuts in your diet.",
            "Don't skip breakfast - it jumpstarts your metabolism.",
            "Use herbs and spices instead of salt for flavor.",
            "Choose whole grains over refined grains for more nutrients.",
            "Snack on nuts and seeds for healthy fats and protein.",
            "Stay hydrated throughout the day for better energy.",
            "Limit processed foods and opt for whole foods."
        ];
        
        return tips[Math.floor(Math.random() * tips.length)];
    }
    
    async logNotification(userId, notification) {
        try {
            const logs = await db.readFile('notification_logs.json');
            logs.push({
                id: Date.now(),
                userId,
                ...notification,
                loggedAt: new Date().toISOString()
            });
            
            await db.writeFile('notification_logs.json', logs);
        } catch (error) {
            console.error('Error logging notification:', error);
        }
    }
    
    async sendCustomNotification(userId, notificationData) {
        try {
            await this.sendNotificationToUser(userId, notificationData);
            return { success: true, message: 'Notification sent' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async sendBulkNotification(userIds, notificationData) {
        const results = {
            total: userIds.length,
            sent: 0,
            failed: 0,
            errors: []
        };
        
        for (const userId of userIds) {
            try {
                await this.sendNotificationToUser(userId, notificationData);
                results.sent++;
            } catch (error) {
                results.failed++;
                results.errors.push({
                    userId,
                    error: error.message
                });
            }
        }
        
        return results;
    }
    
    stop() {
        // Stop all scheduled tasks
        for (const task of this.tasks.values()) {
            task.stop();
        }
        this.tasks.clear();
        console.log('Notification scheduler stopped');
    }
}

// Create singleton instance
const notificationScheduler = new NotificationScheduler();

// Load existing subscriptions
webPushService.loadSubscriptions().catch(console.error);

module.exports = notificationScheduler;