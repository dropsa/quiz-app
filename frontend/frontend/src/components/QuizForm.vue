<template>
    <div class="space-y-6">
      <!-- Context Textarea -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Quiz Context</label>
        <textarea
          :value="context"
          @input="$emit('update:context', $event.target.value)"
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
          :value="quizLanguage"
          @change="$emit('update:quizLanguage', $event.target.value)"
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
          :value="quizType"
          @change="$emit('update:quizType', $event.target.value)"
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
          :value="numQuestions"
          @input="$emit('update:numQuestions', Number($event.target.value))"
          min="1"
          max="5"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
        />
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      context: String,
      quizType: String,
      quizLanguage: String,
      numQuestions: Number,
      file: File,
      fileName: String,
    },
    emits: ['update:context', 'update:quizType', 'update:quizLanguage', 'update:numQuestions', 'update:file', 'update:fileName'],
    methods: {
      handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
  
        this.$emit('update:fileName', file.name);
        this.$emit('update:file', file);
      },
    },
  };
  </script>