// backend/nodejs/controllers/exerciseController.js - Add delete functionality
const { db } = require('../utils/database');

class ExerciseController {
    // Log exercise
    async logExercise(req, res) {
        try {
            const { userId, exerciseName, duration, caloriesBurned, exerciseType } = req.body;
            
            // Validate input
            if (!userId || !exerciseName || !duration || !caloriesBurned || !exerciseType) {
                return res.status(400).json({ error: 'All fields are required' });
            }
            
            // Create exercise log
            const exerciseLog = {
                id: Date.now(),
                userId: parseInt(userId),
                exerciseName,
                duration: parseInt(duration),
                caloriesBurned: parseInt(caloriesBurned),
                exerciseType,
                timestamp: new Date().toISOString()
            };
            
            // Save to database
            await db.insert('exercises.json', exerciseLog);
            
            res.status(201).json({
                message: 'Exercise logged successfully',
                exerciseLog
            });
        } catch (error) {
            console.error('Log exercise error:', error);
            res.status(500).json({ error: 'Failed to log exercise' });
        }
    }
    
    // Get exercise recommendations
    async getRecommendations(req, res) {
        try {
            const { userId } = req.params;
            
            // Get user profile
            const user = await db.findOne('users.json', { id: parseInt(userId) });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Get user's exercise history
            const exerciseLogs = await db.find('exercises.json', { userId: parseInt(userId) });
            
            // Calculate recent exercise frequency
            const recentExercises = exerciseLogs.filter(ex => {
                const exerciseDate = new Date(ex.timestamp);
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                return exerciseDate >= weekAgo;
            });
            
            // Get food history to calculate calorie balance
            const foodLogs = await db.find('user_foods.json', { userId: parseInt(userId) });
            const today = new Date().toISOString().split('T')[0];
            const todayFoods = foodLogs.filter(food => 
                food.timestamp.split('T')[0] === today
            );
            
            const todayCalories = todayFoods.reduce((sum, food) => sum + (food.calories || 0), 0);
            
            // Generate recommendations based on user profile and history
            let recommendations = [];
            let tips = [];
            
            // Determine workout frequency
            const weeklyFrequency = recentExercises.length;
            
            if (user.goal === 'lose') {
                if (weeklyFrequency < 3) {
                    recommendations = [
                        {
                            name: 'Beginner Cardio',
                            duration: 30,
                            calories: 250,
                            type: 'cardio',
                            description: 'Low impact for beginners'
                        },
                        {
                            name: 'Bodyweight Circuit',
                            duration: 25,
                            calories: 200,
                            type: 'strength',
                            description: 'No equipment needed'
                        }
                    ];
                    tips.push('Start with 3 workouts per week for weight loss');
                } else {
                    recommendations = [
                        {
                            name: 'HIIT Training',
                            duration: 30,
                            calories: 350,
                            type: 'cardio',
                            description: 'High intensity for maximum burn'
                        },
                        {
                            name: 'Strength Training',
                            duration: 45,
                            calories: 250,
                            type: 'strength',
                            description: 'Build muscle to boost metabolism'
                        }
                    ];
                }
            } else if (user.goal === 'gain') {
                recommendations = [
                    {
                        name: 'Heavy Lifting',
                        duration: 60,
                        calories: 300,
                        type: 'strength',
                        description: 'Focus on compound movements'
                    },
                    {
                        name: 'Resistance Training',
                        duration: 45,
                        calories: 200,
                        type: 'strength',
                        description: 'Build muscle mass'
                    }
                ];
                tips.push('Ensure adequate protein intake for muscle recovery');
            } else { // maintain
                recommendations = [
                    {
                        name: 'Mixed Workout',
                        duration: 45,
                        calories: 300,
                        type: 'mixed',
                        description: 'Balance of cardio and strength'
                    },
                    {
                        name: 'Active Recovery',
                        duration: 30,
                        calories: 150,
                        type: 'flexibility',
                        description: 'Gentle movement for recovery'
                    }
                ];
            }
            
            // Add general tips
            tips.push(`You've completed ${weeklyFrequency} workouts this week`);
            if (weeklyFrequency >= 5) {
                tips.push('Great consistency! Consider adding variety to your workouts');
            }
            
            res.json({
                userGoal: user.goal,
                weeklyFrequency,
                todayCalories,
                recommendations,
                tips
            });
        } catch (error) {
            console.error('Get recommendations error:', error);
            res.status(500).json({ error: 'Failed to get exercise recommendations' });
        }
    }
    
    // Get exercise history
    async getExerciseHistory(req, res) {
        try {
            const { userId } = req.params;
            const { startDate, endDate, exerciseType } = req.query;
            
            // Get all exercise logs for user
            let exerciseLogs = await db.find('exercises.json', { userId: parseInt(userId) });
            
            // Apply filters
            if (startDate) {
                const start = new Date(startDate);
                start.setHours(0, 0, 0, 0);
                exerciseLogs = exerciseLogs.filter(ex => new Date(ex.timestamp) >= start);
            }
            
            if (endDate) {
                const end = new Date(endDate);
                end.setHours(23, 59, 59, 999);
                exerciseLogs = exerciseLogs.filter(ex => new Date(ex.timestamp) <= end);
            }
            
            if (exerciseType) {
                exerciseLogs = exerciseLogs.filter(ex => ex.exerciseType === exerciseType);
            }
            
            // Sort by timestamp (newest first)
            exerciseLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            // Calculate totals
            const totals = {
                totalExercises: exerciseLogs.length,
                totalDuration: exerciseLogs.reduce((sum, ex) => sum + (ex.duration || 0), 0),
                totalCaloriesBurned: exerciseLogs.reduce((sum, ex) => sum + (ex.caloriesBurned || 0), 0),
                byType: {
                    cardio: exerciseLogs.filter(ex => ex.exerciseType === 'cardio').length,
                    strength: exerciseLogs.filter(ex => ex.exerciseType === 'strength').length,
                    flexibility: exerciseLogs.filter(ex => ex.exerciseType === 'flexibility').length
                }
            };
            
            res.json({
                count: exerciseLogs.length,
                totals,
                exerciseLogs
            });
        } catch (error) {
            console.error('Get exercise history error:', error);
            res.status(500).json({ error: 'Failed to get exercise history' });
        }
    }
    
    // Delete exercise
    async deleteExercise(req, res) {
        try {
            const { exerciseId } = req.params;
            
            // Find the exercise first to check ownership
            const exercise = await db.findOne('exercises.json', { id: parseInt(exerciseId) });
            
            if (!exercise) {
                return res.status(404).json({ error: 'Exercise not found' });
            }
            
            // For security, you might want to check if the user owns this exercise
            // const userId = req.user?.id; // Assuming you have authentication
            // if (exercise.userId !== userId) {
            //     return res.status(403).json({ error: 'Not authorized' });
            // }
            
            // Delete from database
            const success = await db.delete('exercises.json', parseInt(exerciseId));
            
            if (!success) {
                return res.status(500).json({ error: 'Failed to delete exercise' });
            }
            
            res.json({
                message: 'Exercise deleted successfully'
            });
        } catch (error) {
            console.error('Delete exercise error:', error);
            res.status(500).json({ error: 'Failed to delete exercise' });
        }
    }
    
    // Update exercise
    async updateExercise(req, res) {
        try {
            const { exerciseId } = req.params;
            const updates = req.body;
            
            // Find the exercise first
            const exercise = await db.findOne('exercises.json', { id: parseInt(exerciseId) });
            
            if (!exercise) {
                return res.status(404).json({ error: 'Exercise not found' });
            }
            
            // Update the exercise
            const updatedExercise = await db.update('exercises.json', parseInt(exerciseId), {
                ...updates,
                updatedAt: new Date().toISOString()
            });
            
            res.json({
                message: 'Exercise updated successfully',
                exercise: updatedExercise
            });
        } catch (error) {
            console.error('Update exercise error:', error);
            res.status(500).json({ error: 'Failed to update exercise' });
        }
    }
    
    // Generate exercise tips
    generateExerciseTips(goal, calorieBalance) {
        const tips = [];
        
        if (goal === 'lose') {
            if (calorieBalance > 300) {
                tips.push('You\'re consuming more calories than you burn. Focus on cardio exercises to create a deficit.');
                tips.push('Aim for 150-300 minutes of moderate cardio per week for weight loss.');
            } else if (calorieBalance < -300) {
                tips.push('You\'re in a significant deficit. Make sure to include strength training to preserve muscle mass.');
            } else {
                tips.push('Good balance! Continue with regular exercise and monitor your progress.');
            }
            tips.push('Combine cardio with strength training for optimal fat loss and muscle preservation.');
        } else if (goal === 'gain') {
            if (calorieBalance < 0) {
                tips.push('You need to consume more calories to support muscle growth. Increase your calorie intake.');
            }
            tips.push('Focus on progressive overload in your strength training.');
            tips.push('Allow 48 hours of rest between working the same muscle groups.');
        } else {
            tips.push('Maintain a balanced exercise routine including cardio, strength, and flexibility training.');
            tips.push('Aim for 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity weekly.');
        }
        
        tips.push('Stay hydrated during and after exercise.');
        tips.push('Listen to your body and rest when needed.');
        
        return tips;
    }
}

module.exports = new ExerciseController();