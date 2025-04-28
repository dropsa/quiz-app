<template>
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Saved Quizzes</h2>
        <div v-if="savedQuizzes.length === 0" class="text-gray-600">
          No saved quizzes found.
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="quiz in savedQuizzes"
            :key="quiz.id"
            class="p-4 bg-gray-50 rounded-lg flex justify-between items-center"
          >
            <div>
              <p class="text-gray-700 font-semibold">
                {{ quiz.context || 'Untitled Quiz' }}
              </p>
              <p class="text-sm text-gray-500">
                Created: {{ new Date(quiz.createdAt).toLocaleString() }}
              </p>
              <p class="text-sm text-gray-500">
                Type: {{ quiz.quizType }} | Questions: {{ quiz.numQuestions }}
              </p>
            </div>
            <div class="flex space-x-2">
              <button
                @click="$emit('loadQuiz', quiz)"
                class="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Load
              </button>
              <button
                @click="$emit('deleteQuiz', quiz.id)"
                class="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="mt-6 w-full bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition"
        >
          Close
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      savedQuizzes: Array,
    },
    emits: ['loadQuiz', 'deleteQuiz', 'close'],
  };
  </script>