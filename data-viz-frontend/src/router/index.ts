// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../pages/Home.vue'; // New Home component
import LiveData from '../pages/LiveData.vue'; // The new page component

const routes = [
  { path: '/', component: Home }, // Home page route
  { path: '/new-page', component: LiveData }, // New page route
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
