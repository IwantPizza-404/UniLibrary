<template>
  <div class="home-page">
    <div class="main-content">
      <!-- Popular section -->
      <section class="content-section">
        <h2 class="section-title">Popular</h2>
        <div class="documents-grid">
          <div v-if="loadingPopular && !popularPosts.length" class="loading-state">
            Loading popular posts...
          </div>
          <div v-else-if="!popularPosts.length" class="empty-state">
            No popular posts found.
          </div>
          <div 
            v-else
            v-for="post in popularPosts" 
            :key="`popular-${post.id}`" 
            class="document-card"
            @click="navigateToPost(post.id)"
          >
            <div class="document-preview">
              <img :src="getDocumentPreviewImage(post)" alt="Document preview" class="preview-image">
            </div>
            <div class="document-info">
              <h3 class="document-title">{{ post.title }}</h3>
              <p class="document-author">{{ post.author.username }} {{ formatDate(post.created_at) }}</p>
              <p class="document-type">{{ post.category.name }}</p>
              <div class="document-rating">
                <span class="rating-percentage">
                  <LikeIcon class="like-icon" />
                  {{ Math.round(post.rating_percentage) }}%
                </span>
              </div>
            </div>
          </div>
          <button v-if="hasMorePopular" class="carousel-btn next-btn" @click="loadMorePopular">
            <span>›</span>
          </button>
        </div>
      </section>

      <!-- Following section -->
      <section class="content-section">
        <h2 class="section-title">Following</h2>
        <div class="documents-grid">
          <div v-if="loadingFollowing && !followingPosts.length" class="loading-state">
            Loading following posts...
          </div>
          <div v-else-if="!followingPosts.length" class="empty-state">
            No posts from followed users yet.
          </div>
          <div 
            v-else
            v-for="post in followingPosts" 
            :key="`following-${post.id}`" 
            class="document-card"
            @click="navigateToPost(post.id)"
          >
            <div class="document-preview">
              <img :src="getDocumentPreviewImage(post)" alt="Document preview" class="preview-image">
            </div>
            <div class="document-info">
              <h3 class="document-title">{{ post.title }}</h3>
              <p class="document-author">{{ post.author.username }} {{ formatDate(post.created_at) }}</p>
              <p class="document-type">{{ post.category.name }}</p>
              <div class="document-rating">
                <span class="rating-percentage">
                  <LikeIcon class="like-icon" />
                  {{ Math.round(post.rating_percentage) }}%
                </span>
              </div>
            </div>
          </div>
          <button v-if="hasMoreFollowing" class="carousel-btn next-btn" @click="loadMoreFollowing">
            <span>›</span>
          </button>
        </div>
      </section>

      <!-- Explore recommendations -->
      <section class="explore-section">
        <div class="explore-content">
          <div class="explore-text">
            <h2>Explore and get</h2>
            <p>tailored recommendations!</p>
            <button class="explore-btn" @click="navigateToExplore">
              Explore <span>→</span>
            </button>
          </div>
          <div class="explore-graphics">
            <div class="graphics-container">
              <div class="graphic-icon chart-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="none" d="M0 0h24v24H0z"/>
                  <path d="M5 3v16h16v2H3V3h2zm15.293 3.293l1.414 1.414L16 13.414l-3-2.999-4.293 4.292-1.414-1.414L13 7.586l3 2.999 4.293-4.292z" fill="#4CAF50"/>
                </svg>
              </div>
              <div class="graphic-icon list-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="none" d="M0 0h24v24H0z"/>
                  <path d="M8 4h13v2H8V4zm-5 3h2v2H3V7zm0 8h2v2H3v-2zm0-4h2v2H3v-2zm5 4h13v2H8v-2zm0-4h13v2H8v-2z" fill="#2196F3"/>
                </svg>
              </div>
              <div class="graphic-icon folder-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="none" d="M0 0h24v24H0z"/>
                  <path d="M12.414 5H21a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h7.414l2 2zM4 5v14h16V7h-8.414l-2-2H4z" fill="#4CAF50"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { LikeIcon } from '@/components/icons';
import { 
  fetchPopularPosts,
  fetchFollowingPosts
} from '@/services/postService';

const router = useRouter();

// State variables
const popularPosts = ref([]);
const followingPosts = ref([]);
const loadingPopular = ref(false);
const loadingFollowing = ref(false);
const hasMorePopular = ref(true);
const hasMoreFollowing = ref(true);
const popularPage = ref(0);
const followingPage = ref(0);
const limit = 6; // Number of items to show in each row

const loadPopularPosts = async () => {
  if (loadingPopular.value || !hasMorePopular.value) return;
  
  loadingPopular.value = true;
  
  try {
    const skip = popularPage.value * limit;
    const newPosts = await fetchPopularPosts(skip, limit);
    
    if (newPosts && newPosts.length > 0) {
      popularPosts.value = [...popularPosts.value, ...newPosts];
      hasMorePopular.value = newPosts.length === limit;
      popularPage.value++;
    } else {
      hasMorePopular.value = false;
    }
  } catch (err) {
    console.error('Error loading popular posts:', err);
  } finally {
    loadingPopular.value = false;
  }
};

const loadFollowingPosts = async () => {
  if (loadingFollowing.value || !hasMoreFollowing.value) return;
  
  loadingFollowing.value = true;
  
  try {
    const skip = followingPage.value * limit;
    const newPosts = await fetchFollowingPosts(skip, limit);
    
    if (newPosts && newPosts.length > 0) {
      followingPosts.value = [...followingPosts.value, ...newPosts];
      hasMoreFollowing.value = newPosts.length === limit;
      followingPage.value++;
    } else {
      hasMoreFollowing.value = false;
    }
  } catch (err) {
    console.error('Error loading following posts:', err);
    // If the API fails or isn't implemented yet, we'll try to use popular posts as a fallback
    if (followingPosts.value.length === 0) {
      await loadPopularPosts();
      followingPosts.value = [...popularPosts.value];
      hasMoreFollowing.value = hasMorePopular.value;
    }
  } finally {
    loadingFollowing.value = false;
  }
};

const loadMorePopular = () => {
  loadPopularPosts();
};

const loadMoreFollowing = () => {
  loadFollowingPosts();
};

const navigateToPost = (postId) => {
  router.push(`/post/${postId}`);
};

const navigateToExplore = () => {
  router.push('/explore');
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric'
  }).replace(/\//g, '-');
};

const getDocumentPreviewImage = (post) => {
  // Generate a color based on the post ID
  const colors = ['#e3f2fd', '#e8f5e9', '#fff3e0', '#f3e5f5', '#e8eaf6', '#e0f7fa'];
  const colorIndex = post.id % colors.length;
  
  // Return a data URL for a colored rectangle with the first letter of the title
  const firstLetter = post.title.charAt(0).toUpperCase();
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 300;
  const ctx = canvas.getContext('2d');
  
  // Fill background
  ctx.fillStyle = colors[colorIndex];
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Draw letter
  ctx.fillStyle = '#333';
  ctx.font = 'bold 120px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(firstLetter, canvas.width / 2, canvas.height / 2);
  
  return canvas.toDataURL();
};

onMounted(() => {
  loadPopularPosts();
  loadFollowingPosts();
});
</script>

<style scoped>
.home-page {
  background-color: white;
  width: 100%;
  padding: 20px;
}

.main-content {
  background: none;
  max-width: 1170px;
  margin: 0 auto;
}

.content-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.documents-grid {
  display: flex;
  overflow-x: auto;
  gap: 16px;
  padding: 10px 0;
  position: relative;
  scrollbar-width: none; /* Firefox */
}

.documents-grid::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge */
}

.document-card {
  min-width: 195px;
  max-width: 175px;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.1s;
}
.document-card:hover {
  background: #0099ff10;
}
.document-preview {
  height: 110px;
  background-color: #f5f5f5;
  border-radius: 20px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.document-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.document-title {
  font-size: 16px;
  font-weight: 400;
  color: var(--primary-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-author, .document-type {
  font-size: 14px;
  color: #9EA9B5;
}

.document-rating {
  display: flex;
  align-items: center;
}

.rating-percentage {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  height: 24px;
  background-color: #F6F7FB;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 400;
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
  background: white;
  border-radius: 10px;
  color: #666;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  border: none;
  font-size: 1.5rem;
  z-index: 2;
}

.next-btn {
  right: 0;
}

.explore-section {
  background-color: #f0f9eb;
  border-radius: 10px;
  padding: 20px;
  margin-top: 40px;
}

.explore-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.explore-text {
  flex: 1;
}

.explore-text h2 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.explore-text p {
  margin: 5px 0 20px 0;
  color: #666;
}

.explore-btn {
  display: inline-flex;
  align-items: center;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.explore-btn:hover {
  background-color: #f5f5f5;
}

.explore-btn span {
  margin-left: 5px;
}

.explore-graphics {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.graphics-container {
  display: flex;
  gap: 20px;
}

.graphic-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.graphic-icon svg {
  width: 30px;
  height: 30px;
}

.chart-icon {
  transform: translateY(-10px);
}

.list-icon {
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .documents-grid {
    overflow-x: auto;
  }
  
  .document-card {
    min-width: 200px;
  }
  
  .explore-content {
    flex-direction: column;
  }
  
  .explore-graphics {
    margin-top: 20px;
    justify-content: center;
  }
}
</style>