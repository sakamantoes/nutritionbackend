# This file defines data models for the nutrition tracking system

class User:
    def __init__(self, user_id, name, email, age, weight, height, goal, activity_level):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.weight = weight  # kg
        self.height = height  # cm
        self.goal = goal  # lose, gain, maintain
        self.activity_level = activity_level  # sedentary, light, moderate, active, very_active
        self.daily_calorie_goal = self.calculate_calorie_goal()
    
    def calculate_calorie_goal(self):
        """Calculate daily calorie goal based on user profile"""
        # BMR calculation using Mifflin-St Jeor Equation
        bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(self.activity_level, 1.55)
        
        # Adjust based on goal
        if self.goal == 'lose':
            return tdee - 500  # 500 calorie deficit for weight loss
        elif self.goal == 'gain':
            return tdee + 500  # 500 calorie surplus for weight gain
        else:  # maintain
            return tdee
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'goal': self.goal,
            'activity_level': self.activity_level,
            'daily_calorie_goal': self.daily_calorie_goal
        }

class FoodItem:
    def __init__(self, food_id, name, food_group, serving_size_g, nutrition_data):
        self.food_id = food_id
        self.name = name
        self.food_group = food_group
        self.serving_size_g = serving_size_g
        self.nutrition_data = nutrition_data  # Dictionary with all nutrition values
    
    def to_dict(self):
        return {
            'food_id': self.food_id,
            'name': self.name,
            'food_group': self.food_group,
            'serving_size_g': self.serving_size_g,
            **self.nutrition_data
        }

class Meal:
    def __init__(self, meal_id, user_id, timestamp, food_items, meal_type):
        self.meal_id = meal_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.food_items = food_items  # List of FoodItem objects
        self.meal_type = meal_type  # breakfast, lunch, dinner, snack
        self.total_nutrition = self.calculate_total_nutrition()
    
    def calculate_total_nutrition(self):
        """Calculate total nutrition for the meal"""
        totals = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0
        }
        
        for food_item in self.food_items:
            nutrition = food_item.nutrition_data
            totals['calories'] += nutrition.get('energy_kcal', 0)
            totals['protein'] += nutrition.get('protein_g', 0)
            totals['carbs'] += nutrition.get('carbohydrates_g', 0)
            totals['fat'] += nutrition.get('total_fat_g', 0)
            totals['fiber'] += nutrition.get('fiber_g', 0)
            totals['sugar'] += nutrition.get('sugars_g', 0)
            totals['sodium'] += nutrition.get('sodium_mg', 0)
        
        return totals
    
    def to_dict(self):
        return {
            'meal_id': self.meal_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'meal_type': self.meal_type,
            'food_items': [item.to_dict() for item in self.food_items],
            'total_nutrition': self.total_nutrition
        }

class Exercise:
    def __init__(self, exercise_id, name, duration_min, calories_burned, exercise_type):
        self.exercise_id = exercise_id
        self.name = name
        self.duration_min = duration_min
        self.calories_burned = calories_burned
        self.exercise_type = exercise_type  # cardio, strength, flexibility
    
    def to_dict(self):
        return {
            'exercise_id': self.exercise_id,
            'name': self.name,
            'duration_min': self.duration_min,
            'calories_burned': self.calories_burned,
            'exercise_type': self.exercise_type
        }