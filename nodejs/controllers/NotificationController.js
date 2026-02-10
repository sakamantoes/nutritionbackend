const webPushService = require('../utils/webpush');
const notificationScheduler = require('../utils/notificationScheduler');
const { db } = require('../utils/database');

class NotificationController {
    // Get WebPush public key
    async getPublicKey(req, res) {
        try {
            const publicKey = webPushService.getPublicKey();
            
            if (!publicKey) {
                return res.status(500).json({ error: 'WebPush not initialized' });
            }
            
            res.json({
                publicKey,
                status: 'success'
            });
        } catch (error) {
            console.error('Get public key error:', error);
            res.status(500).json({ error: 'Failed to get public key' });
        }
    }
    
    // Subscribe user to WebPush
    async subscribe(req, res) {
        try {
            const { userId, subscription } = req.body;
            
            if (!userId || !subscription) {
                return res.status(400).json({ error: 'userId and subscription are required' });
            }
            
            // Validate subscription
            if (!subscription.endpoint || !subscription.keys || !subscription.keys.p256dh || !subscription.keys.auth) {
                return res.status(400).json({ error: 'Invalid subscription object' });
            }
            
            // Subscribe user
            const success = await webPushService.subscribeUser(userId, subscription);
            
            if (success) {
                // Update user notification preferences
                const user = await db.findOne('users.json', { id: parseInt(userId) });
                if (user) {
                    const prefs = user.notificationPreferences || {};
                    prefs.webPushEnabled = true;
                    prefs.lastSubscribed = new Date().toISOString();
                    await db.update('users.json', parseInt(userId), { notificationPreferences: prefs });
                }
                
                res.status(201).json({
                    message: 'Subscribed to push notifications',
                    userId,
                    status: 'success'
                });
            } else {
                res.json({
                    message: 'Already subscribed',
                    userId,
                    status: 'success'
                });
            }
        } catch (error) {
            console.error('Subscribe error:', error);
            res.status(500).json({ error: 'Failed to subscribe' });
        }
    }
    
    // Unsubscribe user from WebPush
    async unsubscribe(req, res) {
        try {
            const { userId, endpoint } = req.body;
            
            if (!userId || !endpoint) {
                return res.status(400).json({ error: 'userId and endpoint are required' });
            }
            
            const success = await webPushService.unsubscribeUser(userId, endpoint);
            
            if (success) {
                res.json({
                    message: 'Unsubscribed from push notifications',
                    userId,
                    status: 'success'
                });
            } else {
                res.status(404).json({
                    error: 'Subscription not found',
                    userId
                });
            }
        } catch (error) {
            console.error('Unsubscribe error:', error);
            res.status(500).json({ error: 'Failed to unsubscribe' });
        }
    }
    
    // Unsubscribe user from all notifications
    async unsubscribeAll(req, res) {
        try {
            const { userId } = req.body;
            
            if (!userId) {
                return res.status(400).json({ error: 'userId is required' });
            }
            
            const success = await webPushService.unsubscribeAll(userId);
            
            if (success) {
                // Update user notification preferences
                const user = await db.findOne('users.json', { id: parseInt(userId) });
                if (user) {
                    const prefs = user.notificationPreferences || {};
                    prefs.webPushEnabled = false;
                    prefs.unsubscribedAt = new Date().toISOString();
                    await db.update('users.json', parseInt(userId), { notificationPreferences: prefs });
                }
                
                res.json({
                    message: 'Unsubscribed from all push notifications',
                    userId,
                    status: 'success'
                });
            } else {
                res.status(404).json({
                    error: 'User not found or not subscribed',
                    userId
                });
            }
        } catch (error) {
            console.error('Unsubscribe all error:', error);
            res.status(500).json({ error: 'Failed to unsubscribe' });
        }
    }
    
    // Send test notification
    async sendTestNotification(req, res) {
        try {
            const { userId } = req.body;
            
            if (!userId) {
                return res.status(400).json({ error: 'userId is required' });
            }
            
            const notification = {
                title: 'Test Notification 🎯',
                body: 'This is a test notification from your nutrition tracker!',
                icon: '/icons/app-icon.png',
                badge: '/icons/badge.png',
                data: {
                    type: 'test',
                    timestamp: new Date().toISOString(),
                    action: 'test',
                    url: '/dashboard'
                }
            };
            
            const result = await notificationScheduler.sendCustomNotification(userId, notification);
            
            if (result.success) {
                res.json({
                    message: 'Test notification sent',
                    userId,
                    notification,
                    status: 'success'
                });
            } else {
                res.status(500).json({
                    error: result.error,
                    userId
                });
            }
        } catch (error) {
            console.error('Send test notification error:', error);
            res.status(500).json({ error: 'Failed to send test notification' });
        }
    }
    
    // Send custom notification
    async sendCustomNotification(req, res) {
        try {
            const { userId, title, body, data } = req.body;
            
            if (!userId || !title || !body) {
                return res.status(400).json({ error: 'userId, title, and body are required' });
            }
            
            const notification = {
                title,
                body,
                icon: '/icons/app-icon.png',
                badge: '/icons/badge.png',
                data: {
                    type: 'custom',
                    timestamp: new Date().toISOString(),
                    ...data
                }
            };
            
            const result = await notificationScheduler.sendCustomNotification(userId, notification);
            
            if (result.success) {
                res.json({
                    message: 'Custom notification sent',
                    userId,
                    notification,
                    status: 'success'
                });
            } else {
                res.status(500).json({
                    error: result.error,
                    userId
                });
            }
        } catch (error) {
            console.error('Send custom notification error:', error);
            res.status(500).json({ error: 'Failed to send custom notification' });
        }
    }
    
    // Get user notification preferences
    async getPreferences(req, res) {
        try {
            const { userId } = req.params;
            
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            const preferences = user.notificationPreferences || {
                mealReminders: true,
                waterReminders: true,
                exerciseReminders: true,
                calorieUpdates: true,
                nutritionTips: true,
                achievements: true,
                dailySummary: true,
                weeklySummary: true,
                webPushEnabled: false,
                quietHours: {
                    start: '22:00',
                    end: '07:00'
                }
            };
            
            // Check if user has active WebPush subscriptions
            const subscriptions = await webPushService.getSubscriptions(userId);
            preferences.webPushEnabled = subscriptions.length > 0;
            preferences.activeSubscriptions = subscriptions.length;
            
            res.json({
                userId,
                preferences,
                status: 'success'
            });
        } catch (error) {
            console.error('Get preferences error:', error);
            res.status(500).json({ error: 'Failed to get preferences' });
        }
    }
    
    // Update user notification preferences
    async updatePreferences(req, res) {
        try {
            const { userId } = req.params;
            const preferences = req.body;
            
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Merge with existing preferences
            const currentPrefs = user.notificationPreferences || {};
            const updatedPrefs = { ...currentPrefs, ...preferences };
            
            await db.update('users.json', parseInt(userId), {
                notificationPreferences: updatedPrefs
            });
            
            res.json({
                message: 'Notification preferences updated',
                userId,
                preferences: updatedPrefs,
                status: 'success'
            });
        } catch (error) {
            console.error('Update preferences error:', error);
            res.status(500).json({ error: 'Failed to update preferences' });
        }
    }
    
    // Get notification history for user
    async getHistory(req, res) {
        try {
            const { userId } = req.params;
            const limit = parseInt(req.query.limit) || 50;
            const offset = parseInt(req.query.offset) || 0;
            
            const logs = await db.readFile('notification_logs.json');
            const userLogs = logs.filter(log => log.userId === userId);
            
            // Sort by sentAt (newest first)
            userLogs.sort((a, b) => new Date(b.sentAt) - new Date(a.sentAt));
            
            // Paginate
            const paginatedLogs = userLogs.slice(offset, offset + limit);
            
            res.json({
                userId,
                total: userLogs.length,
                count: paginatedLogs.length,
                offset,
                limit,
                notifications: paginatedLogs,
                status: 'success'
            });
        } catch (error) {
            console.error('Get history error:', error);
            res.status(500).json({ error: 'Failed to get notification history' });
        }
    }
    
    // Send calorie goal achievement notification
    async sendCalorieAchievement(req, res) {
        try {
            const { userId, caloriesConsumed, calorieGoal, percentage } = req.body;
            
            if (!userId || !caloriesConsumed || !calorieGoal) {
                return res.status(400).json({ error: 'userId, caloriesConsumed, and calorieGoal are required' });
            }
            
            const percentageCalc = percentage || (caloriesConsumed / calorieGoal * 100);
            const roundedPercentage = Math.round(percentageCalc);
            
            let title, body;
            
            if (roundedPercentage >= 100) {
                title = 'Goal Achieved! 🎯';
                body = `You've reached your daily calorie goal of ${calorieGoal} calories!`;
            } else if (roundedPercentage >= 75) {
                title = 'Almost There! ⚡';
                body = `You're at ${roundedPercentage}% of your calorie goal. Keep going!`;
            } else if (roundedPercentage >= 50) {
                title = 'Halfway There! 📊';
                body = `You've consumed ${roundedPercentage}% of your daily calories.`;
            } else {
                title = 'Calorie Update 📈';
                body = `Current: ${caloriesConsumed}/${calorieGoal} calories (${roundedPercentage}%)`;
            }
            
            const notification = {
                title,
                body,
                icon: '/icons/calories.png',
                badge: '/icons/badge.png',
                data: {
                    type: 'calorie_achievement',
                    timestamp: new Date().toISOString(),
                    caloriesConsumed,
                    calorieGoal,
                    percentage: roundedPercentage,
                    action: 'view_dashboard',
                    url: '/dashboard'
                }
            };
            
            const result = await notificationScheduler.sendCustomNotification(userId, notification);
            
            if (result.success) {
                res.json({
                    message: 'Calorie achievement notification sent',
                    userId,
                    notification,
                    status: 'success'
                });
            } else {
                res.status(500).json({
                    error: result.error,
                    userId
                });
            }
        } catch (error) {
            console.error('Send calorie achievement error:', error);
            res.status(500).json({ error: 'Failed to send calorie achievement notification' });
        }
    }
    
    // Send exercise reminder
    async sendExerciseReminder(req, res) {
        try {
            const { userId, exerciseType } = req.body;
            
            if (!userId) {
                return res.status(400).json({ error: 'userId is required' });
            }
            
            const exercises = {
                cardio: { title: 'Cardio Time! 🏃‍♂️', body: 'Time for some cardiovascular exercise!' },
                strength: { title: 'Strength Training 💪', body: 'Build those muscles with strength training!' },
                flexibility: { title: 'Stretch Time! 🧘‍♀️', body: 'Improve flexibility with stretching exercises.' }
            };
            
            const exercise = exercises[exerciseType] || { 
                title: 'Exercise Time! 🏋️', 
                body: 'Time to get active and exercise!' 
            };
            
            const notification = {
                title: exercise.title,
                body: exercise.body,
                icon: '/icons/exercise.png',
                badge: '/icons/badge.png',
                data: {
                    type: 'exercise_reminder',
                    timestamp: new Date().toISOString(),
                    exerciseType: exerciseType || 'general',
                    action: 'log_exercise',
                    url: '/log-exercise'
                }
            };
            
            const result = await notificationScheduler.sendCustomNotification(userId, notification);
            
            if (result.success) {
                res.json({
                    message: 'Exercise reminder sent',
                    userId,
                    notification,
                    status: 'success'
                });
            } else {
                res.status(500).json({
                    error: result.error,
                    userId
                });
            }
        } catch (error) {
            console.error('Send exercise reminder error:', error);
            res.status(500).json({ error: 'Failed to send exercise reminder' });
        }
    }
    
    // Send food suggestion
    async sendFoodSuggestion(req, res) {
        try {
            const { userId, foodName, reason, calories } = req.body;
            
            if (!userId || !foodName) {
                return res.status(400).json({ error: 'userId and foodName are required' });
            }
            
            const body = reason || `Consider adding ${foodName} to your diet.`;
            const calorieText = calories ? ` (${calories} calories)` : '';
            
            const notification = {
                title: 'Food Suggestion 🥗',
                body: `${body}${calorieText}`,
                icon: '/icons/food.png',
                badge: '/icons/badge.png',
                data: {
                    type: 'food_suggestion',
                    timestamp: new Date().toISOString(),
                    foodName,
                    reason: reason || 'nutrition_balanced',
                    calories: calories || null,
                    action: 'view_food_suggestions',
                    url: '/food-suggestions'
                }
            };
            
            const result = await notificationScheduler.sendCustomNotification(userId, notification);
            
            if (result.success) {
                res.json({
                    message: 'Food suggestion sent',
                    userId,
                    notification,
                    status: 'success'
                });
            } else {
                res.status(500).json({
                    error: result.error,
                    userId
                });
            }
        } catch (error) {
            console.error('Send food suggestion error:', error);
            res.status(500).json({ error: 'Failed to send food suggestion' });
        }
    }
    
    // Get notification statistics
    async getStats(req, res) {
        try {
            const { userId } = req.params;
            
            const logs = await db.readFile('notification_logs.json');
            const userLogs = logs.filter(log => log.userId === userId);
            
            // Calculate statistics
            const stats = {
                total: userLogs.length,
                byType: {},
                byDay: {},
                last30Days: 0
            };
            
            // Count by type
            userLogs.forEach(log => {
                const type = log.data?.type || 'unknown';
                stats.byType[type] = (stats.byType[type] || 0) + 1;
            });
            
            // Count by day (last 30 days)
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            
            userLogs.forEach(log => {
                const sentDate = new Date(log.sentAt);
                if (sentDate >= thirtyDaysAgo) {
                    stats.last30Days++;
                    
                    const dayKey = sentDate.toISOString().split('T')[0];
                    stats.byDay[dayKey] = (stats.byDay[dayKey] || 0) + 1;
                }
            });
            
            // Get user preferences
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            const preferences = user?.notificationPreferences || {};
            
            // Get WebPush subscriptions
            const subscriptions = await webPushService.getSubscriptions(userId);
            
            res.json({
                userId,
                stats,
                preferences,
                webPushEnabled: subscriptions.length > 0,
                subscriptionCount: subscriptions.length,
                status: 'success'
            });
        } catch (error) {
            console.error('Get stats error:', error);
            res.status(500).json({ error: 'Failed to get notification statistics' });
        }
    }
}

module.exports = new NotificationController();