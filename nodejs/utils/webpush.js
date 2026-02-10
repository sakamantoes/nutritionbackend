const webpush = require('web-push');
const fs = require('fs').promises;
const path = require('path');

class WebPushService {
    constructor() {
        this.subscriptions = new Map(); // user_id -> subscription[]
        this.vapidKeysPath = path.join(__dirname, '..', 'data', 'vapid-keys.json');
        
        // Initialize VAPID keys
        this.initVapidKeys();
    }
    
    async initVapidKeys() {
        try {
            const keys = await this.loadVapidKeys();
            
            if (!keys.publicKey || !keys.privateKey) {
                console.log('Generating new VAPID keys...');
                const newKeys = webpush.generateVAPIDKeys();
                await this.saveVapidKeys(newKeys);
                this.vapidKeys = newKeys;
            } else {
                this.vapidKeys = keys;
            }
            
            // Set VAPID details
            webpush.setVapidDetails(
                'mailto:nutrition@example.com',
                this.vapidKeys.publicKey,
                this.vapidKeys.privateKey
            );
            
            console.log('WebPush service initialized');
            console.log('Public Key:', this.vapidKeys.publicKey.substring(0, 50) + '...');
            
        } catch (error) {
            console.error('Failed to initialize WebPush:', error);
        }
    }
    
    async loadVapidKeys() {
        try {
            const data = await fs.readFile(this.vapidKeysPath, 'utf8');
            return JSON.parse(data);
        } catch (error) {
            return { publicKey: null, privateKey: null };
        }
    }
    
    async saveVapidKeys(keys) {
        try {
            await fs.writeFile(this.vapidKeysPath, JSON.stringify(keys, null, 2));
            console.log('VAPID keys saved');
        } catch (error) {
            console.error('Failed to save VAPID keys:', error);
        }
    }
    
    async subscribeUser(userId, subscription) {
        if (!this.subscriptions.has(userId)) {
            this.subscriptions.set(userId, []);
        }
        
        // Check if subscription already exists
        const existingSubs = this.subscriptions.get(userId);
        const exists = existingSubs.some(sub => 
            sub.endpoint === subscription.endpoint
        );
        
        if (!exists) {
            existingSubs.push(subscription);
            console.log(`User ${userId} subscribed to WebPush`);
            await this.saveSubscriptions();
            return true;
        }
        
        return false;
    }
    
    async unsubscribeUser(userId, endpoint) {
        if (this.subscriptions.has(userId)) {
            const userSubs = this.subscriptions.get(userId);
            const initialLength = userSubs.length;
            
            this.subscriptions.set(userId, 
                userSubs.filter(sub => sub.endpoint !== endpoint)
            );
            
            if (this.subscriptions.get(userId).length < initialLength) {
                console.log(`User ${userId} unsubscribed from WebPush`);
                await this.saveSubscriptions();
                return true;
            }
        }
        
        return false;
    }
    
    async unsubscribeAll(userId) {
        if (this.subscriptions.has(userId)) {
            this.subscriptions.delete(userId);
            console.log(`User ${userId} unsubscribed from all WebPush notifications`);
            await this.saveSubscriptions();
            return true;
        }
        
        return false;
    }
    
    async sendNotification(userId, payload) {
        if (!this.subscriptions.has(userId)) {
            console.log(`No subscriptions found for user ${userId}`);
            return { sent: 0, failed: 0 };
        }
        
        const subscriptions = this.subscriptions.get(userId);
        const results = {
            sent: 0,
            failed: 0,
            errors: []
        };
        
        for (const subscription of subscriptions) {
            try {
                await webpush.sendNotification(subscription, JSON.stringify(payload));
                results.sent++;
                console.log(`Notification sent to user ${userId}`);
            } catch (error) {
                results.failed++;
                results.errors.push({
                    endpoint: subscription.endpoint,
                    error: error.message
                });
                
                // If subscription is invalid, remove it
                if (error.statusCode === 410) {
                    console.log(`Removing expired subscription for user ${userId}`);
                    await this.unsubscribeUser(userId, subscription.endpoint);
                }
            }
        }
        
        return results;
    }
    
    async sendNotificationToAll(payload) {
        const results = {
            totalUsers: this.subscriptions.size,
            sent: 0,
            failed: 0,
            errors: []
        };
        
        for (const [userId] of this.subscriptions) {
            const result = await this.sendNotification(userId, payload);
            results.sent += result.sent;
            results.failed += result.failed;
            results.errors.push(...result.errors);
        }
        
        return results;
    }
    
    async getSubscriptions(userId) {
        return this.subscriptions.get(userId) || [];
    }
    
    async saveSubscriptions() {
        try {
            const dataPath = path.join(__dirname, '..', 'data', 'webpush-subscriptions.json');
            const data = Object.fromEntries(this.subscriptions);
            await fs.writeFile(dataPath, JSON.stringify(data, null, 2));
        } catch (error) {
            console.error('Failed to save subscriptions:', error);
        }
    }
    
    async loadSubscriptions() {
        try {
            const dataPath = path.join(__dirname, '..', 'data', 'webpush-subscriptions.json');
            const data = await fs.readFile(dataPath, 'utf8');
            const parsed = JSON.parse(data);
            this.subscriptions = new Map(Object.entries(parsed));
            console.log(`Loaded ${this.subscriptions.size} user subscriptions`);
        } catch (error) {
            console.log('No existing subscriptions found, starting fresh');
            this.subscriptions = new Map();
        }
    }
    
    getPublicKey() {
        return this.vapidKeys?.publicKey || null;
    }
}

// Create singleton instance
const webPushService = new WebPushService();

module.exports = webPushService;