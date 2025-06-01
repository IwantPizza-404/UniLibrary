<template>
  <div class="form-input">
    <label v-if="label" :for="id" class="input-label">{{ label }}</label>
    <div class="input-wrapper">
      <input
        v-if="type !== 'textarea'"
        :id="id"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :required="required"
        class="input-field"
      />
      <textarea
        v-else
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :required="required"
        class="input-field textarea"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.form-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.input-label {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color-light);
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-field {
  width: 100%;
  height: 48px;
  padding: 12px 16px;
  font-size: 16px;
  font-family: var(--font-family);
  color: var(--text-color);
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.input-field::placeholder {
  color: #9EA9B5;
}

.input-field.textarea {
  height: auto;
  min-height: 120px;
  resize: vertical;
}

/* Error state */
.input-field.error {
  border-color: #ef4444;
}

.input-field.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Disabled state */
.input-field:disabled {
  background-color: #f8fafc;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>