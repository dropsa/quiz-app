import Vue from 'vue'
import VueRouter from 'vue-router'
import QuizApp from '@/components/QuizApp.vue';

Vue.use(VueRouter)

const routes = [
  {
    path: '/quizapp',
    name: 'QuizApp',
    component: QuizApp
  }
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
