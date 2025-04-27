<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-2xl bg-white rounded-xl shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">Quiz App Laura</h1>
      <p class="text-gray-600 mb-8 text-center">Generate a quiz based on your context</p>

      <div class="space-y-6">
        <!-- Context Textarea -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Quiz Context</label>
          <textarea
            v-model="context"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
            placeholder="Enter the context for the quiz"
          ></textarea>
        </div>

        <!-- File Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload Context File (Optional)</label>
          <input
            type="file"
            @change="handleFileUpload"
            accept=".txt,.pdf"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          />
          <p v-if="fileName" class="text-sm text-gray-600 mt-2">Selected file: {{ fileName }}</p>
        </div>

        <!-- Quiz Language Select -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Quiz Language</label>
          <select
            v-model="quizLanguage"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          >
            <option value="English">English</option>
            <option value="Hungarian">Hungarian</option>
          </select>
        </div>

        <!-- Quiz Type Select -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Quiz Type</label>
          <select
            v-model="quizType"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          >
            <option value="multiple-choice">Multiple Choice</option>
            <option value="true-false">True/False</option>
            <option value="open-ended">Open-Ended</option>
          </select>
        </div>

        <!-- Number of Questions -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
          <input
            type="number"
            v-model.number="numQuestions"
            min="1"
            max="5"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
          />
        </div>

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

        <!-- Questions Display -->
        <div v-if="questions.length > 0" class="mt-8">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Questions</h2>
          <div class="space-y-4">
            <div
              v-for="(question, index) in questions"
              :key="index"
              class="p-4 rounded-lg transition-colors"
              :class="getQuestionBgClass(index)"
            >
              <p class="text-gray-700 mb-4">{{ question }}</p>
              <div v-if="quizType === 'true-false'" class="flex justify-center space-x-2">
                <button
                  @click="selectAnswer(index, true)"
                  :class="{
                    'bg-blue-500 text-white': userAnswers[index] === true,
                    'bg-gray-200 text-gray-700': userAnswers[index] !== true
                  }"
                  class="px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold"
                >
                  True
                </button>
                <button
                  @click="selectAnswer(index, false)"
                  :class="{
                    'bg-blue-500 text-white': userAnswers[index] === false,
                    'bg-gray-200 text-gray-700': userAnswers[index] !== false
                  }"
                  class="px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold"
                >
                  False
                </button>
              </div>
              <div v-else-if="quizType === 'multiple-choice'" class="space-y-2">
                <div v-for="(option, optIndex) in alternatives[index]" :key="optIndex" class="flex justify-center">
                  <button
                    @click="selectAnswer(index, option[0])"
                    :class="{
                      'bg-blue-500 text-white': userAnswers[index] === option[0],
                      'bg-gray-200 text-gray-700': userAnswers[index] !== option[0]
                    }"
                    class="w-full px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold text-left"
                  >
                    {{ option }}
                  </button>
                </div>
              </div>
              <div v-else-if="quizType === 'open-ended'" class="space-y-2">
                <textarea
                  v-model="userAnswers[index]"
                  rows="4"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  placeholder="Type your answer here"
                ></textarea>
                <div v-if="evaluations[index]" class="mt-4 p-4 rounded-lg bg-gray-100">
                  <h3 class="text-lg font-semibold mb-2">Feedback</h3>
                  <p class="text-gray-700">{{ evaluations[index].feedback }}</p>
                  <div class="mt-2">
                    <span class="font-bold">Evaluation:</span>
                    <span :class="getEvaluationClass(evaluations[index].is_correct)">{{ evaluations[index].is_correct }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Answers Display -->
        <div v-if="showAnswerFlag && quizType !== 'open-ended' && answers.length > 0" class="mt-8">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Answers</h2>
          <hr class="border-gray-300 mb-4" />
          <pre class="bg-gray-50 p-4 rounded-lg text-gray-700">{{ answers }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      context: "",
      quizType: "true-false",
      quizLanguage: "English",
      numQuestions: 3,
      questions: [],
      answers: [],
      alternatives: [],
      showAnswerFlag: false,
      userAnswers: {},
      evaluations: {}, // Store evaluation feedback for open-ended questions
      file: null,
      fileName: "",
    };
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.fileName = file.name;
      this.file = file;
      console.log("File selected:", this.fileName);
    },
    async generateQuiz() {
      this.showAnswerFlag = false;
      this.userAnswers = {};
      this.evaluations = {}; // Reset evaluations
      this.alternatives = [];

      try {
        const formData = new FormData();
        formData.append("context", this.context);
        formData.append("quiz_type", this.quizType);
        formData.append("num_questions", this.numQuestions);
        formData.append("quiz_language", this.quizLanguage);
        if (this.file) {
          formData.append("file", this.file);
        }

        console.log("Sending request with file:", this.fileName, "language:", this.quizLanguage);
        const response = await fetch("http://localhost:5000/generate-quiz", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Backend response:", data);

        if (data.error) {
          alert(`Error from backend: ${data.error}`);
          return;
        }

        this.questions = data.questions || [];
        this.answers = data.answers || data.reference_answers || []; // Support reference answers for open-ended
        if (this.quizType === "multiple-choice") {
          this.alternatives = data.alternatives || [];
        }
      } catch (error) {
        console.error("Error generating quiz:", error);
        alert("Failed to generate quiz. Check the console for details.");
      }
    },
    async evaluateAnswers() {
      try {
        const response = await fetch("http://localhost:5000/evaluate-answers", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            questions: this.questions,
            user_answers: this.userAnswers,
            reference_answers: this.quizType === "open-ended" ? this.answers : [],
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
        console.error("Error evaluating answers:", error);
        alert("Failed to evaluate answers. Check the console for details.");
      }
    },
    showAnswers() {
      this.showAnswerFlag = true;
    },
    selectAnswer(index, value) {
      this.$set(this.userAnswers, index, value);
    },
    isCorrect(index) {
      if (this.quizType === "open-ended") {
        return this.evaluations[index]?.is_correct === "true" || 
               this.evaluations[index]?.is_correct === "partially_correct";
      }
      if (this.userAnswers[index] === undefined || this.answers[index] === undefined) {
        return false;
      }
      if (this.quizType === "true-false") {
        const backendAnswer = this.answers[index].toLowerCase() === "true";
        return this.userAnswers[index] === backendAnswer;
      } else {
        const userAnswer = this.userAnswers[index].toLowerCase().trim();
        const backendAnswer = this.answers[index].toLowerCase().trim();
        return userAnswer === backendAnswer;
      }
    },
    getQuestionBgClass(index) {
      if (!this.showAnswerFlag) {
        return 'bg-gray-50';
      }
      if (this.quizType !== 'open-ended') {
        if (this.userAnswers[index] === undefined) {
          return 'bg-gray-50';
        } else if (this.isCorrect(index)) {
          return 'bg-green-100';
        } else {
          return 'bg-red-100';
        }
      } else {
        if (!this.evaluations[index]) {
          return 'bg-gray-50';
        } else {
          switch (this.evaluations[index].is_correct) {
            case 'true':
              return 'bg-green-100';
            case 'partially_correct':
              return 'bg-yellow-100';
            case 'false':
              return 'bg-red-100';
            default:
              return 'bg-gray-50';
          }
        }
      }
    },
    getEvaluationClass(status) {
      switch (status) {
        case 'true':
          return 'text-green-600';
        case 'false':
          return 'text-red-600';
        case 'partially_correct':
          return 'text-orange-600';
        default:
          return 'text-gray-600';
      }
    },
  },
};
</script>