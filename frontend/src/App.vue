<template>
  <div class="app-container">
    <Header v-if="$route.meta.showUI"/>
    <div class="main-layout">
      <Sidebar v-if="$route.meta.showUI"/>
      <div class="main-content">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue';
import Header from '@/components/layout/Header.vue';
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.main-layout {
  display: flex;
  flex: 1;
}
.main-content {
  flex: 1;
  background-color: #f8f9fa;
  overflow-y: auto;
}
</style>