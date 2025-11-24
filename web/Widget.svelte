<script>
  /** @type {{ bindings: { value: number }}*/
  let { bindings } = $props();
</script>

<button onclick={() => bindings.value++}>Count is {bindings.value}</button>

<style>
  button {
    background: #ad1a1a;
    border-radius: 10px;
    border: 0;
    color: white;
    cursor: pointer;
    font-family: "Roboto", sans-serif;
    font-size: 2em;
    margin: 10px;
    padding: 10px 20px;
    transition: transform 0.25s ease-in-out;
  }

  button:hover {
    transform: scale(1.05);
  }
</style>
