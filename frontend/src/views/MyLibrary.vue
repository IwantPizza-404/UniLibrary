<template>
    <div v-if="loading">
        <!-- Skeleton loader -->
    </div>
    <div v-else class="library-page">
        <div class="container">
            <section class="content-section upload-block">
                <h2 class="section-title">Start your contribution to learning</h2>
                <button @click="$router.push('/upload')" class="upload-area">
                    <UploadPic/>
                    Upload a document to start working on it
                </button>
            </section>
            <section class="content-section">
                <h2 class="section-title">My Uploads</h2>
                <div class="section-content">
                    <div v-if="posts && isAuthenticated" class="uploads-list">
                        <router-link :to="'/post/'+post.id" v-for="(post, index) in posts" :key="post.id" class="upload-item">
                            <DocumentIcon/>
                            <span class="upload-title">{{ post.title }}</span>
                            <span class="upload-tag">{{ post.category.name }}</span>
                        </router-link>
                    </div>
                    <div v-else class="info-section">
                        <div class="info-icon">
                            <InfoIcon/>
                        </div>
                        Once you upload your first document, it will appear here.
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { fetchUserPosts } from '@/services/postService';
import { useAuthStore } from '@/store/authStore';
import { DocumentIcon, PlusIcon, UploadPic, InfoIcon} from '@/components/icons'

// State variables
const authStore = useAuthStore();
const user = computed(() => authStore.user);
const posts = ref(null);
const loading = ref(false);
const error = ref(null);

// Computed properties
const isAuthenticated = computed(() => authStore.isAuthenticated);

const loadPosts = async (username) => {
  loading.value = true;
  error.value = null;

  try {
    posts.value = await fetchUserPosts(username);
  } catch (err) {
    console.error(err);
    error.value = 'Failed to load data';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
    if (isAuthenticated.value) {
        loadPosts(user.value.username);
    }
});
</script>

<style scoped>
.container {
    width: 100%;
    max-width: 1170px;
    margin: 0 auto;
    padding: 0 24px;
}
.library-page {
    padding: 36px 0;
}
.content-section {
    padding: 32px;
    background-color: #fff;
    border-radius: 20px;
}
.content-section:not(:last-child) {
    margin-bottom: 36px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 12px;
}
.uploads-list {
    display: flex;
    width: 100%;
    flex-direction: column;
}
.upload-item {
    display: flex;
    align-items: center;
    gap: 8px;
    overflow: hidden;
    padding: 16px 12px;
    text-decoration: none;
    border-radius: 8px;
}
.upload-item:hover {
    background: var(--primary-color-10);
}
.upload-title {
    font-size: 16px;
    font-weight: 400;
    color: var(--text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.upload-tag {
    font-size: 14px;
    font-weight: 400;
    color: #9EA9B5;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.upload-block {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.upload-area {
    align-items: center;
    border: 2px dashed;
    border-radius: 20px;
    display: flex;
    gap: 16px;
    width: 100%;
    justify-content: center;
    padding: 16px;
    pointer-events: painted;
    background-color: #f1f7fe;
    border-color: #d5e9fe;
    padding: 36px;
}
.info-section {
    display: flex;
    gap: 8px;
    align-items: center;
    margin: 8px 0;
    padding: 16px;
    border-radius: 12px;
    font-size: 16px;
    background-color: #f1f7fe;
    border: 1px solid #e2effd;
}
.info-icon {
    background-color: var(--primary-color);
    color: #f6f7fb;
    align-items: center;
    border-radius: 8px;
    display: inline-flex;
    flex-shrink: 0;
    height: 36px;
    justify-content: center;
    width: 36px;
}
</style>