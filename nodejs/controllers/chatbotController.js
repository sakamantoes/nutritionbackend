// Rule-based chatbot responses
const getResponse = (message) => {
    const lowerMessage = message.toLowerCase().trim();
    
    // Define response rules
    const rules = [
        {
            keywords: ['hello', 'hi', 'hey'],
            response: "Hello! I'm your nutrition assistant. How can I help you today?"
        },
        {
            keywords: ['how are you', 'how do you do'],
            response: "I'm great! Ready to help you with your nutrition questions."
        },
        {
            keywords: ['calorie', 'calories'],
            response: "Calories are units of energy from food. The average adult needs 2000-2500 calories daily depending on age, gender, and activity level."
        },
        {
            keywords: ['protein'],
            response: "Protein helps build and repair tissues. Aim for 0.8-1.2g per kg of body weight daily. Good sources: meat, fish, eggs, dairy, legumes."
        },
        {
            keywords: ['carb', 'carbohydrate'],
            response: "Carbs are your body's main energy source. Choose complex carbs like whole grains, fruits, and vegetables over simple sugars."
        },
        {
            keywords: ['fat'],
            response: "Healthy fats are essential for brain function and hormone production. Focus on unsaturated fats from nuts, seeds, avocados, and olive oil."
        },
        {
            keywords: ['fiber'],
            response: "Fiber aids digestion and helps control blood sugar. Aim for 25-30g daily from fruits, vegetables, whole grains, and legumes."
        },
        {
            keywords: ['vitamin'],
            response: "Vitamins are essential nutrients your body needs in small amounts. Eat a variety of colorful fruits and vegetables to get different vitamins."
        },
        {
            keywords: ['mineral'],
            response: "Minerals like calcium, iron, and potassium are crucial for body functions. Dairy, leafy greens, and bananas are good sources."
        },
        {
            keywords: ['weight loss', 'lose weight'],
            response: "For weight loss, create a calorie deficit through diet and exercise. Aim for 1-2 pounds per week for sustainable loss."
        },
        {
            keywords: ['weight gain', 'gain weight'],
            response: "To gain weight healthily, consume more calories than you burn and focus on strength training to build muscle."
        },
        {
            keywords: ['healthy diet', 'balanced diet'],
            response: "A healthy diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods, sugar, and saturated fats."
        },
        {
            keywords: ['meal plan', 'meal planning'],
            response: "Plan meals around protein, complex carbs, and healthy fats. Include 3 main meals and 1-2 snacks. Prepare in advance for success."
        },
        {
            keywords: ['breakfast'],
            response: "A good breakfast includes protein, fiber, and healthy fats. Examples: eggs with whole grain toast, Greek yogurt with berries, or oatmeal with nuts."
        },
        {
            keywords: ['lunch'],
            response: "Lunch should be balanced. Try salads with protein, whole grain sandwiches, or leftovers from dinner."
        },
        {
            keywords: ['dinner'],
            response: "Dinner should be lighter than lunch. Focus on vegetables and lean protein. Examples: grilled fish with vegetables, stir-fry, or soup."
        },
        {
            keywords: ['snack', 'snacks'],
            response: "Healthy snacks include fruits, nuts, yogurt, vegetables with hummus, or a small portion of cheese."
        },
        {
            keywords: ['water', 'hydration'],
            response: "Drink at least 8 glasses (2 liters) of water daily. More if you exercise or live in a hot climate."
        },
        {
            keywords: ['sugar'],
            response: "Limit added sugars to less than 10% of daily calories. Read labels - sugar has many names like sucrose, fructose, and corn syrup."
        },
        {
            keywords: ['salt', 'sodium'],
            response: "Limit sodium to less than 2300mg daily. Most sodium comes from processed foods, not table salt."
        },
        {
            keywords: ['exercise', 'workout'],
            response: "Aim for 150 minutes of moderate exercise or 75 minutes of vigorous exercise weekly, plus strength training twice a week."
        },
        {
            keywords: ['vegetarian'],
            response: "Vegetarian diets can be healthy with proper planning. Ensure adequate protein from legumes, dairy, eggs, and soy products."
        },
        {
            keywords: ['vegan'],
            response: "Vegan diets require attention to B12, iron, calcium, and omega-3. Consider supplements and eat fortified foods."
        },
        {
            keywords: ['gluten'],
            response: "Gluten-free diets are necessary for celiac disease. Otherwise, whole grains with gluten can be part of a healthy diet."
        },
        {
            keywords: ['dairy'],
            response: "Dairy provides calcium and protein. Alternatives include fortified plant milks, leafy greens, and tofu for calcium."
        },
        {
            keywords: ['fruit'],
            response: "Fruits provide vitamins, fiber, and antioxidants. Aim for 2-3 servings daily of different colors."
        },
        {
            keywords: ['vegetable'],
            response: "Vegetables are nutrient-dense and low in calories. Aim for 3-5 servings daily, focusing on variety."
        },
        {
            keywords: ['sleep'],
            response: "Aim for 7-9 hours of sleep. Poor sleep affects hunger hormones and can lead to weight gain."
        },
        {
            keywords: ['stress'],
            response: "Chronic stress affects digestion and food choices. Practice stress management through exercise, meditation, or hobbies."
        },
        {
            keywords: ['detox', 'cleanse'],
            response: "Your body naturally detoxifies through liver and kidneys. Focus on a healthy diet with plenty of water rather than detox products."
        },
        {
            keywords: ['supplement'],
            response: "Supplements can help fill nutritional gaps but shouldn't replace whole foods. Consult a healthcare provider before starting."
        },
        {
            keywords: ['thank', 'thanks'],
            response: "You're welcome! Is there anything else I can help you with?"
        },
        {
            keywords: ['bye', 'goodbye'],
            response: "Goodbye! Remember to eat a balanced diet and stay hydrated!"
        },
        {
            keywords: ['help'],
            response: "I can help with nutrition advice, meal planning, exercise recommendations, and analyzing your diet. What would you like to know?"
        }
    ];
    
    // Find matching rule
    for (const rule of rules) {
        for (const keyword of rule.keywords) {
            if (lowerMessage.includes(keyword)) {
                return rule.response;
            }
        }
    }
    
    // Default response if no rules match
    return "I'm here to help with nutrition and health questions. Could you be more specific about what you'd like to know?";
};

class ChatbotController {
    // Handle chatbot message
    async handleMessage(req, res) {
        try {
            const { message, userId } = req.body;
            
            if (!message) {
                return res.status(400).json({ error: 'Message is required' });
            }
            
            // Get response from rule-based chatbot
            const response = getResponse(message);
            
            // If we have a user ID, we could store the conversation
            if (userId) {
                // In a full implementation, we would store the conversation
                console.log(`User ${userId}: ${message}`);
                console.log(`Bot: ${response}`);
            }
            
            res.json({
                response,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('Chatbot error:', error);
            res.status(500).json({ error: 'Failed to process message' });
        }
    }
}

module.exports = new ChatbotController();