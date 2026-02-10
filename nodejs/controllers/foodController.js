const { db } = require('../utils/database');
const fs = require('fs').promises;
const path = require('path');

class FoodController {
    // Log food intake
    async logFood(req, res) {
        try {
            const { userId, foodName, foodGroup, servingSize, calories, protein, carbs, fat, fiber, sugar, sodium, mealType, imageUrl } = req.body;
            
            // Create food log
            const foodLog = {
                id: Date.now(),
                userId: parseInt(userId),
                foodName,
                foodGroup,
                servingSize,
                calories,
                protein: protein || 0,
                carbs: carbs || 0,
                fat: fat || 0,
                fiber: fiber || 0,
                sugar: sugar || 0,
                sodium: sodium || 0,
                mealType: mealType || 'snack',
                imageUrl: imageUrl || '',
                timestamp: new Date().toISOString()
            };
            
            // Save to database
            await db.insert('user_foods.json', foodLog);
            
            res.status(201).json({
                message: 'Food logged successfully',
                foodLog
            });
        } catch (error) {
            console.error('Log food error:', error);
            res.status(500).json({ error: 'Failed to log food' });
        }
    }
    
    // Get food history for a user
    async getFoodHistory(req, res) {
        try {
            const { userId } = req.params;
            const { startDate, endDate, mealType } = req.query;
            
            // Get all food logs for user
            let foodLogs = await db.find('user_foods.json', { userId: parseInt(userId) });
            
            // Apply filters
            if (startDate) {
                const start = new Date(startDate);
                foodLogs = foodLogs.filter(food => new Date(food.timestamp) >= start);
            }
            
            if (endDate) {
                const end = new Date(endDate);
                end.setHours(23, 59, 59, 999);
                foodLogs = foodLogs.filter(food => new Date(food.timestamp) <= end);
            }
            
            if (mealType) {
                foodLogs = foodLogs.filter(food => food.mealType === mealType);
            }
            
            // Sort by timestamp (newest first)
            foodLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            res.json({
                count: foodLogs.length,
                foodLogs
            });
        } catch (error) {
            console.error('Get food history error:', error);
            res.status(500).json({ error: 'Failed to get food history' });
        }
    }
    
    // Get nutrition dataset
    async getNutritionDataset(req, res) {
        try {
            const datasetPath = path.join(__dirname, '..', 'data', 'nutrition_dataset.json');
            
            try {
                const data = await fs.readFile(datasetPath, 'utf8');
                const dataset = JSON.parse(data);
                
                // Apply filters if provided
                let filteredData = dataset;
                const { foodGroup, minCalories, maxCalories, minProtein, maxProtein } = req.query;
                
                if (foodGroup) {
                    filteredData = filteredData.filter(item => item.food_group === foodGroup);
                }
                
                if (minCalories) {
                    filteredData = filteredData.filter(item => item.energy_kcal >= parseInt(minCalories));
                }
                
                if (maxCalories) {
                    filteredData = filteredData.filter(item => item.energy_kcal <= parseInt(maxCalories));
                }
                
                if (minProtein) {
                    filteredData = filteredData.filter(item => item.protein_g >= parseInt(minProtein));
                }
                
                if (maxProtein) {
                    filteredData = filteredData.filter(item => item.protein_g <= parseInt(maxProtein));
                }
                
                // Limit results
                const limit = parseInt(req.query.limit) || 50;
                const offset = parseInt(req.query.offset) || 0;
                const paginatedData = filteredData.slice(offset, offset + limit);
                
                res.json({
                    total: filteredData.length,
                    count: paginatedData.length,
                    offset,
                    limit,
                    data: paginatedData
                });
            } catch (error) {
                // If file doesn't exist, return empty
                res.json({
                    total: 0,
                    count: 0,
                    data: []
                });
            }
        } catch (error) {
            console.error('Get nutrition dataset error:', error);
            res.status(500).json({ error: 'Failed to get nutrition dataset' });
        }
    }
    
    // Search for foods
    async searchFoods(req, res) {
        try {
            const { query } = req.query;
            
            if (!query) {
                return res.status(400).json({ error: 'Search query is required' });
            }
            
            const datasetPath = path.join(__dirname, '..', 'data', 'nutrition_dataset.json');
            
            try {
                const data = await fs.readFile(datasetPath, 'utf8');
                const dataset = JSON.parse(data);
                
                // Search in food names and groups
                const searchResults = dataset.filter(item => 
                    item.food_name.toLowerCase().includes(query.toLowerCase()) ||
                    item.food_group.toLowerCase().includes(query.toLowerCase())
                );
                
                // Limit results
                const limitedResults = searchResults.slice(0, 20);
                
                res.json({
                    query,
                    count: limitedResults.length,
                    results: limitedResults
                });
            } catch (error) {
                // If file doesn't exist, return empty
                res.json({
                    query,
                    count: 0,
                    results: []
                });
            }
        } catch (error) {
            console.error('Search foods error:', error);
            res.status(500).json({ error: 'Failed to search foods' });
        }
    }
    
    // Delete a food log
    async deleteFoodLog(req, res) {
        try {
            const { logId } = req.params;
            
            const success = await db.delete('user_foods.json', parseInt(logId));
            
            if (!success) {
                return res.status(404).json({ error: 'Food log not found' });
            }
            
            res.json({
                message: 'Food log deleted successfully'
            });
        } catch (error) {
            console.error('Delete food log error:', error);
            res.status(500).json({ error: 'Failed to delete food log' });
        }
    }
}

module.exports = new FoodController();