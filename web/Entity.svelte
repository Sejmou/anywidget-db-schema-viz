<script lang="ts">
  import { onMount } from "svelte";
  import { formatDatatype } from "./utils.js";
  interface Entity {
    name: string;
    attributes: Array<{
      name: string;
      datatype: string;
      primary_key?: boolean;
      foreign_key?: { entity: string; attribute: string };
    }>;
  }
  interface Props {
    entity: Entity;
    x: number;
    y: number;
    layer: number;
    showDatatypes: boolean;
    truncateLength: number;
    onDragStart: (event: MouseEvent) => void;
    onDrag: (event: MouseEvent) => void;
    onDragEnd: () => void;
    onClick: (event: MouseEvent) => void;
  }
  let {
    entity,
    x,
    y,
    layer = 0,
    showDatatypes = true,
    truncateLength = 30,
    onDragStart,
    onDrag,
    onDragEnd,
    onClick,
  }: Props = $props();
  let expandedAttrs = $state(new Set());
  let isEntityExpanded = $state(true);

  function toggleEntityExpand(event: MouseEvent) {
    event.stopPropagation();
    isEntityExpanded = !isEntityExpanded;
  }

  $inspect({ name: entity.name, isEntityExpanded });

  /**
   * @param {number} index
   * @param {MouseEvent} event
   */
  function toggleExpand(index: number, event: MouseEvent) {
    event.stopPropagation();
    if (expandedAttrs.has(index)) {
      expandedAttrs.delete(index);
    } else {
      expandedAttrs.add(index);
    }
    // Trigger reactivity by creating a new Set
    expandedAttrs = new Set(expandedAttrs);
  }

  function shouldTruncate(datatype: string): boolean {
    return datatype.length > truncateLength;
  }

  function truncate(datatype: string): string {
    return datatype.substring(0, truncateLength) + "...";
  }
</script>

<div
  class="absolute cursor-move bg-white border-2 border-gray-800 rounded-lg shadow-lg min-w-[200px] select-none active:cursor-grabbing focus:outline-none"
  style="left: {x}px; top: {y}px; z-index: {layer > 0 ? layer : 10};"
  onmousedown={(e) => {
    e.preventDefault();
    onDragStart(e);
  }}
  onclick={(e) => {
    onClick(e);
  }}
  onkeydown={(e) => {
    // TODO: implement keyboard navigation
    e.preventDefault();
  }}
  role="button"
  tabindex="0"
>
  <!-- Entity Name -->
  <div
    class="entity-header bg-blue-600 text-white font-bold px-4 py-2 rounded-t-md flex items-center justify-between"
  >
    <span>{entity.name}</span>
    <button
      class="text-white hover:text-gray-200 text-sm underline cursor-pointer shrink-0 ml-2"
      onclick={(e) => toggleEntityExpand(e)}
      type="button"
      aria-label={isEntityExpanded ? "Collapse entity" : "Expand entity"}
    >
      {isEntityExpanded ? "collapse" : "expand"}
    </button>
  </div>

  <!-- Attributes -->
  {#if isEntityExpanded}
    <div class="entity-attributes">
      {#each entity.attributes as attr, index}
        <div
          class="attribute-row px-4 py-2 border-b border-gray-200 last:border-b-0"
        >
          <div class="flex items-start gap-2 justify-between">
            <div class="flex items-start gap-2 flex-1 min-w-0">
              <span class="attribute-name font-medium text-gray-800 shrink-0">
                {attr.name}
              </span>
              {#if showDatatypes}
                <div class="flex-1 min-w-0">
                  {#if shouldTruncate(attr.datatype) && !expandedAttrs.has(index)}
                    <div class="flex items-center gap-1 flex-wrap">
                      <span
                        class="attribute-type text-sm text-gray-500 font-mono wrap-break-word"
                      >
                        {truncate(attr.datatype)}
                      </span>
                      <button
                        class="text-blue-600 hover:text-blue-800 text-xs underline cursor-pointer shrink-0"
                        onclick={(e) => toggleExpand(index, e)}
                        type="button"
                      >
                        expand
                      </button>
                    </div>
                  {:else if shouldTruncate(attr.datatype) && expandedAttrs.has(index)}
                    <div class="flex flex-col gap-1">
                      <span
                        class="attribute-type text-sm text-gray-500 font-mono whitespace-pre-wrap wrap-break-word"
                      >
                        {formatDatatype(attr.datatype)}
                      </span>
                      <button
                        class="text-blue-600 hover:text-blue-800 text-xs underline cursor-pointer self-start"
                        onclick={(e) => toggleExpand(index, e)}
                        type="button"
                      >
                        collapse
                      </button>
                    </div>
                  {:else}
                    <span
                      class="attribute-type text-sm text-gray-500 font-mono wrap-break-word"
                    >
                      {attr.datatype}
                    </span>
                  {/if}
                </div>
              {/if}
            </div>
            <div class="flex items-center gap-1 shrink-0">
              {#if attr.primary_key}
                <span
                  class="badge bg-yellow-400 text-yellow-900 text-xs px-2 py-0.5 rounded font-semibold"
                  >PK</span
                >
              {/if}
              {#if attr.foreign_key}
                <span
                  class="badge bg-green-400 text-green-900 text-xs px-2 py-0.5 rounded font-semibold"
                  >FK</span
                >
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
