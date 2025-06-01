<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>Welcome Back</h1>
        <p class="subtitle">Please enter your credentials to continue</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
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
          <span v-if="isLoading" class="loading-text">
            <span class="loading-spinner"></span>
            <!-- Logging in... -->
          </span>
          <span v-else>Sign In</span>
        </button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 24px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.btn-primary {
  width: 100%;
  height: 48px;
  padding: 14px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.error {
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #fee2e2;
  color: #ef4444;
  border-radius: 12px;
  font-size: 14px;
  text-align: center;
  animation: shake 0.5s ease-in-out;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .login-container {
    padding: 32px 24px;
  }

  .login-header h1 {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }
}
</style>