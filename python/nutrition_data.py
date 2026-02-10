import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Tuple

class NutritionDataManager:
    """
    Manages nutrition data, including dataset generation, food database,
    and nutrition analysis functions.
    """
    
    def __init__(self):
        self.dataset_path = 'nutrition_dataset.csv'
        self.foods_db_path = 'foods_database.json'
        self.food_categories = {
            'cereals': ['Grains and Cereal Products'],
            'fruits': ['Fresh Fruits', 'Dried Fruits'],
            'vegetables': ['Leafy Greens', 'Root Vegetables', 'Cruciferous Vegetables'],
            'meat': ['Red Meat', 'Poultry', 'Processed Meat'],
            'fish': ['Fatty Fish', 'White Fish', 'Shellfish'],
            'dairy': ['Milk', 'Cheese', 'Yogurt', 'Butter'],
            'legumes': ['Beans', 'Lentils', 'Peas', 'Nuts'],
            'fats_oils': ['Oils', 'Fats', 'Spreads'],
            'processed': ['Snacks', 'Sweets', 'Fast Food', 'Frozen Meals']
        }
        
        # Nutrient daily values (for adults)
        self.daily_values = {
            'calories': 2000,
            'protein_g': 50,          # 50g protein
            'carbs_g': 275,           # 275g carbs
            'fiber_g': 25,            # 25g fiber
            'sugars_g': 50,           # 50g added sugars max
            'total_fat_g': 65,        # 65g total fat
            'saturated_fat_g': 20,    # 20g saturated fat
            'trans_fat_g': 2,         # 2g trans fat max
            'cholesterol_mg': 300,    # 300mg cholesterol
            'sodium_mg': 2300,        # 2300mg sodium
            'vitamin_A_iu': 5000,     # 5000 IU
            'vitamin_C_mg': 90,       # 90mg
            'calcium_mg': 1000,       # 1000mg
            'iron_mg': 18,            # 18mg
            'potassium_mg': 3500      # 3500mg
        }
        
        # Common food items with base nutrition
        self.common_foods = {
            'Apple': {'group': 'fruits', 'calories': 95, 'carbs': 25, 'protein': 0.5, 'fat': 0.3},
            'Banana': {'group': 'fruits', 'calories': 105, 'carbs': 27, 'protein': 1.3, 'fat': 0.4},
            'Orange': {'group': 'fruits', 'calories': 62, 'carbs': 15, 'protein': 1.2, 'fat': 0.2},
            'Broccoli': {'group': 'vegetables', 'calories': 55, 'carbs': 11, 'protein': 3.7, 'fat': 0.6},
            'Spinach': {'group': 'vegetables', 'calories': 23, 'carbs': 3.6, 'protein': 2.9, 'fat': 0.4},
            'Carrots': {'group': 'vegetables', 'calories': 41, 'carbs': 10, 'protein': 0.9, 'fat': 0.2},
            'Chicken Breast': {'group': 'meat', 'calories': 165, 'carbs': 0, 'protein': 31, 'fat': 3.6},
            'Salmon': {'group': 'fish', 'calories': 206, 'carbs': 0, 'protein': 22, 'fat': 13},
            'Brown Rice': {'group': 'cereals', 'calories': 112, 'carbs': 23, 'protein': 2.6, 'fat': 0.9},
            'Whole Wheat Bread': {'group': 'cereals', 'calories': 79, 'carbs': 13, 'protein': 3.1, 'fat': 1.1},
            'Eggs': {'group': 'dairy', 'calories': 78, 'carbs': 0.6, 'protein': 6, 'fat': 5},
            'Greek Yogurt': {'group': 'dairy', 'calories': 59, 'carbs': 3.6, 'protein': 10, 'fat': 0.4},
            'Black Beans': {'group': 'legumes', 'calories': 114, 'carbs': 20, 'protein': 7.6, 'fat': 0.5},
            'Almonds': {'group': 'legumes', 'calories': 164, 'carbs': 6, 'protein': 6, 'fat': 14},
            'Olive Oil': {'group': 'fats_oils', 'calories': 119, 'carbs': 0, 'protein': 0, 'fat': 14},
            'Potato Chips': {'group': 'processed', 'calories': 152, 'carbs': 15, 'protein': 2, 'fat': 10},
            'Chocolate Bar': {'group': 'processed', 'calories': 210, 'carbs': 25, 'protein': 3, 'fat': 12}
        }
    
    def generate_nutrition_dataset(self, num_samples: int = 200) -> pd.DataFrame:
        """
        Generate a synthetic nutrition dataset with realistic values.
        
        Args:
            num_samples: Number of food items to generate
            
        Returns:
            DataFrame containing nutrition data
        """
        data = []
        
        # Sample foods from each category
        samples_per_category = num_samples // len(self.food_categories)
        remaining = num_samples % len(self.food_categories)
        
        for category_idx, (category, subcategories) in enumerate(self.food_categories.items()):
            # Adjust samples for remainder
            extra = 1 if category_idx < remaining else 0
            category_samples = samples_per_category + extra
            
            for _ in range(category_samples):
                food_item = self._generate_food_item(category, subcategories)
                data.append(food_item)
        
        df = pd.DataFrame(data)
        
        # Add calculated columns
        df['health_score'] = df.apply(self._calculate_health_score, axis=1)
        df['energy_density'] = df['energy_kcal'] / df['serving_size_g']
        df['protein_ratio'] = df['protein_g'] / df['serving_size_g'] * 100
        
        return df
    
    def _generate_food_item(self, category: str, subcategories: List[str]) -> Dict:
        """
        Generate a single food item with realistic nutrition data.
        """
        # Generate food name based on category
        food_name = self._generate_food_name(category)
        
        # Base nutrition based on category
        if category == 'cereals':
            nutrition = {
                'serving_size_g': random.randint(30, 100),
                'energy_kcal': random.randint(100, 350),
                'carbohydrates_g': round(random.uniform(15, 75), 1),
                'sugars_g': round(random.uniform(1, 20), 1),
                'fiber_g': round(random.uniform(2, 10), 1),
                'protein_g': round(random.uniform(2, 12), 1),
                'total_fat_g': round(random.uniform(0.5, 5), 1),
                'saturated_fat_g': round(random.uniform(0.1, 1.5), 1),
                'unsaturated_fat_g': round(random.uniform(0.3, 3), 1),
                'trans_fat_g': round(random.uniform(0, 0.2), 1),
                'cholesterol_mg': random.randint(0, 5),
                'sodium_mg': random.randint(0, 300),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': random.randint(0, 10),
                'calcium_percent_DV': random.randint(0, 20),
                'iron_percent_DV': random.randint(2, 50),
                'potassium_mg': random.randint(50, 300)
            }
        elif category == 'fruits':
            nutrition = {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(50, 150),
                'carbohydrates_g': round(random.uniform(10, 40), 1),
                'sugars_g': round(random.uniform(8, 30), 1),
                'fiber_g': round(random.uniform(2, 8), 1),
                'protein_g': round(random.uniform(0.5, 2), 1),
                'total_fat_g': round(random.uniform(0.1, 1), 1),
                'saturated_fat_g': round(random.uniform(0, 0.3), 1),
                'unsaturated_fat_g': round(random.uniform(0.05, 0.7), 1),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 5),
                'vitamin_A_percent_DV': random.randint(0, 25),
                'vitamin_C_percent_DV': random.randint(20, 150),
                'calcium_percent_DV': random.randint(0, 10),
                'iron_percent_DV': random.randint(0, 10),
                'potassium_mg': random.randint(200, 500)
            }
        elif category == 'vegetables':
            leafy = 'spinach' in food_name.lower() or 'kale' in food_name.lower() or 'lettuce' in food_name.lower()
            nutrition = {
                'serving_size_g': random.randint(80, 150),
                'energy_kcal': random.randint(20, 100) if not leafy else random.randint(10, 30),
                'carbohydrates_g': round(random.uniform(3, 20), 1),
                'sugars_g': round(random.uniform(1, 10), 1),
                'fiber_g': round(random.uniform(2, 8), 1),
                'protein_g': round(random.uniform(1, 5), 1),
                'total_fat_g': round(random.uniform(0.1, 1), 1),
                'saturated_fat_g': round(random.uniform(0, 0.2), 1),
                'unsaturated_fat_g': round(random.uniform(0.05, 0.5), 1),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 50),
                'vitamin_A_percent_DV': random.randint(10, 200) if leafy else random.randint(0, 50),
                'vitamin_C_percent_DV': random.randint(20, 120) if leafy else random.randint(10, 80),
                'calcium_percent_DV': random.randint(2, 30) if leafy else random.randint(0, 15),
                'iron_percent_DV': random.randint(5, 25) if leafy else random.randint(0, 15),
                'potassium_mg': random.randint(200, 600) if leafy else random.randint(100, 400)
            }
        elif category == 'meat':
            nutrition = {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(150, 400),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': round(random.uniform(20, 35), 1),
                'total_fat_g': round(random.uniform(5, 30), 1),
                'saturated_fat_g': round(random.uniform(2, 12), 1),
                'unsaturated_fat_g': round(random.uniform(2, 15), 1),
                'trans_fat_g': round(random.uniform(0, 0.5), 1),
                'cholesterol_mg': random.randint(50, 150),
                'sodium_mg': random.randint(50, 200),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': 0,
                'calcium_percent_DV': random.randint(0, 5),
                'iron_percent_DV': random.randint(10, 30),
                'potassium_mg': random.randint(300, 500)
            }
        elif category == 'fish':
            nutrition = {
                'serving_size_g': random.randint(100, 200),
                'energy_kcal': random.randint(150, 350),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': round(random.uniform(18, 30), 1),
                'total_fat_g': round(random.uniform(5, 20), 1),
                'saturated_fat_g': round(random.uniform(1, 5), 1),
                'unsaturated_fat_g': round(random.uniform(3, 15), 1),
                'trans_fat_g': 0,
                'cholesterol_mg': random.randint(40, 100),
                'sodium_mg': random.randint(50, 150),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(0, 10),
                'iron_percent_DV': random.randint(5, 20),
                'potassium_mg': random.randint(300, 600)
            }
        elif category == 'dairy':
            nutrition = {
                'serving_size_g': random.randint(100, 250),
                'energy_kcal': random.randint(100, 300),
                'carbohydrates_g': round(random.uniform(3, 15), 1),
                'sugars_g': round(random.uniform(2, 12), 1),
                'fiber_g': 0,
                'protein_g': round(random.uniform(5, 25), 1),
                'total_fat_g': round(random.uniform(2, 20), 1),
                'saturated_fat_g': round(random.uniform(1, 12), 1),
                'unsaturated_fat_g': round(random.uniform(0.5, 5), 1),
                'trans_fat_g': round(random.uniform(0, 0.3), 1),
                'cholesterol_mg': random.randint(10, 50),
                'sodium_mg': random.randint(50, 200),
                'vitamin_A_percent_DV': random.randint(5, 25),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(20, 50),
                'iron_percent_DV': random.randint(0, 5),
                'potassium_mg': random.randint(150, 400)
            }
        elif category == 'legumes':
            nutrition = {
                'serving_size_g': random.randint(100, 150),
                'energy_kcal': random.randint(100, 250),
                'carbohydrates_g': round(random.uniform(15, 40), 1),
                'sugars_g': round(random.uniform(1, 8), 1),
                'fiber_g': round(random.uniform(5, 15), 1),
                'protein_g': round(random.uniform(7, 20), 1),
                'total_fat_g': round(random.uniform(1, 10), 1),
                'saturated_fat_g': round(random.uniform(0.1, 1.5), 1),
                'unsaturated_fat_g': round(random.uniform(0.5, 8), 1),
                'trans_fat_g': 0,
                'cholesterol_mg': 0,
                'sodium_mg': random.randint(0, 50),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': random.randint(0, 15),
                'calcium_percent_DV': random.randint(2, 15),
                'iron_percent_DV': random.randint(10, 30),
                'potassium_mg': random.randint(300, 600)
            }
        elif category == 'fats_oils':
            nutrition = {
                'serving_size_g': random.randint(15, 30),
                'energy_kcal': random.randint(120, 250),
                'carbohydrates_g': 0,
                'sugars_g': 0,
                'fiber_g': 0,
                'protein_g': 0,
                'total_fat_g': round(random.uniform(13, 28), 1),
                'saturated_fat_g': round(random.uniform(2, 18), 1),
                'unsaturated_fat_g': round(random.uniform(10, 25), 1),
                'trans_fat_g': round(random.uniform(0, 0.3), 1),
                'cholesterol_mg': random.randint(0, 30),
                'sodium_mg': random.randint(0, 100),
                'vitamin_A_percent_DV': random.randint(0, 15),
                'vitamin_C_percent_DV': 0,
                'calcium_percent_DV': random.randint(0, 2),
                'iron_percent_DV': random.randint(0, 5),
                'potassium_mg': random.randint(0, 50)
            }
        elif category == 'processed':
            nutrition = {
                'serving_size_g': random.randint(30, 150),
                'energy_kcal': random.randint(150, 500),
                'carbohydrates_g': round(random.uniform(15, 60), 1),
                'sugars_g': round(random.uniform(5, 40), 1),
                'fiber_g': round(random.uniform(0, 3), 1),
                'protein_g': round(random.uniform(1, 10), 1),
                'total_fat_g': round(random.uniform(5, 30), 1),
                'saturated_fat_g': round(random.uniform(2, 15), 1),
                'unsaturated_fat_g': round(random.uniform(2, 12), 1),
                'trans_fat_g': round(random.uniform(0, 2), 1),
                'cholesterol_mg': random.randint(0, 50),
                'sodium_mg': random.randint(200, 800),
                'vitamin_A_percent_DV': random.randint(0, 10),
                'vitamin_C_percent_DV': random.randint(0, 5),
                'calcium_percent_DV': random.randint(0, 15),
                'iron_percent_DV': random.randint(2, 20),
                'potassium_mg': random.randint(50, 300)
            }
        
        # Add baseline scores
        baseline_scores = self._generate_baseline_scores(category, food_name)
        
        return {
            'food_name': food_name,
            'food_group': category,
            **nutrition,
            **baseline_scores
        }
    
    def _generate_food_name(self, category: str) -> str:
        """
        Generate a realistic food name based on category.
        """
        prefixes = {
            'cereals': ['Whole Grain', 'Organic', 'Fortified', 'Ancient', 'Sprouted'],
            'fruits': ['Fresh', 'Organic', 'Ripe', 'Juicy', 'Seasonal'],
            'vegetables': ['Fresh', 'Organic', 'Baby', 'Heirloom', 'Local'],
            'meat': ['Grass-fed', 'Organic', 'Free-range', 'Lean', 'Premium'],
            'fish': ['Wild-caught', 'Fresh', 'Sustainable', 'Ocean', 'Line-caught'],
            'dairy': ['Organic', 'Grass-fed', 'Low-fat', 'Full-fat', 'Artisanal'],
            'legumes': ['Organic', 'Sprouted', 'Dry', 'Canned', 'Fresh'],
            'fats_oils': ['Cold-pressed', 'Extra Virgin', 'Refined', 'Pure', 'Organic'],
            'processed': ['Classic', 'Premium', 'Artisanal', 'Gourmet', 'Traditional']
        }
        
        suffixes = {
            'cereals': ['Cereal', 'Flakes', 'Granola', 'Puffs', 'Bran'],
            'fruits': ['Apple', 'Banana', 'Orange', 'Berries', 'Melon'],
            'vegetables': ['Broccoli', 'Spinach', 'Carrots', 'Peppers', 'Tomatoes'],
            'meat': ['Steak', 'Chicken', 'Pork', 'Turkey', 'Lamb'],
            'fish': ['Salmon', 'Tuna', 'Cod', 'Shrimp', 'Crab'],
            'dairy': ['Milk', 'Yogurt', 'Cheese', 'Butter', 'Cream'],
            'legumes': ['Beans', 'Lentils', 'Chickpeas', 'Peas', 'Nuts'],
            'fats_oils': ['Oil', 'Butter', 'Spread', 'Dressing', 'Sauce'],
            'processed': ['Chips', 'Cookies', 'Cake', 'Pizza', 'Burger']
        }
        
        prefix = random.choice(prefixes[category])
        suffix = random.choice(suffixes[category])
        
        # Add variety
        varieties = {
            'cereals': ['Oat', 'Wheat', 'Rice', 'Corn', 'Barley'],
            'fruits': ['Red', 'Green', 'Golden', 'Sweet', 'Tart'],
            'vegetables': ['Green', 'Red', 'Yellow', 'Baby', 'Crunchy'],
            'meat': ['Beef', 'Chicken', 'Pork', 'Lamb', 'Duck'],
            'fish': ['Atlantic', 'Pacific', 'Freshwater', 'Saltwater'],
            'dairy': ['Cow', 'Goat', 'Sheep', 'Buffalo'],
            'legumes': ['Black', 'Red', 'White', 'Green', 'Brown'],
            'fats_oils': ['Olive', 'Coconut', 'Avocado', 'Sunflower', 'Canola'],
            'processed': ['Potato', 'Chocolate', 'Vanilla', 'Cheese', 'BBQ']
        }
        
        if random.random() > 0.5:
            variety = random.choice(varieties[category])
            return f"{prefix} {variety} {suffix}"
        else:
            return f"{prefix} {suffix}"
    
    def _generate_baseline_scores(self, category: str, food_name: str) -> Dict:
        """
        Generate baseline quality, safety, and nutritional scores.
        """
        # Determine storage type based on category
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
        
        storage = storage_map.get(category, 'ambient')
        
        # Shelf life based on storage type
        shelf_life = {
            'dry': random.randint(180, 730),      # 6 months to 2 years
            'refrigerated': random.randint(7, 30),  # 1 week to 1 month
            'frozen': random.randint(90, 365),    # 3 months to 1 year
            'ambient': random.randint(30, 365)    # 1 month to 1 year
        }[storage]
        
        # Generate scores (1-10 scale)
        if category in ['fruits', 'vegetables']:
            nutritional_score = random.randint(7, 10)
            safety_score = random.randint(8, 10) if 'organic' in food_name.lower() else random.randint(6, 9)
            quality_score = random.randint(7, 10)
        elif category in ['fish', 'meat']:
            nutritional_score = random.randint(6, 9)
            safety_score = random.randint(7, 10)
            quality_score = random.randint(6, 9)
        elif category == 'processed':
            nutritional_score = random.randint(3, 6)
            safety_score = random.randint(8, 10)  # Processed foods have preservatives
            quality_score = random.randint(5, 8)
        elif category == 'fats_oils':
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
            'shelf_life_days': shelf_life
        }
    
    def _calculate_health_score(self, row: pd.Series) -> float:
        """
        Calculate a health score from 1-10 based on nutrition data.
        """
        score = 5.0  # Base score
        
        # Positive factors
        if row['fiber_g'] > 5:
            score += 1
        if row['protein_g'] > 15:
            score += 0.5
        if row['unsaturated_fat_g'] > row['saturated_fat_g']:
            score += 0.5
        if row['vitamin_C_percent_DV'] > 20:
            score += 0.5
        if row['sodium_mg'] < 100:
            score += 0.5
        if row['cholesterol_mg'] < 50:
            score += 0.5
        if row['potassium_mg'] > 300:
            score += 0.3
        
        # Negative factors
        if row['saturated_fat_g'] > 10:
            score -= 1
        if row['sodium_mg'] > 500:
            score -= 1
        if row['trans_fat_g'] > 0.5:
            score -= 1.5
        if row['sugars_g'] > 25:
            score -= 1
        
        # Adjust based on food group
        if row['food_group'] in ['fruits', 'vegetables']:
            score += 0.5
        elif row['food_group'] in ['processed', 'fats_oils']:
            score -= 0.5
        
        # Ensure score is between 1 and 10
        return max(1, min(10, round(score, 1)))
    
    def save_dataset(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Save dataset to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = self.dataset_path
        
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename} with {len(df)} rows")
        
        # Also save summary statistics
        summary = self.get_dataset_summary(df)
        summary_path = filename.replace('.csv', '_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filename
    
    def load_dataset(self, filename: str = None) -> pd.DataFrame:
        """
        Load dataset from CSV file.
        
        Args:
            filename: Input filename (optional)
            
        Returns:
            Loaded DataFrame
        """
        if filename is None:
            filename = self.dataset_path
        
        if not os.path.exists(filename):
            print(f"Dataset not found at {filename}, generating new one...")
            df = self.generate_nutrition_dataset()
            self.save_dataset(df, filename)
            return df
        
        df = pd.read_csv(filename)
        print(f"Dataset loaded from {filename} with {len(df)} rows")
        return df
    
    def get_dataset_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for the dataset.
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_foods': len(df),
            'by_category': {},
            'nutrition_stats': {},
            'health_score_stats': {}
        }
        
        # Statistics by food group
        for group in df['food_group'].unique():
            group_data = df[df['food_group'] == group]
            summary['by_category'][group] = {
                'count': len(group_data),
                'avg_calories': round(group_data['energy_kcal'].mean(), 1),
                'avg_protein': round(group_data['protein_g'].mean(), 1),
                'avg_fat': round(group_data['total_fat_g'].mean(), 1),
                'avg_carbs': round(group_data['carbohydrates_g'].mean(), 1),
                'avg_sodium': round(group_data['sodium_mg'].mean(), 1),
                'avg_health_score': round(group_data['health_score'].mean(), 1)
            }
        
        # Overall nutrition statistics
        nutrition_cols = ['energy_kcal', 'protein_g', 'carbohydrates_g', 'total_fat_g', 
                         'fiber_g', 'sugars_g', 'sodium_mg', 'cholesterol_mg']
        
        for col in nutrition_cols:
            if col in df.columns:
                summary['nutrition_stats'][col] = {
                    'min': round(df[col].min(), 2),
                    'max': round(df[col].max(), 2),
                    'mean': round(df[col].mean(), 2),
                    'median': round(df[col].median(), 2),
                    'std': round(df[col].std(), 2)
                }
        
        # Health score statistics
        if 'health_score' in df.columns:
            summary['health_score_stats'] = {
                'min': df['health_score'].min(),
                'max': df['health_score'].max(),
                'mean': round(df['health_score'].mean(), 2),
                'median': df['health_score'].median(),
                'std': round(df['health_score'].std(), 2),
                'distribution': {
                    'excellent_9_10': len(df[df['health_score'] >= 9]),
                    'good_7_8': len(df[(df['health_score'] >= 7) & (df['health_score'] < 9)]),
                    'average_5_6': len(df[(df['health_score'] >= 5) & (df['health_score'] < 7)]),
                    'poor_3_4': len(df[(df['health_score'] >= 3) & (df['health_score'] < 5)]),
                    'very_poor_1_2': len(df[df['health_score'] < 3])
                }
            }
        
        return summary
    
    def analyze_meal(self, meal_items: List[Dict]) -> Dict:
        """
        Analyze a meal consisting of multiple food items.
        
        Args:
            meal_items: List of dictionaries with food items and quantities
            
        Returns:
            Dictionary with meal analysis
        """
        totals = {
            'calories': 0,
            'protein_g': 0,
            'carbohydrates_g': 0,
            'sugars_g': 0,
            'fiber_g': 0,
            'total_fat_g': 0,
            'saturated_fat_g': 0,
            'unsaturated_fat_g': 0,
            'trans_fat_g': 0,
            'cholesterol_mg': 0,
            'sodium_mg': 0,
            'potassium_mg': 0
        }
        
        food_groups = {}
        health_scores = []
        
        for item in meal_items:
            # Scale nutrition by quantity
            quantity = item.get('quantity', 1)
            food_data = item.get('nutrition_data', {})
            
            for nutrient in totals.keys():
                if nutrient in food_data:
                    totals[nutrient] += food_data[nutrient] * quantity
            
            # Track food groups
            food_group = item.get('food_group', 'unknown')
            food_groups[food_group] = food_groups.get(food_group, 0) + 1
            
            # Track health scores if available
            if 'health_score' in item:
                health_scores.append(item['health_score'])
        
        # Calculate percentages
        total_calories = totals['calories']
        if total_calories > 0:
            protein_percent = (totals['protein_g'] * 4 / total_calories) * 100
            carb_percent = (totals['carbohydrates_g'] * 4 / total_calories) * 100
            fat_percent = (totals['total_fat_g'] * 9 / total_calories) * 100
        else:
            protein_percent = carb_percent = fat_percent = 0
        
        # Calculate meal health score
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 5
        
        # Generate recommendations
        recommendations = self._generate_meal_recommendations(totals, food_groups)
        
        return {
            'totals': totals,
            'percentages': {
                'protein': round(protein_percent, 1),
                'carbohydrates': round(carb_percent, 1),
                'fat': round(fat_percent, 1)
            },
            'food_group_distribution': food_groups,
            'meal_health_score': round(avg_health_score, 1),
            'recommendations': recommendations,
            'daily_value_percentages': self._calculate_daily_value_percentages(totals)
        }
    
    def _generate_meal_recommendations(self, totals: Dict, food_groups: Dict) -> List[str]:
        """
        Generate recommendations based on meal analysis.
        """
        recommendations = []
        
        # Check protein
        if totals['protein_g'] < 15:
            recommendations.append("Consider adding more protein sources like lean meat, fish, eggs, or legumes.")
        
        # Check fiber
        if totals['fiber_g'] < 5:
            recommendations.append("Add more fiber-rich foods like vegetables, fruits, or whole grains.")
        
        # Check saturated fat
        if totals['saturated_fat_g'] > 10:
            recommendations.append("High saturated fat. Consider using healthier fat sources like olive oil or avocado.")
        
        # Check sodium
        if totals['sodium_mg'] > 500:
            recommendations.append("High sodium content. Try to reduce salt and processed foods.")
        
        # Check food diversity
        if len(food_groups) < 3:
            recommendations.append("Try to include more food groups for balanced nutrition.")
        
        # Check sugar
        if totals['sugars_g'] > 25:
            recommendations.append("High sugar content. Consider reducing added sugars.")
        
        # If no issues found
        if not recommendations:
            recommendations.append("Well-balanced meal! Keep up the good work.")
        
        return recommendations
    
    def _calculate_daily_value_percentages(self, totals: Dict) -> Dict:
        """
        Calculate percentages of daily values for nutrients.
        """
        percentages = {}
        
        # Map totals to daily values
        dv_mapping = {
            'protein_g': 'protein_g',
            'carbohydrates_g': 'carbs_g',
            'fiber_g': 'fiber_g',
            'sugars_g': 'sugars_g',
            'total_fat_g': 'total_fat_g',
            'saturated_fat_g': 'saturated_fat_g',
            'trans_fat_g': 'trans_fat_g',
            'cholesterol_mg': 'cholesterol_mg',
            'sodium_mg': 'sodium_mg',
            'potassium_mg': 'potassium_mg'
        }
        
        for nutrient, dv_key in dv_mapping.items():
            if nutrient in totals and dv_key in self.daily_values:
                dv = self.daily_values[dv_key]
                if dv > 0:
                    percentage = (totals[nutrient] / dv) * 100
                    percentages[nutrient] = round(percentage, 1)
        
        return percentages
    
    def search_foods(self, query: str, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Search for foods by name or group.
        
        Args:
            query: Search query
            df: DataFrame to search in (optional, loads dataset if None)
            
        Returns:
            DataFrame with search results
        """
        if df is None:
            df = self.load_dataset()
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Search in food names and groups
        mask = (
            df['food_name'].str.lower().str.contains(query_lower) |
            df['food_group'].str.lower().str.contains(query_lower)
        )
        
        results = df[mask].copy()
        
        # Sort by relevance (exact matches first, then partial matches)
        results['relevance'] = results.apply(
            lambda row: 2 if query_lower in row['food_name'].lower() else 1, axis=1
        )
        results = results.sort_values(['relevance', 'health_score'], ascending=[False, False])
        
        return results.drop('relevance', axis=1)
    
    def get_food_suggestions(self, nutrient_needs: Dict, df: pd.DataFrame = None, n: int = 5) -> pd.DataFrame:
        """
        Get food suggestions based on nutrient needs.
        
        Args:
            nutrient_needs: Dictionary of nutrient requirements
            df: DataFrame to search in
            n: Number of suggestions to return
            
        Returns:
            DataFrame with food suggestions
        """
        if df is None:
            df = self.load_dataset()
        
        # Create a scoring system based on nutrient needs
        scores = []
        
        for idx, row in df.iterrows():
            score = 0
            
            # Score based on nutrient matches
            for nutrient, target in nutrient_needs.items():
                if nutrient in row:
                    value = row[nutrient]
                    # Higher score if nutrient is close to target
                    if target > 0:
                        ratio = min(value / target, 2)  # Cap at 2x target
                        score += ratio
            
            # Bonus for high health score
            if 'health_score' in row:
                score += row['health_score'] / 10
            
            scores.append(score)
        
        df_copy = df.copy()
        df_copy['match_score'] = scores
        
        # Return top N matches
        return df_copy.nlargest(n, 'match_score')
    
    def export_to_json(self, df: pd.DataFrame, filename: str = 'nutrition_database.json') -> str:
        """
        Export dataset to JSON format for use in web applications.
        
        Args:
            df: DataFrame to export
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        # Add metadata
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_items': len(data),
                'food_groups': list(df['food_group'].unique()),
                'nutrients': list(df.columns)
            },
            'foods': data
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Data exported to {filename}")
        return filename
    
    def generate_sample_meal_plan(self, calorie_target: int = 2000) -> Dict:
        """
        Generate a sample meal plan for a day.
        
        Args:
            calorie_target: Target daily calories
            
        Returns:
            Dictionary with meal plan
        """
        df = self.load_dataset()
        
        # Target distribution: 30% breakfast, 35% lunch, 35% dinner
        meal_targets = {
            'breakfast': int(calorie_target * 0.3),
            'lunch': int(calorie_target * 0.35),
            'dinner': int(calorie_target * 0.35)
        }
        
        meal_plan = {}
        
        for meal_name, target_calories in meal_targets.items():
            # Filter foods appropriate for the meal
            if meal_name == 'breakfast':
                suitable_groups = ['cereals', 'fruits', 'dairy']
            elif meal_name == 'lunch':
                suitable_groups = ['meat', 'fish', 'vegetables', 'legumes']
            else:  # dinner
                suitable_groups = ['meat', 'fish', 'vegetables', 'legumes']
            
            # Get suitable foods
            suitable_foods = df[df['food_group'].isin(suitable_groups)].copy()
            
            # Select foods to reach calorie target
            selected_foods = []
            remaining_calories = target_calories
            
            while remaining_calories > 100 and len(suitable_foods) > 0:
                # Randomly select a food
                food = suitable_foods.sample(1).iloc[0]
                
                # Calculate portion size (aim for 1-2 servings)
                food_calories = food['energy_kcal']
                portion_multiplier = min(2, remaining_calories / food_calories)
                
                if portion_multiplier >= 0.5:  # Only add if reasonable portion
                    selected_foods.append({
                        'food_name': food['food_name'],
                        'food_group': food['food_group'],
                        'serving_size_g': food['serving_size_g'],
                        'portion_multiplier': round(portion_multiplier, 1),
                        'calories': round(food_calories * portion_multiplier, 1),
                        'protein_g': round(food['protein_g'] * portion_multiplier, 1),
                        'carbs_g': round(food['carbohydrates_g'] * portion_multiplier, 1),
                        'fat_g': round(food['total_fat_g'] * portion_multiplier, 1)
                    })
                    
                    remaining_calories -= food_calories * portion_multiplier
                
                # Remove selected food to avoid duplicates
                suitable_foods = suitable_foods[suitable_foods['food_name'] != food['food_name']]
            
            meal_plan[meal_name] = {
                'target_calories': target_calories,
                'selected_foods': selected_foods,
                'total_calories': sum(f['calories'] for f in selected_foods),
                'remaining_calories': max(0, remaining_calories)
            }
        
        # Add snacks if there are remaining calories
        snack_calories = calorie_target - sum(m['total_calories'] for m in meal_plan.values())
        if snack_calories > 100:
            snack_foods = df[df['food_group'].isin(['fruits', 'dairy', 'legumes'])].copy()
            
            if len(snack_foods) > 0:
                snack_food = snack_foods.sample(1).iloc[0]
                meal_plan['snack'] = {
                    'target_calories': snack_calories,
                    'selected_foods': [{
                        'food_name': snack_food['food_name'],
                        'food_group': snack_food['food_group'],
                        'serving_size_g': snack_food['serving_size_g'],
                        'portion_multiplier': 1,
                        'calories': snack_food['energy_kcal'],
                        'protein_g': snack_food['protein_g'],
                        'carbs_g': snack_food['carbohydrates_g'],
                        'fat_g': snack_food['total_fat_g']
                    }],
                    'total_calories': snack_food['energy_kcal']
                }
        
        return meal_plan

# Example usage
if __name__ == "__main__":
    # Create nutrition data manager
    manager = NutritionDataManager()
    
    # Generate and save dataset
    print("Generating nutrition dataset...")
    df = manager.generate_nutrition_dataset(200)
    manager.save_dataset(df)
    
    # Print summary
    summary = manager.get_dataset_summary(df)
    print(f"\nDataset Summary:")
    print(f"Total foods: {summary['total_foods']}")
    
    print("\nBy Category:")
    for category, stats in summary['by_category'].items():
        print(f"  {category}: {stats['count']} items, Avg Health Score: {stats['avg_health_score']}")
    
    # Example: Search for foods
    print("\nSearching for 'apple':")
    results = manager.search_foods('apple', df)
    if len(results) > 0:
        print(f"Found {len(results)} results:")
        for _, row in results.head(3).iterrows():
            print(f"  - {row['food_name']} ({row['food_group']}): {row['energy_kcal']} kcal")
    
    # Example: Generate meal plan
    print("\nGenerating sample meal plan (2000 calories):")
    meal_plan = manager.generate_sample_meal_plan(2000)
    for meal, data in meal_plan.items():
        print(f"\n{meal.capitalize()}:")
        print(f"  Target: {data['target_calories']} calories")
        print(f"  Selected: {len(data['selected_foods'])} items")
        for food in data['selected_foods']:
            print(f"    - {food['food_name']}: {food['calories']} calories")
    
    # Export to JSON for web use
    json_path = manager.export_to_json(df)
    print(f"\nDataset exported to {json_path}")