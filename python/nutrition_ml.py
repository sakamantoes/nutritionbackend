import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import os

class NutritionMLModels:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.dataset_path = 'nutrition_dataset.csv'

    def load_and_prepare_data(self):
        """Load and prepare the nutrition dataset"""
        if not os.path.exists(self.dataset_path):
            print(f"Dataset not found at {self.dataset_path}")
            return None

        df = pd.read_csv(self.dataset_path)
        print(f"Loaded dataset with {len(df)} rows")

        # 1. Food Group Classification Features
        classification_features = [
            'energy_kcal', 'carbohydrates_g', 'protein_g', 'total_fat_g',
            'fiber_g', 'sugars_g', 'sodium_mg', 'cholesterol_mg'
        ]
        X_class = df[classification_features]
        y_class = df['food_group']

        le_food = LabelEncoder()
        y_class_encoded = le_food.fit_transform(y_class)
        self.label_encoders['food_group'] = le_food

        # 2. Health Score Prediction Features
        df['health_score'] = self.calculate_health_score(df)
        regression_features = classification_features + [
            'saturated_fat_g', 'unsaturated_fat_g', 'trans_fat_g',
            'vitamin_C_percent_DV', 'calcium_percent_DV', 'iron_percent_DV',
            'potassium_mg'
        ]
        X_reg = df[regression_features]
        y_reg = df['health_score']

        # 3. Storage Type Classification
        storage_features = [
            'energy_kcal', 'protein_g', 'total_fat_g', 'sodium_mg',
            'baseline_nutritional_score', 'baseline_safety_score'
        ]
        X_storage = df[storage_features]
        y_storage = df['storage_type']

        le_storage = LabelEncoder()
        y_storage_encoded = le_storage.fit_transform(y_storage)
        self.label_encoders['storage_type'] = le_storage

        return {
            'classification': (X_class, y_class_encoded),
            'regression': (X_reg, y_reg),
            'storage': (X_storage, y_storage_encoded),
            'df': df
        }

    def calculate_health_score(self, df):
        """Calculate a health score from 1-10 based on nutrition"""
        scores = []

        for _, row in df.iterrows():
            score = 5.0  # Base score

            # Positive factors
            if row['fiber_g'] > 5:
                score += 1
            if row['protein_g'] > 15:
                score += 0.5
            if row.get('unsaturated_fat_g', 0) > row.get('saturated_fat_g', 0):
                score += 0.5
            if row.get('vitamin_C_percent_DV', 0) > 20:
                score += 0.5
            if row['sodium_mg'] < 100:
                score += 0.5
            if row['cholesterol_mg'] < 50:
                score += 0.5

            # Negative factors
            if row.get('saturated_fat_g', 0) > 10:
                score -= 1
            if row['sodium_mg'] > 500:
                score -= 1
            if row.get('trans_fat_g', 0) > 0.5:
                score -= 1.5
            if row['sugars_g'] > 25:
                score -= 1

            score = max(1, min(10, score))
            scores.append(score)

        return scores

    def train_models(self):
        """Train all ML models"""
        data = self.load_and_prepare_data()
        if data is None:
            print("Failed to load data")
            return

        # ---------- Food Group Classifier ----------
        X_class, y_class = data['classification']
        X_train, X_test, y_train, y_test = train_test_split(
            X_class, y_class, test_size=0.2, random_state=42
        )

        scaler_class = StandardScaler()
        X_train_scaled = scaler_class.fit_transform(X_train)
        X_test_scaled = scaler_class.transform(X_test)
        self.scalers['classification'] = scaler_class

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Food Group Classification Accuracy: {accuracy:.2f}")
        self.models['food_group_classifier'] = clf

        # ---------- Health Score Regressor ----------
        X_reg, y_reg = data['regression']
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )

        scaler_reg = StandardScaler()
        X_train_reg_scaled = scaler_reg.fit_transform(X_train_reg)
        X_test_reg_scaled = scaler_reg.transform(X_test_reg)
        self.scalers['regression'] = scaler_reg

        reg = RandomForestRegressor(n_estimators=100, random_state=42)
        reg.fit(X_train_reg_scaled, y_train_reg)
        y_pred_reg = reg.predict(X_test_reg_scaled)
        mse = mean_squared_error(y_test_reg, y_pred_reg)
        print(f"Health Score Regression MSE: {mse:.2f}")
        self.models['health_score_regressor'] = reg

        # ---------- Storage Type Classifier ----------
        X_storage, y_storage = data['storage']
        X_train_store, X_test_store, y_train_store, y_test_store = train_test_split(
            X_storage, y_storage, test_size=0.2, random_state=42
        )

        scaler_store = StandardScaler()
        X_train_store_scaled = scaler_store.fit_transform(X_train_store)
        X_test_store_scaled = scaler_store.transform(X_test_store)
        self.scalers['storage'] = scaler_store

        clf_store = RandomForestClassifier(n_estimators=50, random_state=42)
        clf_store.fit(X_train_store_scaled, y_train_store)
        y_pred_store = clf_store.predict(X_test_store_scaled)
        accuracy_store = accuracy_score(y_test_store, y_pred_store)
        print(f"Storage Type Classification Accuracy: {accuracy_store:.2f}")
        self.models['storage_classifier'] = clf_store

        self.save_models()

        return {'accuracy': accuracy, 'mse': mse, 'storage_accuracy': accuracy_store}

    def predict_food_group(self, nutrition_data):
        """Predict food group from nutrition data"""
        if 'food_group_classifier' not in self.models:
            self.load_models()

        features = [
            'energy_kcal', 'carbohydrates_g', 'protein_g', 'total_fat_g',
            'fiber_g', 'sugars_g', 'sodium_mg', 'cholesterol_mg'
        ]

        # Make sure input is a DataFrame with same columns
        input_df = pd.DataFrame([{f: nutrition_data.get(f, 0) for f in features}])
        input_scaled = self.scalers['classification'].transform(input_df)
        pred = self.models['food_group_classifier'].predict(input_scaled)[0]
        return self.label_encoders['food_group'].inverse_transform([pred])[0]

    def predict_health_score(self, nutrition_data):
        """Predict health score from nutrition data"""
        if 'health_score_regressor' not in self.models:
            self.load_models()

        features = [
            'energy_kcal', 'carbohydrates_g', 'protein_g', 'total_fat_g',
            'fiber_g', 'sugars_g', 'sodium_mg', 'cholesterol_mg',
            'saturated_fat_g', 'unsaturated_fat_g', 'trans_fat_g',
            'vitamin_C_percent_DV', 'calcium_percent_DV', 'iron_percent_DV',
            'potassium_mg'
        ]

        input_df = pd.DataFrame([{f: nutrition_data.get(f, 0) for f in features}])
        input_scaled = self.scalers['regression'].transform(input_df)
        score = self.models['health_score_regressor'].predict(input_scaled)[0]
        return max(1, min(10, float(score)))

    def save_models(self):
        os.makedirs('models', exist_ok=True)

        for name, model in self.models.items():
            joblib.dump(model, f'models/{name}.joblib')
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/{name}_scaler.joblib')
        for name, le in self.label_encoders.items():
            joblib.dump(le, f'models/{name}_encoder.joblib')

        print("Models saved to 'models' directory")

    def load_models(self):
        try:
            self.models = {
                'food_group_classifier': joblib.load('models/food_group_classifier.joblib'),
                'health_score_regressor': joblib.load('models/health_score_regressor.joblib'),
                'storage_classifier': joblib.load('models/storage_classifier.joblib')
            }
            self.scalers = {
                'classification': joblib.load('models/classification_scaler.joblib'),
                'regression': joblib.load('models/regression_scaler.joblib'),
                'storage': joblib.load('models/storage_scaler.joblib')
            }
            self.label_encoders = {
                'food_group': joblib.load('models/food_group_encoder.joblib'),
                'storage_type': joblib.load('models/storage_type_encoder.joblib')
            }
            print("Models loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


def main():
    ml_models = NutritionMLModels()
    print("Training ML models...")
    ml_models.train_models()

    print("\nTesting predictions with sample data...")
    sample_nutrition = {
   'energy_kcal': 112,
    'carbohydrates_g': 23.5,
    'protein_g': 2.6,
    'total_fat_g': 0.9,
    'fiber_g': 1.8,
    'sugars_g': 0.4,
    'sodium_mg': 5,
    'cholesterol_mg': 0,
    'saturated_fat_g': 0.2,
    'unsaturated_fat_g': 0.5,
    'trans_fat_g': 0,
    'vitamin_C_percent_DV': 0,
    'calcium_percent_DV': 1,
    'iron_percent_DV': 3,
    'potassium_mg': 84
    }

    food_group = ml_models.predict_food_group(sample_nutrition)
    health_score = ml_models.predict_health_score(sample_nutrition)

    print(f"\nSample Prediction:")
    print(f"Predicted Food Group: {food_group}")
    print(f"Predicted Health Score: {health_score:.1f}/10")


if __name__ == "__main__":
    main()
