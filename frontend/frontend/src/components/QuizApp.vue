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

        <!-- Buttons -->
        <div class="flex space-x-4">
          <button
            @click="generateQuiz"
            class="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            Generate Quiz
          </button>
          <button
            @click="showAnswers"
            class="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition font-semibold"
          >
            Show Answers
          </button>
          <button
            v-if="quizType === 'open-ended' && questions.length > 0"
            @click="evaluateAnswers"
            class="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition font-semibold"
          >
            Evaluate Answers
          </button>
        </div>

        <QuizQuestions
          :questions="questions"
          :quizType="quizType"
          :alternatives="alternatives"
          :userAnswers="userAnswers"
          :evaluations="evaluations"
          :answers="answers"
          @selectAnswer="selectAnswer"
          @update:userAnswers="userAnswers = $event"
          :showAnswerFlag="showAnswerFlag"
        />

        <QuizAnswers
          v-if="showAnswerFlag && quizType !== 'open-ended' && answers.length > 0"
          :answers="answers"
          @showAnswers="showAnswers"
        />
      </div>
    </div>
  </div>
</template>

<script>
import QuizForm from './QuizForm.vue';
import QuizQuestions from './QuizQuestions.vue';
import QuizAnswers from './QuizAnswers.vue';

export default {
  components: { QuizForm, QuizQuestions, QuizAnswers },
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
    };
  },
  methods: {
    async generateQuiz() {
      this.showAnswerFlag = false;
      this.userAnswers = {};
      this.evaluations = {};
      this.alternatives = [];

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
  },
};
</script>