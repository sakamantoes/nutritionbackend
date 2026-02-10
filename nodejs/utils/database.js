const fs = require('fs').promises;
const path = require('path');

class JSONDatabase {
    constructor() {
        this.dataDir = path.join(__dirname, '..', 'data');
        this.init();
    }

    async init() {
        try {
            await fs.mkdir(this.dataDir, { recursive: true });
            
            // Initialize files if they don't exist
            const files = ['users.json', 'foods.json', 'user_foods.json', 'exercises.json'];
            
            for (const file of files) {
                const filePath = path.join(this.dataDir, file);
                try {
                    await fs.access(filePath);
                } catch {
                    await fs.writeFile(filePath, JSON.stringify([], null, 2));
                }
            }
            
            console.log('Database initialized successfully');
        } catch (error) {
            console.error('Error initializing database:', error);
        }
    }

    async readFile(filename) {
        try {
            const filePath = path.join(this.dataDir, filename);
            const data = await fs.readFile(filePath, 'utf8');
            return JSON.parse(data);
        } catch (error) {
            console.error(`Error reading ${filename}:`, error);
            return [];
        }
    }

    async writeFile(filename, data) {
        try {
            const filePath = path.join(this.dataDir, filename);
            await fs.writeFile(filePath, JSON.stringify(data, null, 2));
            return true;
        } catch (error) {
            console.error(`Error writing ${filename}:`, error);
            return false;
        }
    }

    async findOne(filename, query) {
        const data = await this.readFile(filename);
        return data.find(item => {
            for (const key in query) {
                if (item[key] !== query[key]) {
                    return false;
                }
            }
            return true;
        });
    }

    async find(filename, query = {}) {
        const data = await this.readFile(filename);
        if (Object.keys(query).length === 0) {
            return data;
        }
        return data.filter(item => {
            for (const key in query) {
                if (item[key] !== query[key]) {
                    return false;
                }
            }
            return true;
        });
    }

    async insert(filename, item) {
        const data = await this.readFile(filename);
        const newId = data.length > 0 ? Math.max(...data.map(d => d.id || 0)) + 1 : 1;
        const newItem = { id: newId, ...item, createdAt: new Date().toISOString() };
        data.push(newItem);
        await this.writeFile(filename, data);
        return newItem;
    }

    async update(filename, id, updates) {
        const data = await this.readFile(filename);
        const index = data.findIndex(item => item.id === id);
        if (index === -1) {
            return null;
        }
        data[index] = { ...data[index], ...updates, updatedAt: new Date().toISOString() };
        await this.writeFile(filename, data);
        return data[index];
    }

    async delete(filename, id) {
        const data = await this.readFile(filename);
        const index = data.findIndex(item => item.id === id);
        if (index === -1) {
            return false;
        }
        data.splice(index, 1);
        await this.writeFile(filename, data);
        return true;
    }
}

// Create singleton instance
const db = new JSONDatabase();

module.exports = {
    db,
    initDatabase: () => db.init(),
    getDatabase: () => db
};