<template>
  <div class="register-page">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
      <FormInput
        id="fullName"
        label="Full Name"
        type="text"
        v-model="fullName"
        placeholder="Enter your full name"
        required
      />
      <FormInput
        id="username"
        label="Username"
        type="text"
        v-model="username"
        placeholder="Enter your username"
        required
      />
      <FormInput
        id="email"
        label="Email"
        type="email"
        v-model="email"
        placeholder="Enter your email"
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
        <span v-if="isLoading">Registering...</span>
        <span v-else>Register</span>
      </button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { registerUser } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';
import FormInput from '@/components/common/FormInput.vue';

const fullName = ref('');
const username = ref('');
const email = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

const handleRegister = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await registerUser({
      full_name: fullName.value,
      username: username.value,
      email: email.value,
      password: password.value,
    });

    if (response) {
      await authStore.login(username.value, password.value);
      router.push('/');
    }
  } catch (error) {
    errorMessage.value = 'Registration failed. Please try again.';
    console.error('Registration error:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.register-page {
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

.btn-primary:hover {
  background-color: #369f6e;
}

.btn-primary:disabled {
  background-color: #a0c4a8;
  cursor: not-allowed;
}
</style>