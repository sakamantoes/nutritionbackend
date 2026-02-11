const express = require('express');
const router = express.Router();
const fs = require('fs').promises;
const path = require('path');

// Get nutrition analysis
router.post('/analyze', async (req, res) => {
  try {
    const { userId, timeRange } = req.body;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Load user data
    const usersPath = path.join(__dirname, '..', 'data', 'users.json');
    const foodsPath = path.join(__dirname, '..', 'data', 'user_foods.json');
    
    const usersData = await fs.readFile(usersPath, 'utf8');
    const foodsData = await fs.readFile(foodsPath, 'utf8');
    
    const users = JSON.parse(usersData);
    const foods = JSON.parse(foodsData);
    
    const user = users.find(u => u.id === parseInt(userId));
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Filter foods by user and time range
    const userFoods = foods.filter(food => food.userId === parseInt(userId));
    
    // Calculate date range
    const now = new Date();
    let startDate = new Date(now);
    
    switch (timeRange) {
      case 'day':
        startDate.setDate(now.getDate() - 1);
        break;
      case 'week':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'year':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        startDate.setDate(now.getDate() - 7);
    }
    
    // Filter foods by date
    const filteredFoods = userFoods.filter(food => {
      const foodDate = new Date(food.timestamp);
      return foodDate >= startDate;
    });
    
    // Calculate totals
    const totals = {
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: 0,
      sugar: 0,
      sodium: 0,
      count: filteredFoods.length
    };
    
    const foodGroups = {};
    
    filteredFoods.forEach(food => {
      totals.calories += food.calories || 0;
      totals.protein += food.protein || 0;
      totals.carbs += food.carbs || 0;
      totals.fat += food.fat || 0;
      totals.fiber += food.fiber || 0;
      totals.sugar += food.sugar || 0;
      totals.sodium += food.sodium || 0;
      
      const group = food.foodGroup || 'unknown';
      foodGroups[group] = (foodGroups[group] || 0) + 1;
    });
    
    // Calculate averages per day
    const daysInRange = Math.max(1, Math.ceil((now - startDate) / (1000 * 60 * 60 * 24)));
    const dailyAverages = {
      calories: totals.calories / daysInRange,
      protein: totals.protein / daysInRange,
      carbs: totals.carbs / daysInRange,
      fat: totals.fat / daysInRange,
      fiber: totals.fiber / daysInRange
    };
    
    // Calculate percentages
    const percentages = {
      protein: totals.calories > 0 ? (totals.protein * 4 / totals.calories * 100) : 0,
      carbs: totals.calories > 0 ? (totals.carbs * 4 / totals.calories * 100) : 0,
      fat: totals.calories > 0 ? (totals.fat * 9 / totals.calories * 100) : 0
    };
    
    // Generate health score (1-10)
    let healthScore = 5.0; // Base score
    
    // Adjust based on macronutrient balance
    const idealProtein = 15, idealCarbs = 55, idealFat = 30;
    const proteinDiff = Math.abs(percentages.protein - idealProtein);
    const carbsDiff = Math.abs(percentages.carbs - idealCarbs);
    const fatDiff = Math.abs(percentages.fat - idealFat);
    
    const macronutrientScore = 10 - (proteinDiff + carbsDiff + fatDiff) / 10;
    healthScore += (macronutrientScore - 5) * 0.5;
    
    // Adjust based on food diversity
    const diversityScore = Math.min(Object.keys(foodGroups).length / 5, 2);
    healthScore += diversityScore;
    
    // Adjust based on processed foods
    const processedCount = foodGroups.processed || 0;
    const processedPenalty = Math.min(processedCount / filteredFoods.length * 5, 2);
    healthScore -= processedPenalty;
    
    // Ensure score is between 1 and 10
    healthScore = Math.max(1, Math.min(10, Math.round(healthScore * 10) / 10));
    
    // Generate recommendations
    const recommendations = [];
    const strengths = [];
    const weaknesses = [];
    
    if (percentages.protein >= 15 && percentages.protein <= 30) {
      strengths.push('Good protein intake');
    } else if (percentages.protein < 15) {
      weaknesses.push('Insufficient protein');
      recommendations.push('Increase protein intake with lean meats, legumes, or dairy');
    }
    
    if (dailyAverages.fiber >= 25) {
      strengths.push('Adequate fiber consumption');
    } else {
      weaknesses.push('Low fiber intake');
      recommendations.push('Add more fruits, vegetables, and whole grains for fiber');
    }
    
    if (totals.sodium / daysInRange > 2300) {
      weaknesses.push('High sodium intake');
      recommendations.push('Reduce processed foods and added salt');
    }
    
    if (Object.keys(foodGroups).length >= 5) {
      strengths.push('Good food variety');
    } else {
      weaknesses.push('Limited food diversity');
      recommendations.push('Try to include more food groups in your diet');
    }
    
    // Nutrient breakdown
    const nutrientBreakdown = {
      protein: {
        current: Math.round(dailyAverages.protein),
        goal: Math.round(user.weight * 0.8), // 0.8g per kg body weight
        unit: 'g'
      },
      carbs: {
        current: Math.round(dailyAverages.carbs),
        goal: 275, // Standard goal
        unit: 'g'
      },
      fat: {
        current: Math.round(dailyAverages.fat),
        goal: 65, // Standard goal
        unit: 'g'
      },
      fiber: {
        current: Math.round(dailyAverages.fiber),
        goal: 25, // Standard goal
        unit: 'g'
      },
      sugar: {
        current: Math.round(totals.sugar / daysInRange),
        goal: 50, // Standard goal
        unit: 'g'
      },
      sodium: {
        current: Math.round(totals.sodium / daysInRange),
        goal: 2300, // Standard goal
        unit: 'mg'
      }
    };
    
    // Food group distribution
    const totalFoods = filteredFoods.length;
    const foodGroupDistribution = {};
    Object.entries(foodGroups).forEach(([group, count]) => {
      foodGroupDistribution[group] = Math.round((count / totalFoods) * 100);
    });
    
    // Analysis metrics
    const calorieGoal = user.daily_calorie_goal || 2000;
    const calorieBalance = Math.round(dailyAverages.calories - calorieGoal);
    
    const analysis = {
      overallScore: healthScore,
      strengths: strengths.length > 0 ? strengths : ['Consistent eating habits'],
      weaknesses: weaknesses.length > 0 ? weaknesses : ['No major issues detected'],
      recommendations: recommendations.length > 0 ? recommendations : ['Maintain current healthy habits'],
      nutrientBreakdown: nutrientBreakdown,
      foodGroupDistribution: foodGroupDistribution,
      analysis: {
        calorieBalance: calorieBalance,
        macronutrientBalance: macronutrientScore >= 7 ? 'good' : macronutrientScore >= 5 ? 'fair' : 'needs_improvement',
        micronutrientScore: Math.round(healthScore),
        processedFoodPercentage: foodGroupDistribution.processed || 0,
        hydrationScore: 7.5, // Placeholder - you can add water tracking
        daysAnalyzed: daysInRange,
        totalMeals: filteredFoods.length,
        averageCaloriesPerMeal: Math.round(totals.calories / filteredFoods.length)
      }
    };
    
    res.json({
      ...analysis,
      user: {
        id: user.id,
        name: user.name,
        goal: user.goal,
        daily_calorie_goal: calorieGoal
      },
      timeRange: timeRange,
      status: 'success'
    });
    
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ error: 'Failed to analyze nutrition data' });
  }
});

// Get food insights
router.post('/insights', async (req, res) => {
  try {
    const { userId, goal, timeRange } = req.body;
    
    // Load user data
    const usersPath = path.join(__dirname, '..', 'data', 'users.json');
    const usersData = await fs.readFile(usersPath, 'utf8');
    const users = JSON.parse(usersData);
    
    const user = users.find(u => u.id === parseInt(userId));
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Generate insights based on goal
    let insights;
    const actualGoal = goal || user.goal || 'maintain';
    
    if (actualGoal === 'lose') {
      insights = {
        calorie_deficit_needed: 500,
        protein_target_multiplier: 1.2,
        carb_target_multiplier: 0.8,
        recommended_foods: [
          "Leafy greens", "Lean proteins", "Whole grains", "Berries",
          "Greek yogurt", "Eggs", "Chicken breast", "Broccoli"
        ],
        foods_to_limit: [
          "Processed foods", "Sugary drinks", "Refined carbs",
          "Fried foods", "High-sugar snacks"
        ],
        exercise_recommendations: {
          cardio_minutes: 150,
          strength_sessions: 3,
          intensity: "moderate_to_high",
          focus: "Fat burning and calorie deficit"
        },
        meal_timing: {
          breakfast: "Within 1 hour of waking",
          lunch: "Balanced with protein and veggies",
          dinner: "Light, at least 3 hours before bed"
        }
      };
    } else if (actualGoal === 'gain') {
      insights = {
        calorie_surplus_needed: 300,
        protein_target_multiplier: 1.6,
        carb_target_multiplier: 1.2,
        recommended_foods: [
          "Lean meats", "Dairy", "Nuts", "Complex carbs",
          "Salmon", "Sweet potatoes", "Quinoa", "Avocado"
        ],
        foods_to_limit: [],
        exercise_recommendations: {
          cardio_minutes: 75,
          strength_sessions: 4,
          intensity: "high",
          focus: "Muscle building and strength"
        },
        meal_timing: {
          breakfast: "High in protein and carbs",
          pre_workout: "Carbs for energy",
          post_workout: "Protein for recovery"
        }
      };
    } else { // maintain
      insights = {
        calorie_deficit_needed: 0,
        protein_target_multiplier: 1.0,
        carb_target_multiplier: 1.0,
        recommended_foods: [
          "Balanced meals", "Variety of vegetables", "Healthy fats",
          "Whole grains", "Lean proteins", "Colorful fruits"
        ],
        foods_to_limit: [
          "Excessive sugar", "Trans fats", "Highly processed foods"
        ],
        exercise_recommendations: {
          cardio_minutes: 120,
          strength_sessions: 2,
          intensity: "moderate",
          focus: "Overall health and maintenance"
        },
        meal_timing: {
          breakfast: "Balanced start",
          lunch: "Main meal of the day",
          dinner: "Light and early"
        }
      };
    }
    
    // Add time-specific insights
    switch (timeRange) {
      case 'day':
        insights.focus = "Daily consistency";
        insights.tip = "Track every meal and stay hydrated throughout the day";
        insights.daily_goal = "Meet your calorie target with balanced meals";
        break;
      case 'week':
        insights.focus = "Weekly patterns";
        insights.tip = "Look for patterns in your eating habits and adjust accordingly";
        insights.weekly_goal = "Maintain consistency across all days";
        break;
      case 'month':
        insights.focus = "Monthly progress";
        insights.tip = "Review your progress and adjust goals based on results";
        insights.monthly_goal = "See measurable changes in your health metrics";
        break;
      default:
        insights.focus = "Long-term habits";
        insights.tip = "Focus on sustainable changes that you can maintain";
        insights.long_term_goal = "Develop lifelong healthy eating habits";
    }
    
    // Add user-specific metrics
    insights.user_metrics = {
      age: user.age,
      weight: user.weight,
      height: user.height,
      activity_level: user.activity_level,
      calculated_tdee: user.daily_calorie_goal || 2000
    };
    
    // Add actionable steps
    insights.actionable_steps = [
      `Aim for ${insights.calorie_deficit_needed > 0 ? 'a deficit of' : insights.calorie_surplus_needed > 0 ? 'a surplus of' : 'maintenance at'} ${Math.abs(insights.calorie_deficit_needed || insights.calorie_surplus_needed || 0)} calories`,
      `Include protein in every meal`,
      `Drink at least 8 glasses of water daily`,
      `Get ${insights.exercise_recommendations.cardio_minutes} minutes of cardio weekly`,
      `Practice ${insights.exercise_recommendations.strength_sessions} strength sessions weekly`
    ];
    
    res.json({
      insights: insights,
      user_id: userId,
      goal: actualGoal,
      time_range: timeRange,
      generated_at: new Date().toISOString(),
      status: "success"
    });
    
  } catch (error) {
    console.error('Insights error:', error);
    res.status(500).json({ error: 'Failed to generate insights' });
  }
});

// Get trends over time
router.get('/trends/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { period = '30' } = req.query;
    
    const foodsPath = path.join(__dirname, '..', 'data', 'user_foods.json');
    const foodsData = await fs.readFile(foodsPath, 'utf8');
    const foods = JSON.parse(foodsData);
    
    // Filter by user
    const userFoods = foods.filter(food => food.userId === parseInt(userId));
    
    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - parseInt(period));
    
    // Group by date
    const dailyData = {};
    
    userFoods.forEach(food => {
      const foodDate = new Date(food.timestamp);
      if (foodDate >= startDate) {
        const dateKey = foodDate.toISOString().split('T')[0];
        
        if (!dailyData[dateKey]) {
          dailyData[dateKey] = {
            calories: 0,
            protein: 0,
            carbs: 0,
            fat: 0,
            meals: 0
          };
        }
        
        dailyData[dateKey].calories += food.calories || 0;
        dailyData[dateKey].protein += food.protein || 0;
        dailyData[dateKey].carbs += food.carbs || 0;
        dailyData[dateKey].fat += food.fat || 0;
        dailyData[dateKey].meals += 1;
      }
    });
    
    // Convert to array and sort by date
    const trendData = Object.entries(dailyData)
      .map(([date, data]) => ({
        date,
        ...data
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Calculate moving averages (7-day)
    const movingAverages = [];
    const windowSize = 7;
    
    for (let i = windowSize - 1; i < trendData.length; i++) {
      const window = trendData.slice(i - windowSize + 1, i + 1);
      const avg = {
        date: trendData[i].date,
        calories: window.reduce((sum, day) => sum + day.calories, 0) / windowSize,
        protein: window.reduce((sum, day) => sum + day.protein, 0) / windowSize,
        carbs: window.reduce((sum, day) => sum + day.carbs, 0) / windowSize,
        fat: window.reduce((sum, day) => sum + day.fat, 0) / windowSize
      };
      movingAverages.push(avg);
    }
    
    // Calculate weekly totals
    const weeklyData = [];
    let currentWeek = null;
    let weekTotal = null;
    
    trendData.forEach(day => {
      const date = new Date(day.date);
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay());
      const weekKey = weekStart.toISOString().split('T')[0];
      
      if (currentWeek !== weekKey) {
        if (weekTotal) {
          weeklyData.push(weekTotal);
        }
        currentWeek = weekKey;
        weekTotal = {
          week_start: weekKey,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          days: 0
        };
      }
      
      weekTotal.calories += day.calories;
      weekTotal.protein += day.protein;
      weekTotal.carbs += day.carbs;
      weekTotal.fat += day.fat;
      weekTotal.days += 1;
    });
    
    if (weekTotal) {
      weeklyData.push(weekTotal);
    }
    
    res.json({
      userId: parseInt(userId),
      period: `${period} days`,
      daily_data: trendData,
      moving_averages: movingAverages,
      weekly_data: weeklyData,
      summary: {
        total_days: trendData.length,
        avg_daily_calories: trendData.length > 0 ? 
          trendData.reduce((sum, day) => sum + day.calories, 0) / trendData.length : 0,
        avg_daily_protein: trendData.length > 0 ? 
          trendData.reduce((sum, day) => sum + day.protein, 0) / trendData.length : 0,
        avg_daily_meals: trendData.length > 0 ? 
          trendData.reduce((sum, day) => sum + day.meals, 0) / trendData.length : 0
      },
      status: 'success'
    });
    
  } catch (error) {
    console.error('Trends error:', error);
    res.status(500).json({ error: 'Failed to fetch trends' });
  }
});

module.exports = router;