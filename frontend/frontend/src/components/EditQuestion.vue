<template>
    <div class="mt-4 p-4 bg-gray-100 rounded-lg">
      <input
        v-model="localQuestion"
        placeholder="Enter question"
        class="w-full px-4 py-2 mb-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
      />
      <div v-if="quizType === 'multiple-choice'">
        <div v-for="(option, index) in localAlternatives" :key="index" class="flex items-center mb-2">
          <input
            v-model="localAlternatives[index]"
            :placeholder="'Option ' + (index + 1)"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select v-model="localAnswer" class="w-full px-4 py-2 mb-2 border border-gray-300 rounded-lg">
          <option v-for="(option, index) in localAlternatives" :value="option" :key="index">
            {{ option }}
          </option>
        </select>
      </div>
      <div v-else-if="quizType === 'true-false'">
        <select v-model="localAnswer" class="w-full px-4 py-2 mb-2 border border-gray-300 rounded-lg">
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      </div>
      <div v-else>
        <textarea
          v-model="localReferenceAnswer"
          rows="4"
          placeholder="Enter reference answer"
          class="w-full px-4 py-2 mb-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>
      <button @click="save" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
        Save
      </button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      quizType: String,
      question: String,
      alternatives: Array,
      answer: String,
      referenceAnswer: String,
    },
    data() {
      return {
        localQuestion: this.question || '',
        localAlternatives: this.alternatives ? [...this.alternatives] : ['', '', '', ''],
        localAnswer: this.answer || '',
        localReferenceAnswer: this.referenceAnswer || '',
      };
    },
    methods: {
      save() {
        this.$emit('save', {
          question: this.localQuestion,
          alternatives: this.quizType === 'multiple-choice' ? this.localAlternatives : [],
          answer: this.quizType !== 'open-ended' ? this.localAnswer : '',
          referenceAnswer: this.quizType === 'open-ended' ? this.localReferenceAnswer : '',
        });
      },
    },
  };
  </script>