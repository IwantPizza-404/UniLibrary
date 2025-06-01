import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/authStore';
import { fetchUserProfile } from '@/services/userService';
import { fetchPost } from '@/services/postService';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import Home from '@/views/Home.vue';
import Profile from '@/views/Profile.vue';
import Post from '@/views/Post.vue';
import NotFound from '@/views/NotFound.vue';
import Upload from '@/views/Upload.vue';
import MyLibrary from '@/views/MyLibrary.vue';
import Search from '@/views/Search.vue';

const routes = [
  { 
    path: '/', 
    name: 'home',
    component: Home,
    meta: { showUI: true }
  },
  { 
    path: '/library', 
    name: 'library',
    component: MyLibrary,
    meta: { showUI: true }
  },
  { 
    path: '/login', 
    name: 'login',
    component: Login,
    meta: { showUI: false }
  },
  { 
    path: '/register',
    name: 'register',
    component: Register,
    meta: { showUI: false }
  },
  { 
    path: '/upload',
    name: 'upload',
    component: Upload,
    meta: { showUI: false, requiresAuth: true }
  },
  {
    path: '/search',
    name: 'search',
    component: Search,
    meta: { showUI: true }
  },
  { 
    path: '/post/:post_id',
    name: 'post',
    component: Post,
    meta: { showUI: true }
  },
  { 
    path: '/:username',
    name: 'profile',
    component: Profile,
    meta: { showUI: true }

  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFound,
    meta: { showUI: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();

  // Handle dynamic username route
  if (to.params.username && to.name !== 'NotFound') {
    try {
      await fetchUserProfile(to.params.username);
      next(); // Username exists, proceed to Profile
    } catch (error) {
      if (error.message === 'User not found') {
        // Redirect to NotFound route, preserving the URL in the NotFound component if needed
        next({ name: 'NotFound', params: { pathMatch: to.path.slice(1) } });
      } else {
        console.error('Error fetching user profile:', error);
        next({ name: 'NotFound' });
      }
    }
  }
  // Handle dynamic post route
  else if (to.params.post_id && to.path.startsWith('/post/')) {
    try {
      await fetchPost(to.params.post_id);
      next(); // Post exists, proceed to Post
    } catch (error) {
      if (error.message === 'Post not found') {
        next({ name: 'NotFound', params: { pathMatch: to.path.slice(1).split('/') } });
      } else {
        console.error('Error fetching post:', error);
        next({ name: 'NotFound' });
      }
    }
  }

  // Handle protected routes
  else if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } });
  }
  // Proceed for all other routes
  else {
    next();
  }
});

export default router;