import pandas as pd
import numpy as np
import random
from datetime import datetime
import json
import os

class NutritionDatasetGenerator:
    def __init__(self):
        self.food_groups = [
            'cereals', 'fruits', 'vegetables', 'meat', 'fish',
            'dairy', 'legumes', 'fats_oils', 'processed'
        ]
        
        self.food_names = {
            'cereals': ['Whole Wheat Bread', 'Brown Rice', 'Oats', 'Quinoa', 'Corn Flakes', 
                       'Whole Grain Pasta', 'Barley', 'Millet', 'Bran Cereal', 'Rye Bread'],
            'fruits': ['Apple', 'Banana', 'Orange', 'Strawberries', 'Blueberries',
                      'Grapes', 'Mango', 'Pineapple', 'Watermelon', 'Kiwi'],
            'vegetables': ['Broccoli', 'Spinach', 'Carrots', 'Bell Peppers', 'Tomatoes',
                          'Cucumber', 'Kale', 'Lettuce', 'Sweet Potato', 'Cauliflower'],
            'meat': ['Chicken Breast', 'Beef Steak', 'Pork Chop', 'Turkey', 'Lamb',
                    'Duck', 'Bacon', 'Sausage', 'Ham', 'Veal'],
            'fish': ['Salmon', 'Tuna', 'Cod', 'Sardines', 'Mackerel',
                    'Trout', 'Shrimp', 'Crab', 'Lobster', 'Tilapia'],
            'dairy': ['Whole Milk', 'Greek Yogurt', 'Cheddar Cheese', 'Cottage Cheese',
                     'Butter', 'Cream', 'Mozzarella', 'Parmesan', 'Skim Milk', 'Yogurt'],
            'legumes': ['Black Beans', 'Lentils', 'Chickpeas', 'Kidney Beans', 'Peas',
                       'Soybeans', 'Pinto Beans', 'Navy Beans', 'Peanuts', 'Almonds'],
            'fats_oils': ['Olive Oil', 'Coconut Oil', 'Butter', 'Avocado Oil', 'Canola Oil',
                         'Sunflower Oil', 'Peanut Oil', 'Sesame Oil', 'Margarine', 'Lard'],
            'processed': ['Potato Chips', 'Chocolate Bar', 'Ice Cream', 'Pizza', 'Burger',
                         'Hot Dog', 'Cookies', 'Cake', 'Donut', 'French Fries']
        }
    
    def generate_food_item(self, food_group, food_name):
        """Generate realistic nutrition data for a food item"""
        
        # Base templates for different food groups
        if food_group == 'cereals':
            return {
                'serving_size_g': random.randint(30, 100),
                'energy_kcal': random.randint(100, 350),
                'carbohydrates_g': random.uniform(15, 75),
                'sugars_g': random.uniform(1, 20),
                'fiber_g': random.uniform(2, 10),
                'protein_g': random.uniform(2, 12),
                'total_fat_g': random.uniform(0.5, 5),
                'saturated_fat_g': random.uniform(0.1, 1.5),
                'unsaturated_fat_g': random.uniform(0.3, 3),
                'trans_fat_g': 0,
                'cholesterol_mg': random.randint(0, 5),
                'sodium_mg': random.randint(0, 300),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': random.randint(0, 10),
                'calcium_percent_DV': random.randint(0, 20),
                'iron_percent_DV': random.randint(2, 50),
                'potassium_mg': random.randint(50, 300)
            }
        
        elif food_group == 'fruits':
            return {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(50, 150),
                'carbohydrates_g': random.uniform(10, 40),
                'sugars_g': random.uniform(8, 30),
                'fiber_g': random.uniform(2, 8),
                'protein_g': random.uniform(0.5, 2),
                'total_fat_g': random.uniform(0.1, 1),
                'saturated_fat_g': random.uniform(0, 0.3),
                'unsaturated_fat_g': random.uniform(0.05, 0.7),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 5),
                'vitamin_A_percent_DV': random.randint(0, 25),
                'vitamin_C_percent_DV': random.randint(20, 150),
                'calcium_percent_DV': random.randint(0, 10),
                'iron_percent_DV': random.randint(0, 10),
                'potassium_mg': random.randint(200, 500)
            }
        
        elif food_group == 'vegetables':
            leafy = 'spinach' in food_name.lower() or 'kale' in food_name.lower() or 'lettuce' in food_name.lower()
            return {
                'serving_size_g': random.randint(80, 150),
                'energy_kcal': random.randint(20, 100) if not leafy else random.randint(10, 30),
                'carbohydrates_g': random.uniform(3, 20),
                'sugars_g': random.uniform(1, 10),
                'fiber_g': random.uniform(2, 8),
                'protein_g': random.uniform(1, 5),
                'total_fat_g': random.uniform(0.1, 1),
                'saturated_fat_g': random.uniform(0, 0.2),
                'unsaturated_fat_g': random.uniform(0.05, 0.5),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 50),
                'vitamin_A_percent_DV': random.randint(10, 200) if leafy else random.randint(0, 50),
                'vitamin_C_percent_DV': random.randint(20, 120) if leafy else random.randint(10, 80),
                'calcium_percent_DV': random.randint(2, 30) if leafy else random.randint(0, 15),
                'iron_percent_DV': random.randint(5, 25) if leafy else random.randint(0, 15),
                'potassium_mg': random.randint(200, 600) if leafy else random.randint(100, 400)
            }
        
        elif food_group == 'meat':
            return {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(150, 400),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': random.uniform(20, 35),
                'total_fat_g': random.uniform(5, 30),
                'saturated_fat_g': random.uniform(2, 12),
                'unsaturated_fat_g': random.uniform(2, 15),
                'trans_fat_g': random.uniform(0, 0.5),
                'cholesterol_mg': random.randint(50, 150),
                'sodium_mg': random.randint(50, 200),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': 0,
                'calcium_percent_DV': random.randint(0, 5),
                'iron_percent_DV': random.randint(10, 30),
                'potassium_mg': random.randint(300, 500)
            }
        
        elif food_group == 'fish':
            return {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(150, 350),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': random.uniform(18, 30),
                'total_fat_g': random.uniform(5, 20),
                'saturated_fat_g': random.uniform(1, 5),
                'unsaturated_fat_g': random.uniform(3, 15),
                'trans_fat_g': 0,
                'cholesterol_mg': random.randint(40, 100),
                'sodium_mg': random.randint(50, 150),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(0, 10),
                'iron_percent_DV': random.randint(5, 20),
                'potassium_mg': random.randint(300, 600)
            }
        
        elif food_group == 'dairy':
            return {
                'serving_size_g': random.randint(100, 250),
                'energy_kcal': random.randint(100, 300),
                'carbohydrates_g': random.uniform(3, 15),
                'sugars_g': random.uniform(2, 12),
                'fiber_g': 0,
                'protein_g': random.uniform(5, 25),
                'total_fat_g': random.uniform(2, 20),
                'saturated_fat_g': random.uniform(1, 12),
                'unsaturated_fat_g': random.uniform(0.5, 5),
                'trans_fat_g': random.uniform(0, 0.3),
                'cholesterol_mg': random.randint(10, 50),
                'sodium_mg': random.randint(50, 200),
                'vitamin_A_percent_DV': random.randint(5, 25),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(20, 50),
                'iron_percent_DV': random.randint(0, 5),
                'potassium_mg': random.randint(150, 400)
            }
        
        elif food_group == 'legumes':
            return {
                'serving_size_g': random.randint(100, 150),
                'energy_kcal': random.randint(100, 250),
                'carbohydrates_g': random.uniform(15, 40),
                'sugars_g': random.uniform(1, 8),
                'fiber_g': random.uniform(5, 15),
                'protein_g': random.uniform(7, 20),
                'total_fat_g': random.uniform(1, 10),
                'saturated_fat_g': random.uniform(0.1, 1.5),
                'unsaturated_fat_g': random.uniform(0.5, 8),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 50),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': random.randint(0, 15),
                'calcium_percent_DV': random.randint(2, 15),
                'iron_percent_DV': random.randint(10, 30),
                'potassium_mg': random.randint(300, 600)
            }
        
        elif food_group == 'fats_oils':
            return {
                'serving_size_g': random.randint(15, 30),
                'energy_kcal': random.randint(120, 250),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': 0,
                'total_fat_g': random.uniform(13, 28),
                'saturated_fat_g': random.uniform(2, 18),
                'unsaturated_fat_g': random.uniform(10, 25),
                'trans_fat_g': random.uniform(0, 0.3),
                'cholesterol_mg': random.randint(0, 30),
                'sodium_mg': random.randint(0, 100),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': 0,
                'calcium_percent_DV': random.randint(0, 2),
                'iron_percent_DV': random.randint(0, 5),
                'potassium_mg': random.randint(0, 50)
            }
        
        elif food_group == 'processed':
            return {
                'serving_size_g': random.randint(30, 150),
                'energy_kcal': random.randint(150, 500),
                'carbohydrates_g': random.uniform(15, 60),
                'sugars_g': random.uniform(5, 40),
                'fiber_g': random.uniform(0, 3),
                'protein_g': random.uniform(1, 10),
                'total_fat_g': random.uniform(5, 30),
                'saturated_fat_g': random.uniform(2, 15),
                'unsaturated_fat_g': random.uniform(2, 12),
                'trans_fat_g': random.uniform(0, 2),
                'cholesterol_mg': random.randint(0, 50),
                'sodium_mg': random.randint(200, 800),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(0, 15),
                'iron_percent_DV': random.randint(2, 20),
                'potassium_mg': random.randint(50, 300)
            }
    
    def generate_baseline_scores(self, food_group, food_name):
        """Generate baseline scores for food items"""
        
        # Determine storage type
        storage_map = {
            'cereals': 'dry',
            'fruits': 'refrigerated',
            'vegetables': 'refrigerated',
            'meat': 'frozen',
            'fish': 'frozen',
            'dairy': 'refrigerated',
            'legumes': 'dry',
            'fats_oils': 'ambient',
            'processed': 'ambient'
        }
        
        # Determine shelf life
        shelf_life_map = {
            'dry': random.randint(180, 365),
            'refrigerated': random.randint(7, 30),
            'frozen': random.randint(90, 365),
            'ambient': random.randint(30, 180)
        }
        
        storage = storage_map.get(food_group, 'ambient')
        
        # Generate scores based on food group
        if food_group in ['fruits', 'vegetables']:
            nutritional_score = random.randint(7, 10)
            safety_score = random.randint(8, 10)
            quality_score = random.randint(7, 10)
        elif food_group in ['fish', 'meat']:
            nutritional_score = random.randint(6, 9)
            safety_score = random.randint(6, 9)
            quality_score = random.randint(6, 9)
        elif food_group == 'processed':
            nutritional_score = random.randint(3, 6)
            safety_score = random.randint(7, 10)
            quality_score = random.randint(5, 8)
        elif food_group == 'fats_oils':
            nutritional_score = random.randint(4, 8)
            safety_score = random.randint(8, 10)
            quality_score = random.randint(6, 9)
        else:
            nutritional_score = random.randint(5, 9)
            safety_score = random.randint(7, 10)
            quality_score = random.randint(6, 9)
        
        return {
            'baseline_nutritional_score': nutritional_score,
            'baseline_safety_score': safety_score,
            'baseline_quality_score': quality_score,
            'storage_type': storage,
            'shelf_life_days': shelf_life_map[storage]
        }
    
    def generate_dataset(self, num_rows=200):
        """Generate the complete dataset"""
        data = []
        
        # Calculate how many items per group
        items_per_group = num_rows // len(self.food_groups)
        remainder = num_rows % len(self.food_groups)
        
        for group_idx, food_group in enumerate(self.food_groups):
            # Add extra items to first few groups if remainder
            extra = 1 if group_idx < remainder else 0
            total_items = items_per_group + extra
            
            for _ in range(total_items):
                # Select random food name from the group
                food_name = random.choice(self.food_names[food_group])
                
                # Generate nutrition data
                nutrition_data = self.generate_food_item(food_group, food_name)
                
                # Generate baseline scores
                baseline_data = self.generate_baseline_scores(food_group, food_name)
                
                # Combine all data
                row = {
                    'food_name': food_name,
                    'food_group': food_group,
                    **nutrition_data,
                    **baseline_data
                }
                
                data.append(row)
        
        # Shuffle the data
        random.shuffle(data)
        
        return pd.DataFrame(data)
    
    def save_to_csv(self, df, filename='nutrition_dataset.csv'):
        """Save dataset to CSV"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename} with {len(df)} rows")
        
        # Print sample
        print("\nSample of generated data:")
        print(df.head().to_string())
        
        # Print summary by food group
        print("\nSummary by food group:")
        for group in self.food_groups:
            group_data = df[df['food_group'] == group]
            print(f"\n{group.capitalize()}: {len(group_data)} items")
            print(f"  Avg calories: {group_data['energy_kcal'].mean():.1f}")
            print(f"  Avg protein: {group_data['protein_g'].mean():.1f}g")
            print(f"  Avg sodium: {group_data['sodium_mg'].mean():.1f}mg")

def main():
    generator = NutritionDatasetGenerator()
    
    # Generate dataset
    print("Generating nutrition dataset...")
    df = generator.generate_dataset(num_rows=200)
    
    # Save to CSV
    generator.save_to_csv(df, 'nutrition_dataset.csv')
    
    # Also save to JSON for Node.js backend
    df.to_json('nutrition_dataset.json', orient='records', indent=2)
    print("\nDataset also saved to nutrition_dataset.json")
    
    return df

if __name__ == "__main__":
    main()