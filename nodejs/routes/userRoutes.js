const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const { validate, userRegistrationSchema, userLoginSchema } = require('../utils/validation');

// Register new user
router.post('/register', validate(userRegistrationSchema), userController.register);

// Login user
router.post('/login', validate(userLoginSchema), userController.login);

// Get user profile
router.get('/profile/:userId', userController.getProfile);

// Update user profile
router.put('/profile/:userId', userController.updateProfile);

// Get daily nutrition summary
router.get('/summary/:userId', userController.getDailySummary);

// In userRoutes.js, add:
router.get('/nutrition/weekly/:userId', userController.getWeeklyNutrition);

module.exports = router;