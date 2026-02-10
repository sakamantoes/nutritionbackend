// backend/nodejs/routes/exerciseRoutes.js
const express = require('express');
const router = express.Router();
const exerciseController = require('../controllers/exerciseController');
const { validate, exerciseSchema } = require('../utils/validation');

// Log exercise
router.post('/log', validate(exerciseSchema), exerciseController.logExercise);

// Get exercise recommendations for user
router.get('/recommendations/:userId', exerciseController.getRecommendations);

// Get exercise history for user
router.get('/history/:userId', exerciseController.getExerciseHistory);

// Delete exercise
router.delete('/:exerciseId', exerciseController.deleteExercise);

// Update exercise
router.put('/:exerciseId', validate(exerciseSchema), exerciseController.updateExercise);

module.exports = router;