from flask import Flask, jsonify, request
from flask_cors import CORS
from config import load_config
from data_processing import process_file
from quiz_generator import generate_quiz
from answer_evaluator import evaluate_answers

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

config = load_config()

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz_route():
    try:
        context = request.form.get("context", "")
        quiz_type = request.form.get("quiz_type")
        num_questions = int(request.form.get("num_questions"))
        quiz_language = request.form.get("quiz_language", "English")
        file = request.files.get("file")

        file_content = process_file(file) if file else ""
        quiz_data = generate_quiz(context, file_content, quiz_type, num_questions, quiz_language, config['api_key'])
        return jsonify(quiz_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate-answers', methods=['POST'])
def evaluate_answers_route():
    try:
        data = request.get_json()
        evaluations = evaluate_answers(data, config['api_key'])
        return jsonify({"evaluations": evaluations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)