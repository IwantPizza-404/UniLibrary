<template>
  <header class="header">
    <div class="header-content">
      <!-- Logo Section -->
      <div class="logo-section">
        <router-link to="/">
          <Logo />
        </router-link>
      </div>

      <!-- Search Bar Section -->
      <div class="search-bar">
        <input
          type="text"
          placeholder="Search for documents, notes, or files"
          class="search-input"
        />
        <ul class="nav-links">
          <li>
            <router-link to="/about" class="nav-link">About</router-link>
          </li>
          <li>
            <router-link to="/help" class="nav-link">Help</router-link>
          </li>
        </ul>
      </div>

      <!-- Actions Section -->
      <div class="actions">
        <!-- Show user profile if authenticated -->
        <div v-if="isAuthenticated" @click="toggleDropdown" class="user-menu">
          <div class="profile-img">
            <img src="/avatar.png" alt="User" />
          </div>
          <div class="dropdown">
            <button class="dropdown-btn">
              <svg
                width="12"
                height="12"
                viewBox="0 0 12 12"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9.96004 4.475L6.70004 7.735C6.31504 8.12 5.68504 8.12 5.30004 7.735L2.04004 4.475"
                  stroke="#5F6265"
                  stroke-width="1.5"
                  stroke-miterlimit="10"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>
            <ul v-if="isDropdownOpen" class="dropdown-menu">
              <li @click="$router.push('/'+user.username)">
                Profile
                <UserIcon/>
              </li>
              <li @click="handleLogout">
                Logout
                <LogoutIcon/>
              </li>
            </ul>
          </div>
        </div>

        <!-- Show "Sign in" button if not authenticated -->
        <router-link v-else class="signin-btn" to="/login">Sign in</router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/store/authStore.js';
import Logo from '@/assets/images/logo.vue';
import { UserIcon, LogoutIcon } from '@/components/icons';

// Access the authentication store
const authStore = useAuthStore();

// Computed properties for authentication state
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

// Dropdown state
const isDropdownOpen = ref(false);

// Toggle dropdown visibility
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

// Handle logout action
const handleLogout = () => {
  authStore.logout();
  isDropdownOpen.value = false;
};
</script>

<style scoped>
/* Header container */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #ffffff; /* White background */
  border-bottom: 1px solid var(--border-color); /* Light gray border */
  height: 72px; /* Fixed height */
  display: flex;
  align-items: center;
  padding: 16px 32px;
  flex-shrink: 0; /* Prevent shrinking */
}

/* Header content */
.header-content {
  display: grid;
  grid-template-columns: 268px 1fr auto; /* Logo, search bar, actions */
  align-items: center;
  width: 100%;
}

/* Logo section */
.logo-section {
  display: flex;
  align-items: center;
}
.logo-section a {
  display: inline-flex;
}

/* Search bar */
.search-bar {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-input {
  max-width: 480px;
  width: 100%;
  height: 40px;
  padding: 8px 16px;
  border: 1px solid var(--border-color); /* Light gray border */
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: var(--primary-color); /* Blue border on focus */
}

/* Navigation links */
.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  display: inline-flex;
  text-decoration: none;
  border-radius: 20px;
  color: #4C5966;
  transition: color 0.2s;
  padding: 8px 20px;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background: var(--primary-color-10);
}

/* Actions section */
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  cursor: pointer;
}

.profile-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.profile-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown {
  position: relative;
}

.dropdown-btn {
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 16px);
  right: 0;
  min-width: 165px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  list-style: none;
  padding: 8px 0;
  margin: 0;
  z-index: 20;
}

.dropdown-menu li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-menu li:hover {
  color: var(--primary-color);
  background-color: var(--primary-color-10);
}

.signin-btn {
  background-color: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 16px;
  font-weight: 500;
  line-height: 24px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.signin-btn:hover {
  background-color: #2563eb; /* Darker blue */
}
</style>