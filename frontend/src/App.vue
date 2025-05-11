<template>
  <div class="app-container">
    <Header />
    <div class="main-layout">
      <Sidebar />
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