<script setup lang="ts">
withDefaults(
  defineProps<{
    initial: string;
    size?: "default" | "small" | "large";
    tone?: string;
    tinted?: boolean;
  }>(),
  { size: "default", tone: "", tinted: false },
);
</script>

<template>
  <div
    class="avatar"
    :class="[
      size === 'default' ? '' : size,
      tinted ? 'tint' : '',
      tone ? `avatar-${tone}` : '',
    ]"
  >
    {{ initial }}
  </div>
</template>
