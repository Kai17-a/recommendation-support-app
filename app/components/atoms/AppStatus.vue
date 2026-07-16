<script setup lang="ts">
withDefaults(defineProps<{ tone?: string }>(), { tone: "blue" });
</script>

<template>
  <span class="status" :class="tone"><slot /></span>
</template>
