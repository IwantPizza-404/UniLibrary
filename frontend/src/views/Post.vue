<template>
  <div>
    <!-- Loading state with skeleton loader -->
    <div v-if="loading" class="skeleton-loader">
      <div class="container">
        <div class="skeleton-header">
          <div class="skeleton-title"></div>
          <div class="skeleton-meta-bar">
            <div class="skeleton-meta-item"></div>
          </div>
          <div class="skeleton-author-block">
            <div class="skeleton-avatar"></div>
            <div class="skeleton-author-details">
              <div class="skeleton-author-name"></div>
            </div>
          </div>
          <div class="skeleton-date"></div>
        </div>
        <div class="skeleton-content">
          <div class="skeleton-file-display"></div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <div class="container">
        <div class="error-message">
          <h2>Oops! Something went wrong.</h2>
          <p>{{ error }}</p>
          <button @click="retryLoadPost" class="retry-button outline-btn">Retry</button>
        </div>
      </div>
    </div>

    <!-- Post data -->
    <div v-else-if="post" class="post-page">
      <section class="header-section">
        <div class="container">
          <div class="header-content">
            <section class="header-block">
              <h2 class="header__title">{{ post.title }}</h2>
              <div class="meta-bar">
                <div class="meta-item">
                  <div class="category-btn">
                    <CategoryIcon class="category-icon" />
                    <span>{{ post.category.name }}</span>
                  </div>
                </div>
              </div>
              <div class="author-block">
                <h3 class="author-block__title">Uploaded by:</h3>
                <div class="author-info">
                  <img src="/avatar.png" alt="User avatar" class="avatar" aria-hidden="true" />
                  <span class="author-details">
                    <router-link :to="'/'+post.author.username" class="author-name">{{ post.author.username }}</router-link>
                  </span>
                </div>
              </div>
              <h4 class="post-date">{{ formatDate(post.created_at) }}</h4>
            </section>
            <section class="header-block">
              <div class="action-bar">
                <div class="vote-section">
                    <button @click="downloadFile" class="download-btn outline-btn">
                        <DownloadIcon />
                        Download
                    </button>
                    <button 
                        @click="vote(true)"
                        :disabled="voting"
                        :class="{
                            'upvote-btn': true,
                            'vote-btn': true,
                            'outline-btn': true,
                            'active': post.user_vote === true,
                            'disabled': voting
                        }"
                    >
                        <LikeIcon/>
                        {{ post.upvotes }}
                    </button>
                    <button 
                        @click="vote(false)" 
                        :disabled="voting"
                        :class="{
                            'downvote-btn': true,
                            'vote-btn': true,
                            'outline-btn': true,
                            'active': post.user_vote === false,
                            'disabled': voting
                        }"
                    >
                        <DislikeIcon/>
                        {{ post.downvotes }}
                    </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </section>
      <section class="content-section">
        <div class="container">
          <!-- File display -->
          <div v-if="post.file_url" class="file-display">
            <!-- Docx rendered as HTML -->
            <div v-if="isDocx" class="docx-wrapper">
              <div v-if="docxLoading" class="docx-loading">
                <div class="spinner"></div>
                <p>Loading document...</p>
              </div>
              <div v-else class="docx-content" v-html="docxContent"></div>
            </div>
            <!-- PDF (including converted PPT) -->
            <div v-else-if="isPdf" class="pdf-wrapper">
              <iframe
                :src="'http://127.0.0.1:8000' + post.file_url"
                width="100%"
                height="600px"
                title="Post Document"
                frameborder="0"
              ></iframe>
              <p class="pdf-fallback">
                If the PDF does not display,
                <a :href="'http://127.0.0.1:8000' + post.file_url" download>download it here</a>.
              </p>
            </div>
          </div>
          <div v-else class="no-file-message">
            <p>No document attached to this post.</p>
          </div>
        </div>
      </section>
    </div>

    <!-- Fallback (shouldn't occur) -->
    <div v-else class="error-container">
      <div class="container">
        <p>Unexpected error: No post data available.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import mammoth from 'mammoth';
import { ref, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchPost, votePost } from '@/services/postService';
import { useAuthStore } from '@/store/authStore';
import { LikeIcon, DislikeIcon, CategoryIcon, DownloadIcon } from '@/components/icons';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(true);
const error = ref(null);
const docxContent = ref('');
const docxLoading = ref(false);
const voting = ref(false);

const isDocx = computed(() => {
  return post.value?.file_url?.match(/\.(docx)$/i);
});
const isPdf = computed(() => {
  return post.value?.file_url?.match(/\.pdf$/i);
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const loadDocxContent = async (fileUrl) => {
  docxLoading.value = true;
  try {
    const fullUrl = 'http://127.0.0.1:8000' + fileUrl;
    const response = await fetch(fullUrl);
    if (!response.ok) {
      throw new Error('Failed to fetch .docx file');
    }
    const arrayBuffer = await response.arrayBuffer();
    const result = await mammoth.convertToHtml({ arrayBuffer });
    docxContent.value = result.value || 'No content available.';
  } catch (err) {
    console.error('Error rendering .docx:', err);
    docxContent.value = 'Failed to render document.';
  } finally {
    docxLoading.value = false;
  }
};

const loadPost = async (postId) => {
  loading.value = true;
  error.value = null;
  docxContent.value = '';
  docxLoading.value = false;

  try {
    post.value = await fetchPost(postId);
    console.log('Post:', post.value);
    if (post.value?.file_url && isDocx.value) {
      await loadDocxContent(post.value.file_url);
    }
  } catch (err) {
    console.error('Error fetching data:', err);
    error.value = err.message === 'Post not found' ? 'This post does not exist.' : 'Failed to load post';
    router.push({
      name: 'NotFound',
      params: { pathMatch: route.path.slice(1).split('/') }
    });
  } finally {
    loading.value = false;
  }
};

const retryLoadPost = () => {
  loadPost(route.params.post_id);
};

const downloadFile = () => {
  if (post.value?.file_url) {
    const link = document.createElement('a');
    link.href = 'http://127.0.0.1:8000' + post.value.file_url;
    link.download = '';
    link.click();
  }
};

const vote = async (is_upvote) => {
  if (!isAuthenticated.value) {
    router.push('/login');
    return;
  }
  if (voting.value) {
    return; // Prevent multiple votes
  }

  voting.value = true;
  try {
    const updatedPost = await votePost(post.value.id, is_upvote);
    post.value = updatedPost;
  } catch (err) {
    console.error('Error voting post:', err);
    error.value = 'Failed to vote on the post. Please try again.';
  } finally {
    voting.value = false;
  }
};

watch(
  () => route.params.post_id,
  (newPostId) => {
    if (newPostId) {
      loadPost(newPostId);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.header-section {
    padding: 24px 0;
    border-radius: 8px;
}
.container {
    width: 100%;
    max-width: 1170px;
    margin: 0 auto;
    padding: 0 24px;
}
.header-content {
    display: flex;
    flex-direction: column;
}

.header-block {
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid #eaeaea;
}
.header__title {
    font-size: 22px;
    font-weight: 600;
    color: var(--text-color);
}
.meta-bar {
    display: flex;
    width: 100%;
    gap: 16px;
}
.category-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    border-radius: 25px;
    background-color: var(--primary-color-10);
}
.category-btn > span {
    font-size: 14px;
    font-weight: 500;
    color: var(--primary-color);
}
.category-icon {
    color: var(--primary-color);
    width: 16px;
    height: 16px;
}

.author-block {
    display: flex;
    flex-direction: column;
}
.author-block__title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-color-light);
    margin-bottom: 12px;
}
.author-info {
    display: flex;
    align-items: center;
    gap: 12px;
}
.author-info .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
}
.author-details {
    display: flex;
    flex-direction: column;
}
.author-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
}
.action-bar {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
}
.vote-section {
    display: flex;
    gap: 8px;
}
.outline-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 40px;
    padding: 8px 20px;
    border-radius: 25px;
    background: #fff;
    color: var(--text-color);
    border: 1px solid #eaeaea;
    font-size: 16px;
    font-weight: 500;
    text-decoration: none;
    transition: background-color 0.2s, transform 0.2s;
}
.download-btn svg {
    width: 18px;
    height: 18px;
    color: #fff;
}
.download-btn {
    background-color: var(--primary-color);
    color: #fff;
}

.post-date {
    font-size: 14px;
    font-weight: 400;
    color: var(--text-color-light);
    margin-top: 8px;
}
.vote-btn.active{
    color: var(--primary-color);
}

/* Content Section */
.content-section {
  padding: 24px 0;
}
.file-display {
  margin-top: 0;
}
.docx-wrapper {
  position: relative;
}
.docx-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 600px;
  background-color: #f9f9f9;
  border: 1px solid #eaeaea;
  border-radius: 8px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.docx-loading p {
  margin-top: 16px;
  font-size: 16px;
  color: #6c757d;
}
.docx-content {
  border: 1px solid #eaeaea;
  padding: 15px;
  min-height: 600px;
  background-color: #f9f9f9;
  overflow-y: auto;
  border-radius: 8px;
}
.docx-content p {
  margin: 10px 0;
  line-height: 1.6;
}
.docx-content h1,
.docx-content h2,
.docx-content h3 {
  margin: 15px 0;
}
.pdf-wrapper {
  position: relative;
}
iframe {
  border: none;
  border-radius: 8px;
}
.pdf-fallback {
  margin-top: 8px;
  font-size: 14px;
  color: #6c757d;
  text-align: center;
}
.pdf-fallback a {
  color: #007bff;
  text-decoration: none;
}
.pdf-fallback a:hover {
  text-decoration: underline;
}
.no-file-message {
  text-align: center;
  padding: 40px 0;
  color: #6c757d;
  font-size: 16px;
}


/* Skeleton Loader */
.skeleton-loader {
  padding: 24px 0;
}
.skeleton-header {
  padding: 16px 0;
  border-bottom: 1px solid #eaeaea;
}
.skeleton-title {
  width: 60%;
  height: 28px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}
.skeleton-meta-bar {
  display: flex;
  gap: 16px;
  margin: 12px 0;
}
.skeleton-meta-item {
  width: 100px;
  height: 16px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}
.skeleton-author-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.skeleton-avatar {
  width: 36px;
  height: 36px;
  background: #e0e0e0;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}
.skeleton-author-details {
  flex: 1;
}
.skeleton-author-name {
  width: 120px;
  height: 16px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}
.skeleton-date {
  width: 150px;
  height: 16px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
  margin-top: 12px;
}
.skeleton-content {
  margin-top: 24px;
}
.skeleton-file-display {
  width: 100%;
  height: 600px;
  background: #e0e0e0;
  border-radius: 8px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Error State */
.error-container {
    padding: 40px 0;
    text-align: center;
    background-color: #fff;
    color: #2c3e50;
}
.error-message {
    display: flex;
    align-items: center;
    flex-direction: column;
    max-width: 500px;
    margin: 0 auto;
}
.error-message h2 {
  font-size: 24px;
  font-weight: 600;
  color: (--text-color);
  margin-bottom: 16px;
}
.error-message p {
  font-size: 16px;
  color: #6c757d;
  margin-bottom: 24px;
}
.retry-button {
  background-color: #007bff;
  color: #fff;
}
</style>