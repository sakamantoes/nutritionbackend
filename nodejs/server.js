const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

// Import routes
const userRoutes = require('./routes/userRoutes');
const foodRoutes = require('./routes/foodRoutes');
const exerciseRoutes = require('./routes/exerciseRoutes');
const chatbotRoutes = require('./routes/chatbotRoutes');
const notificationRoutes = require('./routes/notificationRoutes'); // NEW
const analysisRoutes = require('./routes/analysisRoutes');

// Import database utility
const { initDatabase, getDatabase } = require('./utils/database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize database
initDatabase();

// Routes
app.use('/api/users', userRoutes);
app.use('/api/foods', foodRoutes);
app.use('/api/exercises', exerciseRoutes);
app.use('/api/chatbot', chatbotRoutes);
app.use('/api/analysis', analysisRoutes);
app.use('/api/notifications', notificationRoutes); // NEW

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'Nutrition Tracker API is running',
        timestamp: new Date().toISOString(),
        services: {
            database: 'OK',
            notifications: 'OK',
            ml_integration: 'OK'
        }
    });
});

app.get('/', (req,res)=> {
    res.json({
         status: 'OK', 
        message: 'Nutrition Tracker API is running',
    })
})

// Python API proxy endpoints (existing endpoints)
// ... (keep all existing proxy endpoints) ...

// NEW: Notification test endpoint
app.post('/api/test-notification', async (req, res) => {
    try {
        const { userId, message } = req.body;
        
        if (!userId) {
            return res.status(400).json({ error: 'userId is required' });
        }
        
        // Call Python API for notification
        const response = await axios.post('http://localhost:5000/api/notifications/send', {
            user_id: userId,
            type: 'nutrition_tip',
            data: {
                tip: message || 'This is a test notification from the nutrition tracker!'
            }
        });
        
        res.json(response.data);
    } catch (error) {
        console.error('Notification test error:', error.message);
        res.status(500).json({ error: 'Failed to send test notification' });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ 
        error: 'Something went wrong!',
        message: err.message 
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        error: 'Endpoint not found',
        path: req.path,
        method: req.method
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Node.js server running on port ${PORT}`);
    console.log(`🔗 Python API should be running on http://localhost:5000`);
    console.log(`\n📱 Available endpoints:`);
    console.log(`  GET  /health - Health check`);
    console.log(`  POST /api/users/register - Register user`);
    console.log(`  POST /api/users/login - Login user`);
    console.log(`  POST /api/foods/log - Log food intake`);
    console.log(`  GET  /api/foods/history/:userId - Get food history`);
    console.log(`  POST /api/exercises/log - Log exercise`);
    console.log(`  POST /api/chatbot/message - Send message to chatbot`);
    console.log(`\n🔔 Notification Endpoints:`);
    console.log(`  GET  /api/notifications/public-key - Get WebPush public key`);
    console.log(`  POST /api/notifications/subscribe - Subscribe to push notifications`);
    console.log(`  POST /api/notifications/send-test - Send test notification`);
    console.log(`  GET  /api/notifications/preferences/:userId - Get notification preferences`);
});