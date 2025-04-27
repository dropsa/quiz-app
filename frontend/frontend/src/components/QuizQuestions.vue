<template>
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
              @click="$emit('selectAnswer', index, true)"
              :class="{
                'bg-blue-500 text-white': userAnswers[index] === true,
                'bg-gray-200 text-gray-700': userAnswers[index] !== true,
              }"
              class="px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold"
            >
              True
            </button>
            <button
              @click="$emit('selectAnswer', index, false)"
              :class="{
                'bg-blue-500 text-white': userAnswers[index] === false,
                'bg-gray-200 text-gray-700': userAnswers[index] !== false,
              }"
              class="px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold"
            >
              False
            </button>
          </div>
          <div v-else-if="quizType === 'multiple-choice'" class="space-y-2">
            <div v-for="(option, optIndex) in alternatives[index]" :key="optIndex" class="flex justify-center">
              <button
                @click="$emit('selectAnswer', index, option[0])"
                :class="{
                  'bg-blue-500 text-white': userAnswers[index] === option[0],
                  'bg-gray-200 text-gray-700': userAnswers[index] !== option[0],
                }"
                class="w-full px-4 py-2 rounded-lg hover:bg-blue-400 transition font-semibold text-left"
              >
                {{ option }}
              </button>
            </div>
          </div>
          <div v-else-if="quizType === 'open-ended'" class="space-y-2">
            <textarea
              v-model="localUserAnswers[index]"
              rows="4"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              placeholder="Type your answer here"
              @input="$emit('update:userAnswers', { ...localUserAnswers })"
            ></textarea>
            <div v-if="evaluations[index]" class="mt-4 p-4 rounded-lg bg-gray-100">
              <h3 class="text-lg font-semibold mb-2">Feedback</h3>
              <p class="text-gray-700">{{ evaluations[index].feedback }}</p>
              <div class="mt-2">
                <span class="font-bold">Evaluation:</span>
                <span :class="getEvaluationClass(evaluations[index].is_correct)">{{
                  evaluations[index].is_correct
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      questions: Array,
      quizType: String,
      alternatives: Array,
      userAnswers: Object,
      evaluations: Object,
      showAnswerFlag: Boolean,
      answers: Array,
    },
    emits: ['selectAnswer', 'update:userAnswers'],
    computed: {
      localUserAnswers: {
        get() {
          return this.userAnswers;
        },
        set(value) {
          this.$emit('update:userAnswers', value);
        },
      },
    },
    methods: {
      isCorrect(index) {
        if (this.quizType === 'open-ended') {
          return (
            this.evaluations[index]?.is_correct === 'true' ||
            this.evaluations[index]?.is_correct === 'partially_correct'
          );
        }
        if (this.userAnswers[index] === undefined || this.answers[index] === undefined) {
          return false;
        }
        if (this.quizType === 'true-false') {
          const backendAnswer = this.answers[index].toLowerCase() === 'true';
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