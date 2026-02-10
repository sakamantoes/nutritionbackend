const express = require('express');
const router = express.Router();
const chatbotController = require('../controllers/chatbotController');
const { validate, chatbotMessageSchema } = require('../utils/validation');

// Send message to chatbot
router.post('/message', validate(chatbotMessageSchema), chatbotController.handleMessage);

module.exports = router;