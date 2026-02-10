const { db } = require('../utils/database');
const { v4: uuidv4 } = require('uuid');

class UserController {
    // Calculate daily calorie goal (make it a static method)
    static calculateCalorieGoal(age, weight, height, goal, activity_level) {
        // BMR calculation using Mifflin-St Jeor Equation
        const bmr = 10 * weight + 6.25 * height - 5 * age + 5;
        
        // Activity multipliers
        const activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        };
        
        const tdee = bmr * (activity_multipliers[activity_level] || 1.55);
        
        // Adjust based on goal
        if (goal === 'lose') {
            return Math.round(tdee - 500); // 500 calorie deficit for weight loss
        } else if (goal === 'gain') {
            return Math.round(tdee + 500); // 500 calorie surplus for weight gain
        } else { // maintain
            return Math.round(tdee);
        }
    }
    
    // Register a new user
    async register(req, res) {
        try {
            const { name, email, password, age, weight, height, goal, activity_level } = req.body;
            
            // Check if user already exists
            const existingUser = await db.findOne('users.json', { email });
            if (existingUser) {
                return res.status(400).json({ error: 'User already exists' });
            }
            
            // Create new user
            const newUser = {
                id: Date.now(),
                name,
                email,
                password, // In production, hash this!
                age,
                weight,
                height,
                goal,
                activity_level,
                daily_calorie_goal: UserController.calculateCalorieGoal(age, weight, height, goal, activity_level),
                createdAt: new Date().toISOString()
            };
            
            // Save user
            await db.insert('users.json', newUser);
            
            // Remove password from response
            const { password: _, ...userWithoutPassword } = newUser;
            
            res.status(201).json({
                message: 'User registered successfully',
                user: userWithoutPassword
            });
        } catch (error) {
            console.error('Registration error:', error);
            console.error('Error details:', error.message);
            console.error('Stack trace:', error.stack);
            res.status(500).json({ 
                error: 'Failed to register user',
                details: error.message 
            });
        }
    }
    
    // Login user
    async login(req, res) {
        try {
            const { email, password } = req.body;
            
            // Find user
            const users = await db.readFile('users.json');
            const user = users.find(u => u.email === email && u.password === password);
            
            if (!user) {
                return res.status(401).json({ error: 'Invalid credentials' });
            }
            
            // Remove password from response
            const { password: _, ...userWithoutPassword } = user;
            
            res.json({
                message: 'Login successful',
                user: userWithoutPassword
            });
        } catch (error) {
            console.error('Login error:', error);
            res.status(500).json({ error: 'Failed to login' });
        }
    }
    
    // Get user profile
    async getProfile(req, res) {
        try {
            const { userId } = req.params;
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Remove password from response
            const { password, ...userWithoutPassword } = user;
            
            res.json(userWithoutPassword);
        } catch (error) {
            console.error('Get profile error:', error);
            res.status(500).json({ error: 'Failed to get profile' });
        }
    }
    
    // Update user profile
    async updateProfile(req, res) {
        try {
            const { userId } = req.params;
            const updates = req.body;
            
            // Calculate new calorie goal if relevant fields changed
            if (updates.age || updates.weight || updates.height || updates.goal || updates.activity_level) {
                const user = await db.findOne('users.json', { id: parseInt(userId) });
                if (user) {
                    const age = updates.age || user.age;
                    const weight = updates.weight || user.weight;
                    const height = updates.height || user.height;
                    const goal = updates.goal || user.goal;
                    const activity_level = updates.activity_level || user.activity_level;
                    
                    updates.daily_calorie_goal = UserController.calculateCalorieGoal(
                        age, weight, height, goal, activity_level
                    );
                }
            }
            
            const updatedUser = await db.update('users.json', parseInt(userId), updates);
            
            if (!updatedUser) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Remove password from response
            const { password, ...userWithoutPassword } = updatedUser;
            
            res.json({
                message: 'Profile updated successfully',
                user: userWithoutPassword
            });
        } catch (error) {
            console.error('Update profile error:', error);
            res.status(500).json({ error: 'Failed to update profile' });
        }
    }
    
    // Get user's daily nutrition summary
    async getDailySummary(req, res) {
        try {
            const { userId } = req.params;
            const { date } = req.query;
            
            // Get user's food logs for the day
            const userFoods = await db.find('user_foods.json', { userId: parseInt(userId) });
            
            // Filter by date if provided
            let filteredFoods = userFoods;
            if (date) {
                filteredFoods = userFoods.filter(food => {
                    const foodDate = new Date(food.timestamp).toDateString();
                    return foodDate === new Date(date).toDateString();
                });
            }
            
            // Calculate totals
            const totals = {
                calories: 0,
                protein: 0,
                carbs: 0,
                fat: 0,
                fiber: 0,
                sugar: 0,
                sodium: 0
            };
            
            filteredFoods.forEach(food => {
                totals.calories += food.calories || 0;
                totals.protein += food.protein || 0;
                totals.carbs += food.carbs || 0;
                totals.fat += food.fat || 0;
                totals.fiber += food.fiber || 0;
                totals.sugar += food.sugar || 0;
                totals.sodium += food.sodium || 0;
            });
            
            // Get user's calorie goal
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            const calorieGoal = user ? user.daily_calorie_goal : 2000;
            
            // Calculate percentages
            const remainingCalories = Math.max(0, calorieGoal - totals.calories);
            const proteinPercentage = totals.calories > 0 ? (totals.protein * 4 / totals.calories * 100) : 0;
            const carbPercentage = totals.calories > 0 ? (totals.carbs * 4 / totals.calories * 100) : 0;
            const fatPercentage = totals.calories > 0 ? (totals.fat * 9 / totals.calories * 100) : 0;
            
            res.json({
                date: date || new Date().toISOString().split('T')[0],
                totals,
                goals: {
                    calories: calorieGoal,
                    protein: Math.round(calorieGoal * 0.15 / 4), // 15% of calories from protein
                    carbs: Math.round(calorieGoal * 0.55 / 4), // 55% of calories from carbs
                    fat: Math.round(calorieGoal * 0.30 / 9) // 30% of calories from fat
                },
                percentages: {
                    protein: proteinPercentage,
                    carbs: carbPercentage,
                    fat: fatPercentage
                },
                remainingCalories,
                foodCount: filteredFoods.length,
                meals: filteredFoods.reduce((acc, food) => {
                    if (!acc.includes(food.mealType)) {
                        acc.push(food.mealType);
                    }
                    return acc;
                }, [])
            });
        } catch (error) {
            console.error('Get daily summary error:', error);
            res.status(500).json({ error: 'Failed to get daily summary' });
        }
    }

    // In userController.js, add this method:

async getWeeklyNutrition(req, res) {
  try {
    const { userId } = req.params;
    const { weeks = 1 } = req.query;
    
    // Get user's food history for the last n weeks
    const userFoods = await db.find('user_foods.json', { userId: parseInt(userId) });
    
    // Calculate date ranges
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - (weeks * 7));
    
    // Filter foods by date range
    const filteredFoods = userFoods.filter(food => {
      const foodDate = new Date(food.timestamp);
      return foodDate >= startDate && foodDate <= endDate;
    });
    
    // Group by day and calculate totals
    const dailyTotals = {};
    
    filteredFoods.forEach(food => {
      const date = new Date(food.timestamp).toDateString();
      if (!dailyTotals[date]) {
        dailyTotals[date] = {
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0,
          sugar: 0,
          sodium: 0,
          count: 0,
        };
      }
      
      dailyTotals[date].calories += food.calories || 0;
      dailyTotals[date].protein += food.protein || 0;
      dailyTotals[date].carbs += food.carbs || 0;
      dailyTotals[date].fat += food.fat || 0;
      dailyTotals[date].fiber += food.fiber || 0;
      dailyTotals[date].sugar += food.sugar || 0;
      dailyTotals[date].sodium += food.sodium || 0;
      dailyTotals[date].count += 1;
    });
    
    // Format for chart (last 7 days)
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weeklyData = [];
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateString = date.toDateString();
      const dayName = days[date.getDay()];
      
      if (dailyTotals[dateString]) {
        weeklyData.push({
          day: dayName,
          calories: Math.round(dailyTotals[dateString].calories),
          protein: Math.round(dailyTotals[dateString].protein),
          carbs: Math.round(dailyTotals[dateString].carbs),
          fat: Math.round(dailyTotals[dateString].fat),
        });
      } else {
        weeklyData.push({
          day: dayName,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
        });
      }
    }
    
    res.json({
      weeks: parseInt(weeks),
      dailyTotals,
      weeklyData,
      totalEntries: filteredFoods.length,
    });
  } catch (error) {
    console.error('Get weekly nutrition error:', error);
    res.status(500).json({ error: 'Failed to get weekly nutrition data' });
  }
}
}

module.exports = new UserController();