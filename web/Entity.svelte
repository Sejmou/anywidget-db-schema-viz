<script>
  /** @type {{ 
    entity: { name: string, attributes: Array<{ name: string, datatype: string, primaryKey?: boolean, foreignKey?: { entity: string, attribute: string } }> },
    x: number,
    y: number,
    onDragStart: (event: MouseEvent) => void,
    onDrag: (event: MouseEvent) => void,
    onDragEnd: () => void
  }}*/
  let { entity, x, y, onDragStart, onDrag, onDragEnd } = $props();
</script>

<div
  class="absolute cursor-move bg-white border-2 border-gray-800 rounded-lg shadow-lg min-w-[200px] select-none active:cursor-grabbing focus:outline-none"
  style="left: {x}px; top: {y}px;"
  onmousedown={(e) => {
    e.preventDefault();
    onDragStart(e);
  }}
  role="button"
  tabindex="0"
>
  <!-- Entity Name -->
  <div
    class="entity-header bg-blue-600 text-white font-bold px-4 py-2 rounded-t-md"
  >
    {entity.name}
  </div>

  <!-- Attributes -->
  <div class="entity-attributes">
    {#each entity.attributes as attr}
      <div
        class="attribute-row px-4 py-2 border-b border-gray-200 last:border-b-0 flex items-center justify-between"
      >
        <div class="flex items-center gap-2 flex-1">
          <span class="attribute-name font-medium text-gray-800">
            {attr.name}
          </span>
          <span class="attribute-type text-sm text-gray-500">
            ({attr.datatype})
          </span>
        </div>
        <div class="flex items-center gap-1">
          {#if attr.primaryKey}
            <span
              class="badge bg-yellow-400 text-yellow-900 text-xs px-2 py-0.5 rounded font-semibold"
              >PK</span
            >
          {/if}
          {#if attr.foreignKey}
            <span
              class="badge bg-green-400 text-green-900 text-xs px-2 py-0.5 rounded font-semibold"
              >FK</span
            >
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>
