<template>
  <div class="progress-bar-wrapp">
    <div class="progress-container">
      <div class="progress-bar" :style="{ width: `${value}%` }"></div>
    </div>
    <span class="progress-text">{{ value }}%</span>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    value: {
      type: Number,
      required: true,
      validator: value => value >= 0 && value <= 100
    }
  }
};
</script>

<style scoped>
.progress-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  height: 5px;
  display: flex;
  align-items: center;
}

.progress-bar {
  height: 100%;
  background-color: #007bff; /* Matches the primary color from your design */
  transition: width 0.3s ease-in-out;
  border-radius: 4px;
}

.progress-text {
  color: #9ea9b5;
  font-size: 12px;
}
.progress-bar-wrapp {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>