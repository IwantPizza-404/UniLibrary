<template>
  <div class="upload-page">
    <header class="header">
      <div class="logo-section">
        <router-link to="/">
          <Logo/>
        </router-link>
      </div>
    </header>
    <main class="main">
      <div class="main-header">
        <h1 class="main_title">Start your contribution in education</h1>
        <p class="main_subtitle">Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
      </div>
      <div class="main-content">
        <div class="main-cont">
          <div class="upload-section">
            <div class="steps-bar">
              <div class="step-item" :class="{ active: currentStep === 1 }">
                <div class="step-label">
                  <span class="step-icon">1</span>
                  <span>Upload</span>
                </div>
                <div class="step-indicator"></div>
              </div>
              <div class="step-item" :class="{ active: currentStep === 2 }">
                <div class="step-label">
                  <span class="step-icon">2</span>
                  <span>Details</span>
                </div>
                <div class="step-indicator"></div>
              </div>
              <div class="step-item" :class="{ active: currentStep === 3 }">
                <div class="step-label">
                  <span class="step-icon">3</span>
                  <span>Done</span>
                </div>
                <div class="step-indicator"></div>
              </div>
            </div>
            <!-- Step 1: Upload -->
            <div v-if="currentStep === 1">
              <div class="upload-area">
                <input id="uploadfile" class="upload-input" type="file" @change="handleFileUpload" accept=".pdf,.doc,.docx">
                <UploadPic/>
                <h2 class="upload-area-title">Upload your file</h2>
                <div class="action-pannel">
                  <label for="uploadfile" class="browse-btn">Browse my files</label>
                </div>
                <p class="upload-caption">Supported files: pdf, docx, doc, ppt</p>
              </div>
              <div v-if="uploadedFile.name">
                <div class="uploaded-file-section">
                  <div class="uploaded-file-header">
                    <div class="uploaded-file-title">
                      <DocumentIcon/>
                      <h4 class="uploaded-file__title">{{ uploadedFile.name }}</h4>
                    </div>
                    <button class="remove-upload-btn" @click="removeFile">
                      <TrashIcon/>
                    </button>
                  </div>
                  <div class="uploaded-file-progress">
                    <span>{{ (uploadedFile.size / 1024).toFixed(2) }} KB</span>
                    <ProgressBar :value="uploadedFile.progress"></ProgressBar>
                  </div>
                </div>
                <div class="navigation">
                  <button @click="nextStep" class="nav-btn">Next</button>
                </div>
              </div>
            </div>
            <!-- Step 2: Details -->
            <div v-if="currentStep === 2">
              <form class="details-area">
                <FormInput
                  id="title"
                  label="Title"
                  type="text"
                  v-model="fileDetails.title"
                  placeholder="Enter title"
                  required
                />
                <FormInput
                  id="description"
                  label="Description"
                  type="textarea"
                  v-model="fileDetails.description"
                  placeholder="Enter description"
                  required
                />
                <div class="input-field">
                  <label for="category">Category:</label>
                  <select id="category" v-model="fileDetails.categoryId">
                    <option value="" disabled selected>Select category</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>
              </form>
              <div class="navigation">
                <button @click="prevStep" class="nav-btn">Back</button>
                <button @click="nextStep" :disabled="!isDetailsValid" class="nav-btn">Next</button>
              </div>
            </div>
            <!-- Step 3: Done -->
            <div v-if="currentStep === 3">
              <div class="done-area">
                <div class="success-icon">
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="24" cy="24" r="24" fill="#E6F7F0"/>
                    <path d="M32 16L20 28L16 24" stroke="#42B983" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <h2 class="done-title">Thanks for sharing!</h2>
                <p v-if="!errorMessage" class="done-message">Your file "{{ uploadedFile.name }}" has been successfully submitted with the following details:</p>
                <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
                <div v-if="!errorMessage" class="details-list">
                  <div class="detail-item">
                    <span class="detail-label">Title</span>
                    <span class="detail-value">{{ fileDetails.title }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Description</span>
                    <span class="detail-value">{{ fileDetails.description }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Category</span>
                    <span class="detail-value">{{ getCategoryName(fileDetails.categoryId) }}</span>
                  </div>
                </div>
                <div class="navigation">
                  <button @click="$router.push('/')" class="default-btn home-btn">
                    <HomeIcon/>
                    Home
                  </button>
                  <button @click="resetForm" class="default-btn upload-more-btn">
                    <PlusIcon/>
                    Upload More
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Logo from '@/assets/images/logo.vue';
import { UploadPic, DocumentIcon, TrashIcon, HomeIcon, PlusIcon } from '@/components/icons';
import ProgressBar from '@/components/common/ProgressBar.vue';
import FormInput from '@/components/common/FormInput.vue';
import { createPost } from '@/services/postService';
import { fetchCategories } from '@/services/categoryService';

// Reactive state
const currentStep = ref(1);
const uploadedFile = ref({});
const fileDetails = ref({
  title: '',
  description: '',
  categoryId: ''
});
const errorMessage = ref('');
const categories = ref([]);
const isProcessing = ref(false); // Track processing state for simulation

// Fetch Categories on component mount
onMounted(async () => {
  await loadCategories();
});

// Fetch Categories
const loadCategories = async () => {
  try {
    const fetchedCategories = await fetchCategories();
    categories.value = fetchedCategories || [];
    if (categories.value.length === 0) {
      errorMessage.value = 'No categories available. Please try again later.';
    }
  } catch (err) {
    console.error('Failed to load categories:', err);
    errorMessage.value = 'Failed to load categories. Please try again later.';
  }
};

// Computed property
const isDetailsValid = computed(() => {
  return fileDetails.value.title && fileDetails.value.description && fileDetails.value.categoryId;
});

// Methods
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    uploadedFile.value = {
      file, // Store the actual file object
      name: file.name,
      size: file.size,
      progress: 0 // Start at 0
    };
  }
};

const removeFile = () => {
  uploadedFile.value = {};
};

const prevStep = () => {
  if (currentStep.value > 1) currentStep.value--;
};

const simulateProgress = () => {
  return new Promise((resolve) => {
    let progress = 0;
    isProcessing.value = true;
    const interval = setInterval(() => {
      progress += 10; // Increment by 10% every 300ms
      uploadedFile.value.progress = Math.min(progress, 100); // Cap at 100%
      if (progress >= 100) {
        clearInterval(interval);
        isProcessing.value = false;
        resolve();
      }
    }, 300); // Adjust timing for smoother or faster simulation
  });
};

const nextStep = async () => {
  if (currentStep.value === 1 && !uploadedFile.value.name) return;
  if (currentStep.value === 2 && !isDetailsValid.value) return;
  if (currentStep.value === 2) {
    const formData = new FormData();
    formData.append('title', fileDetails.value.title);
    formData.append('description', fileDetails.value.description);
    formData.append('category_id', fileDetails.value.categoryId); // Already an integer ID
    formData.append('file', uploadedFile.value.file);

    try {
      // Start progress simulation immediately
      simulateProgress();

      // Send the request (non-blocking)
      const result = await createPost(formData, () => {}); // No real progress callback needed
      if (result) {
        currentStep.value++;
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      errorMessage.value = 'Failed to submit the post. Please try again.';
      uploadedFile.value.progress = 0; // Reset progress on error
      console.error('Upload error:', error);
    }
  } else if (currentStep.value < 3) {
    currentStep.value++;
  }
};

const resetForm = () => {
  currentStep.value = 1;
  uploadedFile.value = {};
  fileDetails.value = { title: '', description: '', categoryId: '' };
  errorMessage.value = '';
  isProcessing.value = false;
};

// Helper to display category name in Done step
const getCategoryName = (categoryId) => {
  const category = categories.value.find(cat => cat.id === categoryId);
  return category ? category.name : 'Unknown';
};
</script>

<style scoped>
.header{
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    height: 72px;
    padding: 16px 32px;
    background-color: #F6F7FB;
    position: -webkit-sticky;
    position: sticky;
    top: 0;
    transition: background-color .5s ease;
    width: 100%;
    z-index: 10;
}
.main-header{
    background-color: #F6F7FB;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    color: var(--text-color);
    padding: 18px 0;
    gap: 4px;
}
.main_title{
    font-size: 26px;
    font-weight: 700;
    line-height: 125%;
}
.main_subtitle{
    font-size: 16px;
    font-weight: 400;
}
.main-cont{
    width: 100%;
    max-width: 970px;
    padding: 32px 20px 60px 20px;
    margin: 0 auto;
}
.steps-bar{
    display: flex;
    gap: 12px;
    margin: 0 auto 32px;
    max-width: 900px;
    width: 100%;
}
.step-item{
    align-items: center;
    display: flex;
    flex: 1;
    flex-direction: column;
    min-width: 56px;
    position: relative;
    transition: flex .5s ease-out;
}

.step-label > *{
    font-size: 16px;
    font-weight: 700;
    color: #d3d9e0;
}
.step-item.active .step-label > *{
    color: var(--primary-color);
}
.step-label{
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 8px;
}
.step-icon{
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 12px;
    font-weight: 700;
    width: 16px;
    height: 16px;
    aspect-ratio: 1;
}
.step-icon::before{
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: #d3d9e0;
    opacity: 0.4;
    border-radius: 50%;
}
.step-item.active .step-icon::before{
    background: var(--primary-color);
}

.step-item.active .step-indicator{
    background: var(--primary-color);

}
.step-indicator{
    background: #d3d9e0;
    border-radius: 4px;
    height: 8px;
    width: 100%;
}
.upload-area{
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background-color: #f1f7fe;
    border: 2px dashed #aad2ff;
    border-radius: 20px;
    position: relative;
    padding: 24px;
}
.upload-area-title{
    font-size: 22px;
    font-weight: 700;
    color: var(--text-color-light);
    margin-bottom: 20px;
}
.upload-caption{
    font-size: 14px;
    font-weight: 400;
    color: #9ea9b5;
}
.browse-btn{
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-color);
    color: white;
    border-radius: 40px;
    font-size: 16px;
    font-weight: 500;
    min-height: 40px;
    padding: 8px 20px;
}
.action-pannel{
    margin-bottom: 8px;
}
.upload-input{
    display: none;
}
.uploaded-file-section{
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 24px;
}
.uploaded-file-header{
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.uploaded-file-title{
    display: flex;
    align-items: center;
    gap: 8px;
}
.uploaded-file__title{
    font-size: 14px;
    font-weight: 700;
    color: var(--text-color-light);
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.uploaded-file-progress{
    display: flex;
    align-items: center;
    gap: 4px;
}
.uploaded-file-progress span{
    white-space: nowrap;
    color: #9ea9b5;
    font-size: 12px;
}
.remove-upload-btn{
    display: flex;
}
.remove-upload-btn svg{
    flex-shrink: 0;
    width: 20px;
    height: 20px;
}
.navigation{
    display: flex;
    gap: 12px;
    justify-content: space-between;
    align-items: center;
    margin-top: 24px;
}
.default-btn{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: var(--primary-color);
    color: white;
    border-radius: 40px;
    font-size: 16px;
    font-weight: 500;
    min-height: 40px;
    padding: 8px 20px;
}
.nav-btn{
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-color);
    color: white;
    border-radius: 40px;
    font-size: 16px;
    font-weight: 500;
    min-height: 40px;
    padding: 8px 20px;
}
.nav-btn:disabled{
    background: #9ea9b5;
}
.input-field {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
}

.input-field label {
    font-size: 16px;
    font-weight: 500;
    color: var(--text-color-light);
}

.input-field select {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background-color: #fff;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%239EA9B5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 16px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    color: var(--text-color);
    display: block;
    font-size: 16px;
    height: 48px;
    line-height: 130%;
    padding: 8px 36px 8px 16px;
    transition: all 0.2s ease;
    width: 100%;
}

.input-field select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.input-field select:disabled {
    background-color: #f8fafc;
    cursor: not-allowed;
    opacity: 0.7;
}

/* Add basic styling for new sections */
.details-area, .done-area {
    border: 1px solid #e6ebef;
    background: #f9f9f9;
    border-radius: 20px;
    margin-bottom: 24px;
    padding: 32px;
}
.details-area div {
  margin-bottom: 15px;
}
.done-area ul {
  list-style-type: none;
  padding: 0;
}

.done-area {
    border: 1px solid #e6ebef;
    background: white;
    border-radius: 24px;
    margin-bottom: 24px;
    padding: 40px;
    text-align: center;
}

.success-icon {
    margin-bottom: 24px;
    animation: scale-in 0.5s ease-out;
}

.done-title {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 16px 0;
    animation: slide-up 0.5s ease-out;
}

.done-message {
    font-size: 16px;
    color: #64748b;
    margin: 0 0 32px 0;
    animation: slide-up 0.5s ease-out 0.1s;
}

.error-message {
    color: #ef4444;
    background-color: #fee2e2;
    padding: 12px 16px;
    border-radius: 12px;
    margin: 0 0 32px 0;
    animation: shake 0.5s ease-in-out;
}

.details-list {
    background: #f8fafc;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 32px;
    text-align: left;
    animation: slide-up 0.5s ease-out 0.2s;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px 0;
    border-bottom: 1px solid #e2e8f0;
}

.detail-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.detail-item:first-child {
    padding-top: 0;
}

.detail-label {
    font-size: 14px;
    font-weight: 500;
    color: #64748b;
}

.detail-value {
    font-size: 16px;
    color: var(--text-color);
    word-break: break-word;
}

.navigation {
    display: flex;
    gap: 16px;
    justify-content: center;
    animation: slide-up 0.5s ease-out 0.3s;
}

.home-btn, .upload-more-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-width: 160px;
    transition: all 0.2s ease;
}

.home-btn {
    background-color: #f8fafc;
    color: var(--text-color);
}

.home-btn:hover {
    background-color: var(--primary-color-10);
    color: var(--primary-color);
}

.upload-more-btn {
    background-color: var(--primary-color);
    color: white;
}

.upload-more-btn:hover {
    background-color: #369f6e;
    box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

@keyframes scale-in {
    0% {
        transform: scale(0);
        opacity: 0;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes slide-up {
    0% {
        transform: translateY(20px);
        opacity: 0;
    }
    100% {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-4px); }
    75% { transform: translateX(4px); }
}

/* Responsive adjustments */
@media (max-width: 480px) {
    .done-area {
        padding: 24px;
    }

    .done-title {
        font-size: 24px;
    }

    .navigation {
        flex-direction: column;
    }

    .home-btn, .upload-more-btn {
        width: 100%;
    }
}
</style>