<script>
  /** @type {{ 
    entity: { name: string, attributes: Array<{ name: string, datatype: string, primary_key?: boolean, foreign_key?: { entity: string, attribute: string } }> },
    x: number,
    y: number,
    layer: number,
    showDatatypes: boolean,
    truncateLength: number,
    onDragStart: (event: MouseEvent) => void,
    onDrag: (event: MouseEvent) => void,
    onDragEnd: () => void,
    onClick: (event: MouseEvent) => void
  }}*/
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
  } = $props();
  let expandedAttrs = $state(new Set());

  /**
   * @param {number} index
   * @param {MouseEvent} event
   */
  function toggleExpand(index, event) {
    event.stopPropagation();
    if (expandedAttrs.has(index)) {
      expandedAttrs.delete(index);
    } else {
      expandedAttrs.add(index);
    }
    // Trigger reactivity by creating a new Set
    expandedAttrs = new Set(expandedAttrs);
  }

  /**
   * @param {string} datatype
   * @returns {string}
   */
  function formatDatatype(datatype) {
    // Format nested structures with proper indentation for better readability
    let result = "";
    let indentLevel = 0;
    let i = 0;
    const indentSize = 2;

    while (i < datatype.length) {
      const char = datatype[i];
      const prevChar = i > 0 ? datatype[i - 1] : "";
      const nextChar = i < datatype.length - 1 ? datatype[i + 1] : "";

      if (char === "(" || char === "[") {
        result += char;
        // Add line break and indent if this opens a non-empty structure
        if (nextChar && nextChar !== ")" && nextChar !== "]") {
          indentLevel++;
          result += "\n" + " ".repeat(indentLevel * indentSize);
        }
      } else if (char === ")" || char === "]") {
        // Add newline and reduce indent before closing (if not empty structure)
        if (indentLevel > 0 && prevChar !== "(" && prevChar !== "[") {
          indentLevel--;
          result += "\n" + " ".repeat(indentLevel * indentSize);
        }
        result += char;
      } else if (char === ",") {
        result += char;
        // Add line break after comma if not at end of list
        if (
          nextChar &&
          nextChar !== " " &&
          nextChar !== ")" &&
          nextChar !== "]"
        ) {
          result += "\n" + " ".repeat(indentLevel * indentSize);
        } else if (nextChar === " ") {
          result += " ";
        }
      } else {
        result += char;
      }
      i++;
    }

    return result;
  }

  /**
   * @param {string} datatype
   * @returns {boolean}
   */
  function shouldTruncate(datatype) {
    return datatype.length > truncateLength;
  }

  /**
   * @param {string} datatype
   * @returns {string}
   */
  function truncate(datatype) {
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
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onClick(e);
    }
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
</div>
