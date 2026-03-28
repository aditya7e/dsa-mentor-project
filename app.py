from flask import Flask, jsonify, request
from flask_cors import CORS
from quiz_generator import generate_quiz_zero_shot
from roadmap_generator import generate_roadmap
from quiz_generator import generate_quiz_zero_shot, generate_topic_quiz

app = Flask(__name__)
CORS(app)

current_quiz = None

@app.route('/')
def home():
    return "DSA Mentor Backend is Running! 🚀"

@app.route('/api/test')
def test():
    return jsonify({
        "message": "API is working!",
        "status": "success"
    })

@app.route('/api/quiz/generate', methods=['GET'])
def get_quiz():
    global current_quiz
    
    try:
        print("Generating quiz...")
        current_quiz = generate_quiz_zero_shot()
        
        if current_quiz:
            return jsonify({
                "status": "success",
                "message": "Quiz generated successfully",
                "data": current_quiz
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to generate quiz"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/roadmap/generate', methods=['POST'])
def generate_roadmap_api():
    try:
        data = request.json
        user_answers = data.get('user_answers')
        quiz_questions = data.get('quiz_questions')
        
        if not user_answers or not quiz_questions:
            return jsonify({
                "status": "error",
                "message": "Missing user_answers or quiz_questions"
            }), 400
        
        # Generate roadmap
        result = generate_roadmap(user_answers, quiz_questions)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/quiz/topic/<topic>', methods=['GET'])
def get_topic_quiz(topic):
    try:
        print(f"Generating topic quiz for: {topic}")
        quiz = generate_topic_quiz(topic, num_questions=30)
        
        if quiz:
            return jsonify({
                "status": "success",
                "message": f"Topic quiz generated for {topic}",
                "data": quiz
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to generate topic quiz"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/problems/additional/<topic>/<difficulty>', methods=['GET'])
def get_additional_problems(topic, difficulty):
    """
    Get 3-5 additional problems for a topic at a specific difficulty
    """
    try:
        # Load problems database
        import json
        with open('problems_database.json', 'r') as f:
            db = json.load(f)
        
        if topic not in db:
            return jsonify({
                "status": "error",
                "message": f"Topic {topic} not found"
            }), 404
        
        # Get all problems for this topic
        all_problems = db[topic]['problems']
        
        # Filter by difficulty if specified
        if difficulty and difficulty != 'mixed':
            filtered = [p for p in all_problems if p['difficulty'] == difficulty]
        else:
            filtered = all_problems
        
        # Randomly select 3-5 problems
        import random
        num_problems = min(5, len(filtered))
        if num_problems < 3:
            num_problems = len(filtered)
        
        selected = random.sample(filtered, num_problems) if filtered else []
        
        return jsonify({
            "status": "success",
            "problems": selected
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)