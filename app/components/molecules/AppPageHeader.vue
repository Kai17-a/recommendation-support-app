<script setup lang="ts">
defineProps<{
  eyebrow?: string;
  title: string;
  description?: string;
}>();
</script>

<template>
  <div class="page-head">
    <div>
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="description" class="muted">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-head-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
