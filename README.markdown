# Quiz App Laura

## Overview
Quiz App Laura is a web application designed to generate and evaluate quizzes based on user-provided context or uploaded files. It supports multiple quiz types (multiple-choice, true/false, and open-ended), allows users to save and load quizzes, and provides feedback on open-ended answers using AI-powered evaluation.

## Features
- **Quiz Generation**: Create quizzes from text context or uploaded files (PDF or text).
- **Quiz Types**: Supports multiple-choice, true/false, and open-ended questions.
- **Multilingual Support**: Generate quizzes in English or Hungarian.
- **Answer Evaluation**: AI-driven evaluation for open-ended questions with detailed feedback.
- **Quiz Management**: Save, load, and delete quizzes using local storage.
- **Responsive UI**: Built with Vue.js and styled with Tailwind CSS for a modern, user-friendly interface.

## Tech Stack
- **Backend**:
  - Flask (Python) for API endpoints.
  - LangChain and OpenAI for quiz generation and answer evaluation.
  - PyPDF2 for PDF processing.
  - FAISS for vector-based document retrieval.
- **Frontend**:
  - Vue.js for dynamic, component-based UI.
  - Tailwind CSS for styling.
  - LocalStorage for persisting saved quizzes.
- **Dependencies**:
  - Python libraries: `flask`, `flask-cors`, `langchain-openai`, `PyPDF2`, `faiss-cpu`.
  - JavaScript libraries: `vue`, `axios` (implied for API calls).

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (set in `config.py`)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `config.py` file in the root directory with your OpenAI API key:
   ```python
   def load_config():
       return {"api_key": "your-openai-api-key"}
   ```
4. Run the Flask server:
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5000`.

### Frontend Setup
1. Navigate to the frontend directory (if separate) or root:
   ```bash
   cd frontend  # Adjust if frontend is in a subdirectory
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or the port specified by Vite).

## Usage
1. **Generate a Quiz**:
   - Enter context in the text area or upload a PDF/text file.
   - Select quiz type, language, and number of questions (1–5).
   - Click "Generate Quiz" to create the quiz.
2. **Answer Questions**:
   - For multiple-choice or true/false, select an option.
   - For open-ended, type your answer in the provided textarea.
3. **Evaluate Answers**:
   - For open-ended quizzes, click "Evaluate Answers" to get AI-generated feedback.
4. **Manage Quizzes**:
   - Save quizzes with "Save Quiz".
   - View, load, or delete saved quizzes via "Show Saved Quizzes".

## File Structure
- **Backend**:
  - `app.py`: Main Flask application with API endpoints.
  - `quiz_generator.py`: Generates quizzes using LangChain and OpenAI.
  - `answer_evaluator.py`: Evaluates open-ended answers.
  - `data_processing.py`: Processes uploaded files (PDF/text).
  - `config.py`: Stores configuration (e.g., API key).
- **Frontend**:
  - `QuizApp.vue`: Main component orchestrating the app.
  - `QuizForm.vue`: Form for quiz configuration.
  - `QuizQuestions.vue`: Displays and handles quiz questions.
  - `QuizAnswers.vue`: Shows answers for non-open-ended quizzes.
  - `SavedQuizzes.vue`: Manages saved quizzes.

## API Endpoints
- **POST `/generate-quiz`**:
  - Input: Form data (`context`, `quiz_type`, `num_questions`, `quiz_language`, `file`).
  - Output: JSON with questions, answers, and alternatives (if applicable).
- **POST `/evaluate-answers`**:
  - Input: JSON (`questions`, `user_answers`, `reference_answers`, `context`, `quiz_language`).
  - Output: JSON with evaluations (feedback and correctness).

## Notes
- Ensure the Flask backend is running before using the frontend.
- The app uses local storage for saving quizzes, so data persists only in the browser.
- For production, configure CORS properly and use environment variables for sensitive data.
- The OpenAI API key must be valid and have sufficient quota.
