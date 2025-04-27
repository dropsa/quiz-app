<template>
    <div class="mt-8">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Answers</h2>
      <hr class="border-gray-300 mb-4" />
      <pre class="bg-gray-50 p-4 rounded-lg text-gray-700">{{ answers }}</pre>
      <button
        @click="$emit('showAnswers')"
        class="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 transition font-semibold"
      >
        Show Answers
      </button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      answers: Array,
    },
    emits: ['showAnswers'],
  };
  </script>