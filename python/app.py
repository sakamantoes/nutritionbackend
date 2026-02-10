from flask import Flask, request, jsonify
from flask_cors import CORS
from nutrition_ml import NutritionMLModels
from notification_service import notification_service
import json
import os
import asyncio
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize ML models - but only when app starts, not on import
ml_models = None

def initialize_models():
    """Initialize ML models (called only once)"""
    global ml_models
    if ml_models is None:
        print("Initializing ML models...")
        ml_models = NutritionMLModels()
        ml_models.load_models()
        print("Models initialized successfully")

# Import existing endpoints from separate file to avoid duplicate code
# For now, I'll include them directly but organized

@app.route('/')
def home():
    return jsonify({
        "message": "Nutrition Tracking API",
        "endpoints": {
            "predict_food_group": "/api/predict/food-group (POST)",
            "predict_health_score": "/api/predict/health-score (POST)",
            "exercise_recommendation": "/api/exercise/recommend (POST)",
            "nutrition_analysis": "/api/nutrition/analyze (POST)",
            "notifications_register": "/api/notifications/register (POST)",
            "notifications_send": "/api/notifications/send (POST)",
            "notifications_history": "/api/notifications/history/<user_id> (GET)"
        }
    })

# Existing endpoints from previous app.py
@app.route('/api/predict/food-group', methods=['POST'])
def predict_food_group():
    """Predict food group from nutrition data"""
    try:
        initialize_models()  # Ensure models are initialized
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Predict food group
        food_group = ml_models.predict_food_group(data)
        
        return jsonify({
            "prediction": food_group,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict/health-score', methods=['POST'])
def predict_health_score():
    """Predict health score from nutrition data"""
    try:
        initialize_models()  # Ensure models are initialized
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Predict health score
        health_score = ml_models.predict_health_score(data)
        
        return jsonify({
            "health_score": health_score,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exercise/recommend', methods=['POST'])
def recommend_exercise():
    """Recommend exercises based on user profile and nutrition"""
    try:
        data = request.get_json()
        
        # Extract user data
        age = data.get('age', 30)
        weight = data.get('weight', 70)  # kg
        height = data.get('height', 170)  # cm
        calories_consumed = data.get('calories_consumed', 2000)
        goal = data.get('goal', 'maintain')  # lose, gain, maintain
        activity_level = data.get('activity_level', 'moderate')  # sedentary, light, moderate, active
        
        # Calculate BMR (Basal Metabolic Rate)
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        
        # Adjust for activity level
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        # Calculate calorie balance
        calorie_balance = calories_consumed - tdee
        
        # Generate exercise recommendations based on goal and balance
        exercises = []
        
        if goal == 'lose':
            if calorie_balance > 500:
                # High calorie surplus, need intense cardio
                exercises = [
                    {"name": "Running", "duration": 45, "type": "cardio", "calories_burned": 400},
                    {"name": "Cycling", "duration": 60, "type": "cardio", "calories_burned": 450},
                    {"name": "HIIT Workout", "duration": 30, "type": "cardio", "calories_burned": 350}
                ]
            elif calorie_balance > 0:
                exercises = [
                    {"name": "Jogging", "duration": 30, "type": "cardio", "calories_burned": 250},
                    {"name": "Swimming", "duration": 45, "type": "cardio", "calories_burned": 300},
                    {"name": "Strength Training", "duration": 45, "type": "strength", "calories_burned": 200}
                ]
            else:
                exercises = [
                    {"name": "Walking", "duration": 30, "type": "cardio", "calories_burned": 150},
                    {"name": "Yoga", "duration": 45, "type": "flexibility", "calories_burned": 100}
                ]
        
        elif goal == 'gain':
            if calorie_balance < -500:
                # Large deficit, need strength training with minimal cardio
                exercises = [
                    {"name": "Weight Lifting", "duration": 60, "type": "strength", "calories_burned": 200},
                    {"name": "Bodyweight Exercises", "duration": 45, "type": "strength", "calories_burned": 150},
                    {"name": "Resistance Training", "duration": 50, "type": "strength", "calories_burned": 180}
                ]
            else:
                exercises = [
                    {"name": "Strength Training", "duration": 45, "type": "strength", "calories_burned": 200},
                    {"name": "Light Cardio", "duration": 20, "type": "cardio", "calories_burned": 100},
                    {"name": "Flexibility Training", "duration": 30, "type": "flexibility", "calories_burned": 80}
                ]
        
        else:  # maintain
            exercises = [
                {"name": "Mixed Cardio", "duration": 30, "type": "cardio", "calories_burned": 200},
                {"name": "Strength Training", "duration": 40, "type": "strength", "calories_burned": 180},
                {"name": "Yoga/Pilates", "duration": 45, "type": "flexibility", "calories_burned": 120}
            ]
        
        # Add exercise tips
        tips = []
        if calorie_balance > 300:
            tips.append("You're consuming more calories than you burn. Consider increasing cardio exercises.")
        elif calorie_balance < -300:
            tips.append("You're in a calorie deficit. Make sure to get enough protein for muscle maintenance.")
        
        tips.append(f"Your estimated daily calorie needs: {tdee:.0f} calories")
        tips.append(f"Today's balance: {calorie_balance:.0f} calories")
        
        return jsonify({
            "exercises": exercises,
            "tips": tips,
            "calorie_balance": calorie_balance,
            "daily_needs": tdee,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nutrition/analyze', methods=['POST'])
def analyze_nutrition():
    """Analyze daily nutrition intake"""
    try:
        data = request.get_json()
        
        meals = data.get('meals', [])
        
        if not meals:
            return jsonify({"error": "No meal data provided"}), 400
        
        # Calculate totals
        totals = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0
        }
        
        food_groups = {}
        
        for meal in meals:
            for nutrient, value in meal.items():
                if nutrient in totals:
                    totals[nutrient] += value
            
            # Track food groups
            group = meal.get('food_group', 'unknown')
            food_groups[group] = food_groups.get(group, 0) + 1
        
        # Analyze nutritional balance
        analysis = {
            'total_calories': totals['calories'],
            'protein_percentage': (totals['protein'] * 4 / totals['calories'] * 100) if totals['calories'] > 0 else 0,
            'carb_percentage': (totals['carbs'] * 4 / totals['calories'] * 100) if totals['calories'] > 0 else 0,
            'fat_percentage': (totals['fat'] * 9 / totals['calories'] * 100) if totals['calories'] > 0 else 0,
            'fiber_adequate': totals['fiber'] >= 25,  # Recommended minimum
            'sugar_high': totals['sugar'] > 50,  # High if > 50g
            'sodium_high': totals['sodium'] > 2300,  # High if > 2300mg
            'food_group_diversity': len(food_groups),
            'recommended_calories': 2000  # Default, would be personalized in full app
        }
        
        # Generate recommendations
        recommendations = []
        
        if analysis['protein_percentage'] < 15:
            recommendations.append("Increase protein intake. Consider adding lean meats, legumes, or dairy.")
        
        if analysis['fat_percentage'] > 35:
            recommendations.append("Consider reducing fat intake, especially saturated fats.")
        
        if not analysis['fiber_adequate']:
            recommendations.append("Increase fiber intake with more fruits, vegetables, and whole grains.")
        
        if analysis['sugar_high']:
            recommendations.append("Reduce sugar intake. Limit processed foods and sweetened beverages.")
        
        if analysis['sodium_high']:
            recommendations.append("Reduce sodium intake. Limit processed and packaged foods.")
        
        if analysis['food_group_diversity'] < 3:
            recommendations.append("Try to include more food groups for balanced nutrition.")
        
        return jsonify({
            "analysis": analysis,
            "recommendations": recommendations,
            "totals": totals,
            "food_groups": food_groups,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/response', methods=['POST'])
def chatbot_response():
    """Rule-based chatbot response"""
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        
        # Rule-based responses
        responses = {
            'hello': "Hello! I'm your nutrition assistant. How can I help you today?",
            'hi': "Hi there! Ready to talk about your nutrition goals?",
            'calorie': "Calories are units of energy. The average adult needs 2000-2500 calories per day.",
            'protein': "Protein helps build and repair tissues. Aim for 0.8g per kg of body weight daily.",
            'carbohydrate': "Carbs are your body's main energy source. Choose complex carbs like whole grains.",
            'fat': "Healthy fats are essential. Focus on unsaturated fats from nuts, seeds, and oils.",
            'fiber': "Fiber aids digestion. Aim for 25-30g daily from fruits, vegetables, and whole grains.",
            'vitamin': "Vitamins are essential nutrients. Eat a variety of colorful fruits and vegetables.",
            'exercise': "Aim for 150 minutes of moderate exercise or 75 minutes of vigorous exercise weekly.",
            'weight loss': "For weight loss, create a calorie deficit through diet and exercise.",
            'healthy diet': "A healthy diet includes fruits, vegetables, lean proteins, and whole grains.",
            'meal plan': "Consider 3 balanced meals with snacks. Include protein, carbs, and healthy fats.",
            'water': "Drink at least 8 glasses (2 liters) of water daily.",
            'sugar': "Limit added sugars to less than 10% of daily calories.",
            'salt': "Limit sodium to less than 2300mg daily.",
            'breakfast': "A good breakfast includes protein, fiber, and healthy fats.",
            'lunch': "Lunch should be balanced with lean protein, vegetables, and whole grains.",
            'dinner': "Dinner should be lighter. Focus on vegetables and lean protein.",
            'snack': "Healthy snacks include fruits, nuts, yogurt, or vegetables with hummus.",
            'vegetarian': "Vegetarian diets can be healthy with proper planning for protein and nutrients.",
            'vegan': "Vegan diets require attention to B12, iron, calcium, and omega-3 sources.",
            'gluten': "Gluten-free diets are necessary for celiac disease. Otherwise, whole grains are healthy.",
            'dairy': "Dairy provides calcium and protein. Alternatives include fortified plant milks.",
            'fruit': "Fruits provide vitamins, fiber, and antioxidants. Aim for 2-3 servings daily.",
            'vegetable': "Vegetables are nutrient-dense. Aim for 3-5 servings daily.",
            'meat': "Choose lean meats. Limit red and processed meats for better health.",
            'fish': "Fatty fish like salmon provide omega-3 fatty acids. Aim for 2 servings weekly.",
            'egg': "Eggs are excellent protein sources with vitamins and minerals.",
            'nut': "Nuts provide healthy fats, protein, and fiber. A handful makes a good snack.",
            'seed': "Seeds like chia and flax provide fiber, protein, and healthy fats.",
            'oil': "Use healthy oils like olive or avocado oil. Limit saturated and trans fats.",
            'processed food': "Limit processed foods which are often high in salt, sugar, and unhealthy fats.",
            'organic': "Organic foods may reduce pesticide exposure but all fruits and vegetables are healthy.",
            'supplement': "Supplements can help fill gaps but whole foods should be your primary source.",
            'sleep': "Aim for 7-9 hours of sleep. Poor sleep affects hunger hormones and metabolism.",
            'stress': "Chronic stress affects digestion and food choices. Practice stress management.",
            'metabolism': "Metabolism is affected by age, muscle mass, activity level, and genetics.",
            'detox': "Your body naturally detoxifies. Focus on a healthy diet rather than detox products.",
            'juice': "Whole fruits are better than juice which lacks fiber and concentrates sugar.",
            'coffee': "Moderate coffee (3-4 cups) is generally safe and provides antioxidants.",
            'tea': "Tea provides antioxidants. Green tea may boost metabolism slightly.",
            'alcohol': "Limit alcohol to 1 drink daily for women, 2 for men.",
            'soda': "Soda provides empty calories. Choose water or unsweetened beverages.",
            'smoothie': "Smoothies can be healthy. Include vegetables, protein, and limit added sugars.",
            'salad': "Salads are great. Add protein and healthy fats for a balanced meal.",
            'soup': "Homemade soups with vegetables and lean protein make nutritious meals.",
            'sandwich': "Use whole grain bread, lean protein, and plenty of vegetables.",
            'pizza': "Make pizza healthier with whole grain crust, vegetable toppings, and moderate cheese.",
            'pasta': "Choose whole grain pasta and add vegetables and lean protein.",
            'rice': "Brown rice has more fiber than white rice.",
            'bread': "Whole grain bread provides more fiber and nutrients than white bread.",
            'cheese': "Cheese provides calcium and protein but is high in saturated fat. Enjoy in moderation.",
            'yogurt': "Greek yogurt is high in protein. Choose plain to avoid added sugars.",
            'milk': "Milk provides calcium and protein. Choose low-fat if watching calories.",
            'butter': "Butter is high in saturated fat. Use sparingly or choose healthier oils.",
            'avocado': "Avocados provide healthy fats, fiber, and various nutrients.",
            'banana': "Bananas provide potassium, vitamin B6, and fiber.",
            'apple': "Apples provide fiber and antioxidants. Eat with skin for maximum benefits.",
            'orange': "Oranges provide vitamin C, fiber, and various antioxidants.",
            'berry': "Berries are high in antioxidants and fiber with relatively low sugar.",
            'broccoli': "Broccoli is nutrient-dense with vitamins C, K, fiber, and various compounds.",
            'spinach': "Spinach is rich in iron, vitamins A, C, K, and various minerals.",
            'carrot': "Carrots are excellent sources of vitamin A (as beta-carotene) and fiber.",
            'tomato': "Tomatoes provide vitamin C, potassium, and the antioxidant lycopene.",
            'potato': "Potatoes provide potassium and vitamin C. Eat with skin for fiber.",
            'sweet potato': "Sweet potatoes are rich in vitamin A (as beta-carotene) and fiber.",
            'onion': "Onions provide antioxidants and anti-inflammatory compounds.",
            'garlic': "Garlic has various health benefits including immune support.",
            'ginger': "Ginger can aid digestion and has anti-inflammatory properties.",
            'turmeric': "Turmeric contains curcumin which has anti-inflammatory properties.",
            'cinnamon': "Cinnamon may help regulate blood sugar.",
            'pepper': "Black pepper enhances nutrient absorption and has antioxidant properties.",
            'honey': "Honey has antioxidants but is still sugar. Use sparingly.",
            'maple syrup': "Maple syrup has some minerals but is still sugar. Use sparingly.",
            'chocolate': "Dark chocolate (70%+) has antioxidants but also calories and caffeine.",
            'ice cream': "Ice cream is high in sugar and saturated fat. Enjoy occasionally.",
            'cookie': "Cookies are typically high in sugar and refined carbs. Enjoy occasionally.",
            'cake': "Cake is typically high in sugar and refined carbs. Enjoy occasionally.",
            'chip': "Chips are often high in salt and unhealthy fats. Choose baked options occasionally.",
            'candy': "Candy provides empty calories with little nutrition. Enjoy very occasionally.",
            'thank': "You're welcome! Is there anything else I can help you with?",
            'bye': "Goodbye! Remember to eat a balanced diet and stay hydrated!",
            'goodbye': "Take care! Come back anytime for nutrition advice.",
            'help': "I can help with nutrition advice, meal planning, exercise recommendations, and analyzing your diet."
        }
        
        # Find matching response
        response = "I'm here to help with nutrition questions. Could you be more specific?"
        
        for keyword, reply in responses.items():
            if keyword in message:
                response = reply
                break
        
        return jsonify({
            "response": response,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW: Notification Endpoints
@app.route('/api/notifications/register', methods=['POST'])
def register_notifications():
    """Register a user for push notifications"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        push_token = data.get('push_token')
        preferences = data.get('preferences')
        
        if not user_id or not push_token:
            return jsonify({"error": "user_id and push_token are required"}), 400
        
        # Register user with notification service
        notification_service.register_user(user_id, push_token, preferences)
        
        return jsonify({
            "message": "User registered for notifications",
            "user_id": user_id,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/unregister', methods=['POST'])
def unregister_notifications():
    """Unregister a user from push notifications"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        notification_service.unregister_user(user_id)
        
        return jsonify({
            "message": "User unregistered from notifications",
            "user_id": user_id,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/update-preferences', methods=['POST'])
def update_notification_preferences():
    """Update user notification preferences"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        preferences = data.get('preferences')
        
        if not user_id or not preferences:
            return jsonify({"error": "user_id and preferences are required"}), 400
        
        notification_service.update_user_preferences(user_id, preferences)
        
        return jsonify({
            "message": "Notification preferences updated",
            "user_id": user_id,
            "preferences": preferences,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send an immediate notification to a user"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        notification_type = data.get('type')
        notification_data = data.get('data', {})
        
        if not user_id or not notification_type:
            return jsonify({"error": "user_id and type are required"}), 400
        
        success = notification_service.send_notification(
            user_id, 
            notification_type, 
            notification_data
        )
        
        if success:
            return jsonify({
                "message": "Notification sent",
                "user_id": user_id,
                "type": notification_type,
                "status": "success"
            })
        else:
            return jsonify({
                "message": "Failed to send notification",
                "status": "failed"
            }), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/send-calorie-update', methods=['POST'])
def send_calorie_update():
    """Send calorie goal update notification"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        calories_consumed = data.get('calories_consumed')
        calorie_goal = data.get('calorie_goal')
        
        if not all([user_id, calories_consumed, calorie_goal]):
            return jsonify({"error": "user_id, calories_consumed, and calorie_goal are required"}), 400
        
        notification_service.send_calorie_update(
            user_id,
            float(calories_consumed),
            float(calorie_goal)
        )
        
        return jsonify({
            "message": "Calorie update notification sent",
            "user_id": user_id,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/send-achievement', methods=['POST'])
def send_achievement():
    """Send achievement notification"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        achievement = data.get('achievement')
        
        if not user_id or not achievement:
            return jsonify({"error": "user_id and achievement are required"}), 400
        
        notification_service.send_achievement(user_id, achievement)
        
        return jsonify({
            "message": "Achievement notification sent",
            "user_id": user_id,
            "achievement": achievement,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/send-food-suggestion', methods=['POST'])
def send_food_suggestion():
    """Send food suggestion notification"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        food_name = data.get('food_name')
        reason = data.get('reason')
        
        if not user_id or not food_name:
            return jsonify({"error": "user_id and food_name are required"}), 400
        
        notification_service.send_food_suggestion(user_id, food_name, reason)
        
        return jsonify({
            "message": "Food suggestion notification sent",
            "user_id": user_id,
            "food_name": food_name,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/history/<user_id>', methods=['GET'])
def get_notification_history(user_id):
    """Get notification history for a user"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        
        history = notification_service.get_notification_history(user_id, limit)
        
        return jsonify({
            "user_id": user_id,
            "history": history,
            "count": len(history),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/stats/<user_id>', methods=['GET'])
def get_notification_stats(user_id):
    """Get notification statistics for a user"""
    try:
        stats = notification_service.get_user_stats(user_id)
        
        return jsonify({
            "user_id": user_id,
            "stats": stats,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/process-queue', methods=['POST'])
def process_notification_queue():
    """Process the notification queue (for testing)"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(notification_service.process_queue())
        
        return jsonify({
            "message": "Notification queue processed",
            "queue_size": len(notification_service.notification_queue),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Initialize models when app starts (only once)
    initialize_models()
    
    # Start Flask app with debug=False to prevent double execution
    print("Starting Nutrition Tracking API...")
    print("Available endpoints:")
    print("  GET  / - API information")
    print("  POST /api/predict/food-group - Predict food group")
    print("  POST /api/predict/health-score - Predict health score")
    print("  POST /api/exercise/recommend - Get exercise recommendations")
    print("  POST /api/nutrition/analyze - Analyze nutrition data")
    print("  POST /api/chatbot/response - Chat with nutrition assistant")
    print("\nNotification Endpoints:")
    print("  POST /api/notifications/register - Register for notifications")
    print("  POST /api/notifications/send - Send notification")
    print("  GET  /api/notifications/history/<user_id> - Get notification history")
    
    # Run with debug=False to prevent the reloader from running twice
    app.run(debug=False, port=5000)