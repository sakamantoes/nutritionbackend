const express = require('express');
const router = express.Router();
const notificationController = require('../controllers/NotificationController');
const { validate } = require('../utils/validation');

// WebPush subscription endpoints
router.get('/public-key', notificationController.getPublicKey);
router.post('/subscribe', notificationController.subscribe);
router.post('/unsubscribe', notificationController.unsubscribe);
router.post('/unsubscribe-all', notificationController.unsubscribeAll);

// Notification sending endpoints
router.post('/send-test', notificationController.sendTestNotification);
router.post('/send-custom', notificationController.sendCustomNotification);
router.post('/send-calorie-achievement', notificationController.sendCalorieAchievement);
router.post('/send-exercise-reminder', notificationController.sendExerciseReminder);
router.post('/send-food-suggestion', notificationController.sendFoodSuggestion);

// User preferences and history
router.get('/preferences/:userId', notificationController.getPreferences);
router.put('/preferences/:userId', notificationController.updatePreferences);
router.get('/history/:userId', notificationController.getHistory);
router.get('/stats/:userId', notificationController.getStats);

module.exports = router;