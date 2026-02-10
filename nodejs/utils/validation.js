const { z } = require('zod');

// User validation schemas
const userRegistrationSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    age: z.number().min(1).max(120),
    weight: z.number().min(20).max(300),
    height: z.number().min(100).max(250),
    goal: z.enum(['lose', 'gain', 'maintain']),
    activity_level: z.enum(['sedentary', 'light', 'moderate', 'active', 'very_active'])
});

const userLoginSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(1, 'Password is required')
});

// Food logging validation schemas
const foodLogSchema = z.object({
    userId: z.number().int().positive(),
    foodName: z.string().min(1, 'Food name is required'),
    foodGroup: z.enum(['cereals', 'fruits', 'vegetables', 'meat', 'fish', 'dairy', 'legumes', 'fats_oils', 'processed']),
    servingSize: z.number().positive('Serving size must be positive'),
    calories: z.number().nonnegative('Calories cannot be negative'),
    protein: z.number().nonnegative('Protein cannot be negative'),
    carbs: z.number().nonnegative('Carbs cannot be negative'),
    fat: z.number().nonnegative('Fat cannot be negative'),
    mealType: z.enum(['breakfast', 'lunch', 'dinner', 'snack']),
    imageUrl: z.string().url('Invalid URL').optional().or(z.literal(''))
});

// Exercise validation schemas
const exerciseSchema = z.object({
    userId: z.number().int().positive(),
    exerciseName: z.string().min(1, 'Exercise name is required'),
    duration: z.number().positive('Duration must be positive'),
    caloriesBurned: z.number().positive('Calories burned must be positive'),
    exerciseType: z.enum(['cardio', 'strength', 'flexibility'])
});

// Chatbot validation schemas
const chatbotMessageSchema = z.object({
    message: z.string().min(1, 'Message is required'),
    userId: z.number().int().positive().optional()
});

// Validation function
const validate = (schema) => (req, res, next) => {
    try {
        schema.parse(req.body);
        next();
    } catch (error) {
        const errors = error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message
        }));
        res.status(400).json({ errors });
    }
};

module.exports = {
    userRegistrationSchema,
    userLoginSchema,
    foodLogSchema,
    exerciseSchema,
    chatbotMessageSchema,
    validate
};