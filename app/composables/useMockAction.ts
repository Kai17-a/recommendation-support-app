export function useMockAction() {
  const isPending = ref(false);

  async function run(action: () => void, delay = 400) {
    if (isPending.value) return;

    isPending.value = true;
    await new Promise((resolve) => window.setTimeout(resolve, delay));
    action();
    isPending.value = false;
  }

  return { isPending, run };
}
