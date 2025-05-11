import { createApp } from 'vue';
import { createPinia } from 'pinia'; // Import Pinia
import App from './App.vue';
import router from './router';
import { useAuthStore } from './store/authStore'; // Import the auth store
import './assets/styles/main.css'; // Global styles
import './assets/styles/tailwind.css'; // Tailwind CSS styles

const app = createApp(App);

// Create and use Pinia
const pinia = createPinia();
app.use(pinia);

const authStore = useAuthStore();

// Check authentication before mounting the app
authStore.checkAuth().then(() => {
  app.use(router);
  app.mount('#app');
});