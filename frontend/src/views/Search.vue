<template>
    <div class="search-page">
      <div class="container">
        <div class="search-header">
          <div class="category-menu">
            <template v-if="loadingCategories">
              <div
                v-for="n in 4"
                :key="`category-skeleton-${n}`"
                class="category-btn skeleton"
              >
              </div>
            </template>
            <template v-else>
              <button
                @click="categoryHandlers.select(null)"
                :class="['category-btn', { active: !currentCategory }]"
              >
                All
              </button>
              <button
                v-for="category in categories"
                :key="category.id"
                @click="categoryHandlers.select(category.id)"
                :class="['category-btn', { active: currentCategory === category.id }]"
              >
                {{ category.name }}
              </button>
            </template>
          </div>
          <div class="sort-dropdown">
            <button
              class="sort-button"
              @click="dropdownHandlers.toggle"
              @keydown.enter="dropdownHandlers.toggle"
              @keydown.space.prevent="dropdownHandlers.toggle"
              :aria-expanded="isSortDropdownOpen.toString()"
              aria-controls="sort-options"
            >
              <span>{{ currentSort === 'relevant' ? 'Most Relevant' : 'Most Recent' }}</span>
              <svg
                width="12"
                height="12"
                viewBox="0 0 12 12"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M2.5 4.5L6 8L9.5 4.5"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>
            <div class="sort-options" v-show="isSortDropdownOpen" id="sort-options">
              <button
                class="sort-option"
                :class="{ active: currentSort === 'relevant' }"
                @click="dropdownHandlers.select('relevant')"
                @keydown.enter="dropdownHandlers.select('relevant')"
                @keydown.space.prevent="dropdownHandlers.select('relevant')"
              >
                Most Relevant
              </button>
              <button
                class="sort-option"
                :class="{ active: currentSort === 'recent' }"
                @click="dropdownHandlers.select('recent')"
                @keydown.enter="dropdownHandlers.select('recent')"
                @keydown.space.prevent="dropdownHandlers.select('recent')"
              >
                Most Recent
              </button>
            </div>
          </div>
        </div>
  
        <div v-if="error" class="error-state">
          {{ error }}
        </div>
        <div v-else-if="loadingSearch" class="search-content">
          <div
            v-for="n in 6"
            :key="`skeleton-${n}`"
            class="document-card skeleton"
          >
            <div class="document-preview skeleton-preview"></div>
            <div class="document-info">
              <div class="skeleton-title"></div>
              <div class="skeleton-type"></div>
              <div class="skeleton-rating"></div>
            </div>
          </div>
        </div>
        <div v-else-if="!searchQuery" class="search-content empty-state">
          <div>Search here...</div>
        </div>
        <div v-else-if="searchResults.length === 0" class="empty-state">
          No results found for "{{ searchQuery }}"
        </div>
        <div v-else class="search-content">
          <div
            v-for="post in searchResults"
            :key="post.id"
            class="document-card"
            @click="navigateToPost(post.id)"
            role="button"
            tabindex="0"
            @keydown.enter="navigateToPost(post.id)"
            @keydown.space.prevent="navigateToPost(post.id)"
            :aria-label="`Open post: ${post.title}`"
          >
            <div class="document-preview">
              <img
                :src="getDocumentPreviewImage(post)"
                alt="Document preview"
                class="preview-image"
              >
            </div>
            <div class="document-info">
              <h3 class="document-title">{{ post.title }}</h3>
              <p class="document-type">{{ post.category.name }}</p>
              <p class="document-date">
                <DateIcon/>
                {{ formatDate(post.created_at) }}
            </p>
            </div>
            <div class="document-rating">
              <span class="rating-percentage">
                <LikeIcon class="like-icon" />
                {{ Math.round(post.rating_percentage) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getDocumentPreviewImage, formatDate } from '@/utils/utils';
import { LikeIcon, DateIcon } from '@/components/icons';
import { searchPosts } from '@/services/postService';
import { fetchCategories } from '@/services/categoryService';

// Router and route setup
const router = useRouter();
const route = useRoute();

// State management
const searchQuery = ref('');
const searchResults = ref([]);
const categories = ref([]);
const currentCategory = ref(null);
const currentSort = ref('relevant');
const loadingCategories = ref(false);
const loadingSearch = ref(false);
const isSortDropdownOpen = ref(false);
const error = ref(null);

// Debounce setup
const searchTimeout = ref(null);

// Dropdown handlers
const dropdownHandlers = {
  toggle: () => {
    isSortDropdownOpen.value = !isSortDropdownOpen.value;
  },
  close: () => {
    isSortDropdownOpen.value = false;
  },
  select: (sortValue) => {
    currentSort.value = sortValue;
    dropdownHandlers.close();
    handleSortChange();
  }
};

// Search handlers
const searchHandlers = {
  handle: () => {
    if (searchTimeout.value) {
      clearTimeout(searchTimeout.value);
    }
    
    if (searchQuery.value.trim()) {
      searchTimeout.value = setTimeout(() => {
        updateSearchQuery();
      }, 300);
    } else {
      router.push('/search');
      searchResults.value = [];
      error.value = null;
    }
  },
  
  perform: async () => {
    if (!searchQuery.value.trim()) return;
    
    loadingSearch.value = true;
    error.value = null;
    try {
      const results = await searchPosts(
        searchQuery.value,
        currentCategory.value,
        currentSort.value
      );
      searchResults.value = results || [];
    } catch (error) {
      console.error('Search failed:', error);
      error.value = 'Failed to load search results. Please try again.';
      searchResults.value = [];
    } finally {
      loadingSearch.value = false;
    }
  }
};

// Category handlers
const categoryHandlers = {
  select: (categoryId) => {
    currentCategory.value = categoryId;
    if (searchQuery.value.trim()) {
      updateSearchQuery();
    }
  }
};

// Sort handlers
const handleSortChange = () => {
  if (searchQuery.value.trim()) {
    updateSearchQuery();
  }
};

// Navigation handlers
const navigateToPost = (postId) => {
  router.push(`/post/${postId}`);
};

// Helper functions
const updateSearchQuery = () => {
  const query = {
    q: searchQuery.value.trim(),
    sort: currentSort.value
  };
  
  if (currentCategory.value) {
    query.category_id = currentCategory.value;
  }
  
  router.push({
    path: '/search',
    query
  });
};

// Data loading
const loadCategories = async () => {
  loadingCategories.value = true;
  try {
    const fetchedCategories = await fetchCategories();
    categories.value = fetchedCategories || [];
  } catch (err) {
    console.error('Failed to load categories:', err);
    error.value = 'Failed to load categories. Please try again.';
  } finally {
    loadingCategories.value = false;
  }
};

// Watchers
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery;
    searchHandlers.perform();
  } else {
    searchQuery.value = '';
    searchResults.value = [];
    error.value = null;
  }
}, { immediate: true });

watch(() => route.query.category_id, (newCategoryId) => {
  currentCategory.value = newCategoryId ? parseInt(newCategoryId) : null;
  if (searchQuery.value.trim()) {
    searchHandlers.perform();
  }
}, { immediate: true });

watch(() => route.query.sort, (newSort) => {
  currentSort.value = newSort || 'relevant';
  if (searchQuery.value.trim()) {
    searchHandlers.perform();
  }
}, { immediate: true });

// Lifecycle hooks
onMounted(async () => {
  await loadCategories();
});
</script>

<style scoped>
.search-page {
    background-color: white;
    min-height: calc(100vh - 72px);
    width: 100%;
    padding: 32px 0;
}

.container {
    width: 100%;
    max-width: 1170px;
    margin: 0 auto;
    padding: 0 24px;
}

.search-header {
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-bottom: 32px;
}

.category-menu {
    display: flex;
    align-items: center;
    gap: 8px;
}
.category-btn {
    display: flex;
    align-items: center;
    background-color: #fff;
    border-radius: 40px;
    border: 1px solid var(--border-color);
    height: 40px;
    font-size: 16px;
    padding: 8px 16px;
    transition: all 0.2s ease;
}
.category-btn:hover {
    border-color: var(--primary-color);
}
.category-btn.active {
    background-color: var(--primary-color);
    color: #fff;
    border: 1px solid transparent;
}

.search-content {
    display: grid;
    grid-template-columns: 1fr;
}

.document-card {
  display: flex;
  padding: 16px;
  gap: 16px;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.1s;
}
.document-card:hover {
  background: #0099ff10;
}
.document-preview {
    display: flex;
    height: 96px;
    width: auto;
    aspect-ratio: 116/96;
    background-color: #e6ebef;
    border-radius: 12px;
    flex-shrink: 0;
    padding: 8px;
    overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  object-fit: cover;
}

.document-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
}

.document-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--primary-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-author, .document-type {
  font-size: 14px;
  font-weight: 500;
  color: #9EA9B5;
}

.document-date {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: #4C5966;
}

.document-rating {
  display: flex;
  align-items: flex-start;
}

.rating-percentage {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 4px;
    height: 24px;
    font-size: 14px;
    font-weight: 600;
}
.like-icon {
  width: 16px;
  height: 16px;
  color: var(--primary-color);
}

.loading-state,
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 200px;
}

/* Skeleton Loader Styles */
.skeleton {
    cursor: default;
    animation: skeleton-loading 1.5s infinite;
}
.skeleton:hover{
    background: none;
}

.skeleton-preview {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

.skeleton-title {
    height: 20px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 8px;
}

.skeleton-type {
    height: 16px;
    width: 60%;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 12px;
}

.skeleton-rating {
    height: 24px;
    width: 40%;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 12px;
}

@keyframes skeleton-loading {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

.sort-dropdown {
    position: relative;
    max-width: fit-content;
    display: flex;
}

.sort-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    height: 40px;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    font-size: 16px;
    color: var(--text-color);
    background-color: white;
    cursor: pointer;
    transition: all 0.2s ease;
}

.sort-button:hover {
    border-color: var(--primary-color);
}

.sort-button.active {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.sort-button svg {
    transition: transform 0.2s ease;
}

.sort-button.active svg {
    transform: rotate(180deg);
}

.sort-options {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 200px;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 10;
    overflow: hidden;
}

.sort-option {
    display: block;
    width: 100%;
    padding: 12px 16px;
    text-align: left;
    border: none;
    background: none;
    font-size: 16px;
    color: var(--text-color);
    cursor: pointer;
    transition: all 0.2s ease;
}

.sort-option:hover {
    background-color: #f5f7f9;
}

.sort-option.active {
    color: var(--primary-color);
    background-color: #f5f7f9;
}

/* Category Skeleton Styles */
.category-btn.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    cursor: default;
    pointer-events: none;
}
.category-btn.skeleton:nth-child(even) {
    width: 72px;
}
.category-btn.skeleton:nth-child(odd){
    width: 102px;
}
.category-btn.skeleton:first-child{
    width: 52px;
}
</style>