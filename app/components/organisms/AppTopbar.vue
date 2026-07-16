<script setup lang="ts">
defineProps<{ pageTitle: string }>();
</script>

<template>
  <header class="topbar">
    <div class="crumb">
      推薦支援ワークスペース <span>/</span> {{ pageTitle }}
    </div>
  </header>
</template>
