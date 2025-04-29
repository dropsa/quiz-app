<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-2xl bg-white rounded-xl shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">Quiz App Laura</h1>
      <p class="text-gray-600 mb-8 text-center">Generate a quiz based on your context</p>

      <div class="space-y-6">
        <QuizForm
          :context="context"
          :quizType="quizType"
          :quizLanguage="quizLanguage"
          :numQuestions="numQuestions"
          :file="file"
          :fileName="fileName"
          @update:context="context = $event"
          @update:quizType="quizType = $event"
          @update:quizLanguage="quizLanguage = $event"
          @update:numQuestions="numQuestions = $event"
          @update:file="file = $event"
          @update:fileName="fileName = $event"
        />

        <div class="flex space-x-4">
          <transition name="fade">
            <button @click="generateQuiz" class="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold btn-shadow">
              Generate Quiz
            </button>
          </transition>
          <transition name="fade">
            <button v-if="quizType !== 'open-ended' && questions.length > 0" @click="showAnswers" class="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition font-semibold btn-shadow">
              Show Answers
            </button>
          </transition>
          <transition name="fade">
            <button v-if="quizType === 'open-ended' && questions.length > 0" @click="evaluateAnswers" class="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition font-semibold btn-shadow">
              Evaluate Answers
            </button>
          </transition>
          <transition name="fade">
            <button v-if="questions.length > 0" @click="saveQuiz" class="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition font-semibold btn-shadow">
              Save Quiz
            </button>
          </transition>
          <transition name="fade">
            <button @click="showSavedQuizzes = true" class="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold btn-shadow">
              Show Saved Quizzes
            </button>
          </transition>
          <transition name="fade">
            <button v-if="questions.length > 0" @click="editMode = !editMode" class="flex-1 bg-yellow-600 text-white py-3 rounded-lg hover:bg-yellow-700 transition font-semibold btn-shadow">
              {{ editMode ? 'Done Editing' : 'Edit Quiz' }}
            </button>
          </transition>
        </div>

        <div v-if="isLoading" class="flex justify-center mt-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-500"></div>
        </div>

        <QuizQuestions
          v-if="!isLoading && questions.length > 0"
          :questions="questions"
          :quizType="quizType"
          :alternatives="alternatives"
          :userAnswers="userAnswers"
          :evaluations="evaluations"
          :answers="answers"
          :editMode="editMode"
          :editingIndex="editingIndex"
          @selectAnswer="selectAnswer"
          @update:userAnswers="userAnswers = $event"
          @editQuestion="editingIndex = $event"
          @addQuestion="editingIndex = -1"
          @saveQuestion="handleSaveQuestion"
          @deleteQuestion="deleteQuestion"
          :showAnswerFlag="showAnswerFlag"
        />

        <QuizAnswers
          v-if="showAnswerFlag && quizType !== 'open-ended' && answers.length > 0"
          :answers="answers"
          @showAnswers="showAnswers"
        />

        <SavedQuizzes
          v-if="showSavedQuizzes"
          :savedQuizzes="savedQuizzes"
          @loadQuiz="loadQuiz"
          @deleteQuiz="deleteQuiz"
          @close="showSavedQuizzes = false"
        />
      </div>
    </div>
  </div>
</template>

<script>
import QuizForm from './QuizForm.vue';
import QuizQuestions from './QuizQuestions.vue';
import QuizAnswers from './QuizAnswers.vue';
import SavedQuizzes from './SavedQuizzes.vue';

export default {
  components: { QuizForm, QuizQuestions, QuizAnswers, SavedQuizzes },
  data() {
    return {
      context: '',
      quizType: 'true-false',
      quizLanguage: 'English',
      numQuestions: 3,
      questions: [],
      answers: [],
      alternatives: [],
      showAnswerFlag: false,
      userAnswers: {},
      evaluations: {},
      file: null,
      fileName: '',
      savedQuizzes: [],
      showSavedQuizzes: false,
      isLoading: false,
      editMode: false,
      editingIndex: null,
    };
  },
  watch: {
    quizType(newType, oldType) {
      if (newType !== oldType) {
        this.questions = [];
        this.answers = [];
        this.alternatives = [];
        this.userAnswers = {};
        this.evaluations = {};
        this.showAnswerFlag = false;
        this.editMode = false;
        this.editingIndex = null;
      }
    },
  },
  mounted() {
    this.loadSavedQuizzes();
  },
  methods: {
    async generateQuiz() {
      this.isLoading = true;
      this.showAnswerFlag = false;
      this.userAnswers = {};
      this.evaluations = {};
      this.alternatives = [];
      this.editMode = false;
      this.editingIndex = null;

      try {
        const formData = new FormData();
        formData.append('context', this.context);
        formData.append('quiz_type', this.quizType);
        formData.append('num_questions', this.numQuestions);
        formData.append('quiz_language', this.quizLanguage);
        if (this.file) {
          formData.append('file', this.file);
        }

        const response = await fetch('http://localhost:5000/generate-quiz', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
          alert(`Error from backend: ${data.error}`);
          return;
        }

        this.questions = data.questions || [];
        this.answers = data.answers || data.reference_answers || [];
        if (this.quizType === 'multiple-choice') {
          this.alternatives = data.alternatives || [];
        }
      } catch (error) {
        console.error('Error generating quiz:', error);
        alert('Failed to generate quiz. Check the console for details.');
      } finally {
        this.isLoading = false;
      }
    },
    async evaluateAnswers() {
      try {
        const response = await fetch('http://localhost:5000/evaluate-answers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            questions: this.questions,
            user_answers: this.userAnswers,
            reference_answers: this.quizType === 'open-ended' ? this.answers : [],
            context: this.context,
            quiz_language: this.quizLanguage,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
          alert(`Error from backend: ${data.error}`);
          return;
        }

        this.evaluations = data.evaluations || {};
      } catch (error) {
        console.error('Error evaluating answers:', error);
        alert('Failed to evaluate answers. Check the console for details.');
      }
    },
    showAnswers() {
      this.showAnswerFlag = true;
    },
    selectAnswer(index, value) {
      this.$set(this.userAnswers, index, value);
    },
    saveQuiz() {
      const quizData = {
        id: Date.now(),
        context: this.context,
        quizType: this.quizType,
        quizLanguage: this.quizLanguage,
        numQuestions: this.numQuestions,
        questions: this.questions,
        answers: this.answers,
        alternatives: this.alternatives,
        createdAt: new Date().toISOString(),
      };
      this.savedQuizzes.push(quizData);
      localStorage.setItem('savedQuizzes', JSON.stringify(this.savedQuizzes));
      alert('Quiz saved successfully!');
    },
    loadSavedQuizzes() {
      const quizzes = localStorage.getItem('savedQuizzes');
      if (quizzes) {
        this.savedQuizzes = JSON.parse(quizzes);
      }
    },
    loadQuiz(quiz) {
      this.context = quiz.context;
      this.quizType = quiz.quizType;
      this.quizLanguage = quiz.quizLanguage;
      this.numQuestions = quiz.numQuestions;
      this.questions = quiz.questions;
      this.answers = quiz.answers;
      this.alternatives = quiz.alternatives;
      this.userAnswers = {};
      this.evaluations = {};
      this.showAnswerFlag = false;
      this.showSavedQuizzes = false;
      this.editMode = false;
      this.editingIndex = null;
    },
    deleteQuiz(quizId) {
      this.savedQuizzes = this.savedQuizzes.filter((quiz) => quiz.id !== quizId);
      localStorage.setItem('savedQuizzes', JSON.stringify(this.savedQuizzes));
    },
    handleSaveQuestion({ index, data }) {
      if (index === -1) {
        this.questions.push(data.question);
        if (this.quizType === 'multiple-choice') {
          this.alternatives.push(data.alternatives);
          this.answers.push(data.answer);
        } else if (this.quizType === 'true-false') {
          this.answers.push(data.answer);
        } else {
          this.answers.push(data.referenceAnswer);
        }
      } else {
        this.questions[index] = data.question;
        if (this.quizType === 'multiple-choice') {
          this.alternatives[index] = data.alternatives;
          this.answers[index] = data.answer;
        } else if (this.quizType === 'true-false') {
          this.answers[index] = data.answer;
        } else {
          this.answers[index] = data.referenceAnswer;
        }
      }
      this.userAnswers = {};
      this.evaluations = {};
      this.showAnswerFlag = false;
      this.editingIndex = null;
    },
    deleteQuestion(index) {
      this.questions.splice(index, 1);
      if (this.quizType === 'multiple-choice') {
        this.alternatives.splice(index, 1);
      }
      this.answers.splice(index, 1);
      this.userAnswers = {};
      this.evaluations = {};
      this.showAnswerFlag = false;
    },
  },
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
.btn-shadow {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
}
.btn-shadow:hover {
  box-shadow: 0 7px 14px rgba(0, 0, 0, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
}
.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>