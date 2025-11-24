<script>
  // import CSS file w/ tailwind directive; without this the tailwind CSS classes won't be processed and no styles will be applied
  import "./widget.css";

  /** @type {{ bindings: { value: number }}*/
  let { bindings } = $props();
</script>

<button class="bg-gray-500 p-2 rounded-md" onclick={() => bindings.value++}
  >Count is {bindings.value}</button
>
