<template>
  <aside class="sidebar">
    <div class="sidebar__header">
      <div class="user-card">
        <img class="sidebar__avatar" src="/avatar.png" alt="User Avatar" />
        <div class="sidebar__info">
          <RouterLink
            v-if="authStore.isAuthenticated"
            :to="'/'+user.username"
            class="sidebar__name"
          >
            {{ profile.full_name }}
          </RouterLink>
          <p v-else class="sidebar__name">{{ profile.full_name }}</p>
          <p class="sidebar__email">{{ profile.email }}</p>
        </div>
      </div>
      <div class="user-stats">
        <div class="stat-item">
          <span class="stat__value">{{ profile.followers_count}}</span>
          <span class="stat__label">Followers</span>
        </div>
        <div class="stat-item">
          <span class="stat__value">{{ profile.uploads_count}}</span>
          <span class="stat__label">Uploads</span>
        </div>
        <div class="stat-item">
          <span class="stat__value">{{ profile.upvotes_count}}</span>
          <span class="stat__label">Upvotes</span>
        </div>
      </div>
      <div class="toolbar">
        <button class="btn upload-btn" @click="$router.push('/upload')">
          <PlusIcon class="sidebar__icon"/>
          <span>New</span>
        </button>
      </div>
    </div>

    <nav class="sidebar__nav">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="sidebar__link"
        :class="{ active: isActive(item.to) }"
      >
        <component :is="item.icon" class="sidebar__icon" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { RouterLink, useRoute } from 'vue-router';
import { computed, ref, watch, onMounted } from 'vue';
import { PlusIcon, HomeIcon, LibraryIcon, ExploreIcon } from '@/components/icons';
import { useAuthStore } from '@/store/authStore';
import { fetchProfile } from '@/services/userService';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

const profile = ref({
  full_name: 'Guest',
  email: 'Not logged in',
  followers_count: 0,
  uploads_count: 0,
  upvotes_count: 0
});

// Fetch profile function
const loadProfile = async () => {
  const profileData = await fetchProfile();
  if (profileData) {
    profile.value = profileData;
  }
};

// Fetch on mount if already authenticated
onMounted(() => {
  if (isAuthenticated.value) {
    loadProfile();
  }
});

// Also watch for auth changes (e.g. logging in)
watch(isAuthenticated, async (newValue) => {
  if (newValue) {
    await loadProfile();
  } else {
    profile.value = {
      full_name: 'Guest',
      email: 'Not logged in',
      followers_count: 0,
      uploads_count: 0,
      upvotes_count: 0
    };
  }
});

const route = useRoute();
const isActive = (path) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};

const navItems = [
  { to: '/', label: 'Home', icon: HomeIcon },
  { to: '/library', label: 'My Library', icon: LibraryIcon },
  { to: '/explore', label: 'Explore', icon: ExploreIcon }
];

const onUploadClick = () => {
  // Upload logic here
};
</script>

<style scoped>
.sidebar {
  position: sticky;
  width: 300px;
  top: 72px;
  background: #fff;
  color: var(--text-color);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 72px);
  padding: 32px 24px;
}

.sidebar__header {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.sidebar__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.sidebar__info {
  flex: 1;
}

.sidebar__name {
  color: var(--text-color);
  font-weight: 600;
  font-size: 16px;
}

.sidebar__email {
  font-size: 13px;
  color: #6b7280;
}

.user-stats {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px;
  overflow: hidden;
  color: #0a0a0a;
  text-align: center;
  text-transform: capitalize;
  border-radius: 12px;
  transition: opacity .3s ease-in-out;
}

.stat__label {
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  width: 100%;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 400;
  line-height: 125%;
  color: var(--text-color-light);
}

.stat__value {
  font-size: 16px;
  font-weight: 600;
  line-height: 125%;
  color: var(--text-color);
}

.upload-btn {
  background-color: var(--primary-color);
  color: #ffffff;
  width: 100%;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 40px;
  padding: 8px 20px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s, transform 0.2s;
}

.sidebar__nav {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.sidebar__link:hover {
  background-color: #f3f4f6;
}

.sidebar__link.active {
  background-color: var(--primary-color-10);
  color: var(--primary-color);
}

.sidebar__icon {
  width: 20px;
  height: 20px;
}

.toolbar {
  display: flex;
  width: 100%;
}
</style>
