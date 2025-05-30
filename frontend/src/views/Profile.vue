<template>
    <div v-if="loading">
        <!-- Skeleton loader -->
        
    </div>
    <div v-else-if="profile" class="profile-page">
        <section class="header-section">
            <div class="container">
                <div class="header-content">
                    <div class="user-avatar">
                        <img src="/avatar.png" alt="User">
                    </div>
                    <div class="user-info">
                        <h1 class="user__name">{{ profile?.full_name }}</h1>
                        <p class="user__email">{{ profile?.email }}</p>
                        <div class="user__stats">
                            <div class="stat-item">
                                <span class="stat__value">{{ profile?.followers_count }}</span>
                                <span class="stat__label">Followers</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat__value">{{ profile?.following_count }}</span>
                                <span class="stat__label">Following</span>
                            </div>
                        </div>
                        <div class="action-pannel">
                            <button v-if="user?.username !== profile?.username" 
                                    @click="handleFollowUser" 
                                    :class="['btn follow-btn', { 
                                        active: profile?.is_following,
                                        loading: following 
                                    }]"
                                    :disabled="following">
                                <span v-if="following" class="loading-spinner"></span>
                                <PlusIcon v-else-if="!profile?.is_following"/>
                                {{ profile?.is_following ? 'Unfollow' : 'Follow' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <section class="content-section">
            <div class="container">
                <section class="section">
                    <h2 class="section-title">Statistics</h2>
                    <div class="section-content">
                        <div class="uploads-stats">
                            <h2 class="uploads-stats__title">
                                <DocumentIcon/>
                                My Uploads
                            </h2>
                            <div class="uploads-stats__content">
                                <div class="uploads__stat-item">
                                    <span class="uploads__stat__value">{{ profile?.uploads_count }}</span>
                                    <span class="uploads__stat__label">Uploads</span>
                                </div>
                                <div class="uploads__stat-item">
                                    <span class="uploads__stat__value">{{ profile?.upvotes_count }}</span>
                                    <span class="uploads__stat__label">Upvotes</span>
                                </div>
                                <div class="uploads__stat-item">
                                    <span class="uploads__stat__value">{{ profile?.downvotes_count }}</span>
                                    <span class="uploads__stat__label">Downvotes</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                <section class="section">
                    <h2 class="section-title">My Uploads</h2>
                    <div class="section-content">
                        <table class="uploads-table">
                            <thead>
                                <tr>
                                    <th>Document Title</th>
                                    <th>Views</th>
                                    <th>Ratings</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(post, index) in posts" :key="post.id">
                                    <td>
                                        <div class="document-item">
                                            <DocumentIcon class="document-icon"/>
                                            <router-link :to="'/post/'+post.id" href="#" class="document-link">{{ post.title }}</router-link>
                                        </div>
                                    </td>
                                    <td>-</td>
                                    <td>
                                        <div class="like-item">
                                            <LikeIcon class="like-icon"/>
                                            <span>{{ Math.round(post.rating_percentage || 0) }}%</span>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchUserProfile } from '@/services/userService';
import { fetchUserPosts } from '@/services/postService';
import { useAuthStore } from '@/store/authStore';
import { DocumentIcon, LikeIcon, PlusIcon} from '@/components/icons'
import { followUser, unfollowUser } from '@/services/userFollowService';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);
const router = useRouter();
const route = useRoute();
const profile = ref([]);
const posts = ref(null);
const following = ref(false);
const loading = ref(true);
const error = ref(null);

const loadProfile = async (username) => {
  loading.value = true;
  error.value = null;

  try {
    profile.value = await fetchUserProfile(username);
    posts.value = await fetchUserPosts(username);
  } catch (err) {
    console.error(err);
    error.value = 'Failed to load data';
  } finally {
    loading.value = false;
  }
};

const handleFollowUser = async () => {
    if (!isAuthenticated.value) {
        router.push('/login');
        return;
    }
    if (following.value) {
        return;
    }

    following.value = true;
    const previousState = profile.value.is_following;
    const previousFollowersCount = profile.value.followers_count;

    try {
        profile.value.is_following = !previousState;
        profile.value.followers_count = previousState 
            ? previousFollowersCount - 1
            : previousFollowersCount + 1;

        if (!previousState) {
            await followUser(profile.value.id);
        } else {
            await unfollowUser(profile.value.id);
        }
    } catch (err) {
        console.error('Error processing follow/unfollow:', err);
        error.value = 'Failed to process follow/unfollow. Please try again.';
    } finally {
        following.value = false;
    }
}

// react to route param changes
watch(
  () => route.params.username,
  (newUsername) => {
    if (newUsername) {
        loadProfile(newUsername);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.header-section {
    background-color: #f1f7fe;
    padding: 36px 0;
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
    gap: 32px;
}
.user-avatar {
    width: 60px;
    height: 60px;
    aspect-ratio: 1;
}
.user-avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}
.user-info {
    display: flex;
    gap: 4px;
    flex-direction: column;
}
.user__name {
    font-size: 26px;
    font-weight: 600;
    line-height: 130%;
}
.user__email {
    font-size: 16px;
    color: #6b7280;
}
.user__stats {
    display: flex;
    gap: 24px;
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
  color: #7a838c;
}

.stat__value {
  font-size: 16px;
  font-weight: 600;
  line-height: 125%;
  color: var(--text-color);
}

.content-section {
    padding: 36px 0;
    background-color: #ffffff;
}
.section:not(:last-child) {
    margin-bottom: 36px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 12px;
}
.uploads-stats {
    display: flex;
    flex-direction: column;
    padding: 20px 16px;
    background: #fff;
    border: 1px solid #e6ebef;
    border-radius: 20px;
    color: #4c5966;
}
.uploads-stats__title {
    display: flex;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    line-height: 130%;
    margin-bottom: 10px;
}
.uploads-stats__title svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}
.uploads-stats__content {
    display: flex;
    flex: 1;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
    border-top: 1px solid #e6ebef;
    padding-top: 8px;
    text-align: center;
}
.uploads__stat-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: center;
    flex: 1;
}
.uploads__stat-item:not(:last-child) {
    border-right: 1px solid #e6ebef;
}
.uploads__stat__value {
    font-size: 26px;
    font-weight: 700;
    line-height: 130%;
}
.uploads__stat__label{
    font-size: 14px;
    line-height: 130%;
}
.uploads-table {
    border-collapse: collapse;
    border-radius: 20px;
    border-style: hidden;
    box-shadow: 0 0 0 1px #e6ebef;
    overflow: hidden;
    text-align: left;
    width: 100%;
}
.uploads-table th {
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    padding: 12px 10px;
}
.uploads-table th:first-child {
    text-align: left;
    padding-left: 32px;
}
.uploads-table tr {
    border-top: 1px solid #e6ebef;
}
.uploads-table td {
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    padding: 20px 10px;
}
.uploads-table td:first-child {
    padding-left: 32px;
}
.document-link {
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    display: -webkit-box;
    overflow: hidden;
    text-overflow: ellipsis;
}
.document-item {
    display: flex;
    gap: 8px;
    align-items: center;
}
.document-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
}
.like-item {
    display: flex;
    gap: 4px;
    justify-content: center;
    align-items: center;
}
.like-icon {
    width: 18px;
    height: 18px;
    color: var(--primary-color);
    flex-shrink: 0;
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
.follow-btn {
    position: relative;
    background-color: var(--primary-color);
    color: #fff;
    border: 1px solid transparent;
    min-width: 100px;
    transition: all 0.3s ease;
}
.follow-btn.loading {
    background: transparent;
    border: 1px solid var(--text-color);
    color: var(--text-color);
    opacity: 0.7;
    cursor: default;
}
.loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid var(--primary-color);
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
.follow-btn.active {
    background-color: transparent;
    border: 1px solid var(--text-color);
    color: var(--text-color);
}


</style>