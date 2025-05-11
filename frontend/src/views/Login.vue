<template>
  <div class="login-page">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <FormInput
        id="username"
        label="Username"
        type="text"
        v-model="username"
        placeholder="Enter your username"
        required
      />
      <FormInput
        id="password"
        label="Password"
        type="password"
        v-model="password"
        placeholder="Enter your password"
        required
      />
      <button type="submit" class="btn-primary" :disabled="isLoading">
        <span v-if="isLoading">Logging in...</span>
        <span v-else>Login</span>
      </button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authStore.js';
import FormInput from '@/components/common/FormInput.vue';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

const handleLogin = async () => {
  errorMessage.value = ''; // Clear previous errors
  isLoading.value = true; // Set loading state

  try {
    // Call the login action from the auth store
    await authStore.login(username.value, password.value);

    // Redirect to the home page or dashboard
    router.push('/');
  } catch (error) {
    // Handle login errors
    errorMessage.value = error.response?.data?.message || 'Invalid username or password';
  } finally {
    isLoading.value = false; // Reset loading state
  }
};
</script>

<style scoped>
.login-page {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error {
  color: red;
  margin-top: 1rem;
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  background-color: #369f6e;
}
</style>