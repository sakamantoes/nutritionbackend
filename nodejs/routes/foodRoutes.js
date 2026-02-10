const express = require('express');
const router = express.Router();
const foodController = require('../controllers/foodController');
const { validate, foodLogSchema } = require('../utils/validation');

// Log food intake
router.post('/log', validate(foodLogSchema), foodController.logFood);

// Get food history for user
router.get('/history/:userId', foodController.getFoodHistory);

// Get nutrition dataset
router.get('/dataset', foodController.getNutritionDataset);

// Search foods
router.get('/search', foodController.searchFoods);

// Delete food log
router.delete('/log/:logId', foodController.deleteFoodLog);

module.exports = router;