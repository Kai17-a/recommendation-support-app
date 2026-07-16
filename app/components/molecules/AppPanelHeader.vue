<script setup lang="ts">
defineProps<{ title: string; description?: string }>();
</script>

<template>
  <div class="panel-head">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description" class="muted">{{ description }}</p>
    </div>
    <slot name="actions" />
  </div>
</template>
