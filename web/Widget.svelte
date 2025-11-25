<script lang="ts">
  import "./widget.css";
  import EntityComponent from "./Entity.svelte";
  import type { Entity, Attribute, EntityWithRenderingState } from "./types";

  interface Bindings {
    entities: Array<Entity>;
    width: number;
    height: number;
    show_datatypes: boolean;
    datatype_truncate_length: number;
  }
  const { bindings }: { bindings: Bindings } = $props();

  // Single array of entities with their state (position and layer)
  let entitiesWithState = $state<Array<EntityWithRenderingState>>(
    bindings.entities.map((entity, i) => ({
      ...entity,
      x: 100 * i,
      y: 100 * i,
      layer: i,
      expanded: true,
    })),
  );

  // Drag state
  let dragOffset = $state({ x: 0, y: 0 });
  let isDragging = $state(false);
  let dragStartPos = $state({ x: 0, y: 0 });
  const DRAG_THRESHOLD = 5; // pixels

  // Container and canvas dimensions
  let containerRef = $state<HTMLElement | null>(null);
  let canvasRef = $state<HTMLElement | null>(null);
  let measuredWidth = $state(1000);

  // Use explicit width if provided (> 0), otherwise use measured parent width
  const containerWidth = $derived(
    bindings.width && bindings.width > 0 ? bindings.width : measuredWidth,
  );
  const containerHeight = $derived(bindings.height ?? 700);

  // Measure parent container width using ResizeObserver
  $effect(() => {
    if (!containerRef) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        if (width > 0) {
          measuredWidth = width;
        }
      }
    });

    // Observe the parent element
    const parent = containerRef.parentElement;
    if (parent) {
      resizeObserver.observe(parent);

      // Initial measurement
      const initialWidth = parent.getBoundingClientRect().width;
      if (initialWidth > 0) {
        measuredWidth = initialWidth;
      }
    }

    return () => {
      resizeObserver.disconnect();
    };
  });

  function moveEntityToTop(entity: EntityWithRenderingState) {
    // Move dragged entity to top layer
    const maxLayer = Math.max(...entitiesWithState.map((e) => e.layer));
    const entitiesAbove = entitiesWithState.filter(
      (e) => e.layer > entity.layer,
    );
    entity.layer = maxLayer;
    for (const entity of entitiesAbove) {
      entity.layer -= 1;
    }
  }

  // Drag handlers
  function handleDragStart(
    entity: EntityWithRenderingState,
    event: MouseEvent,
  ) {
    moveEntityToTop(entity);
    if (!canvasRef) return;

    const rect = canvasRef.getBoundingClientRect();

    dragOffset = {
      x: event.clientX - rect.left - entity.x,
      y: event.clientY - rect.top - entity.y,
    };
    dragStartPos = { x: event.clientX, y: event.clientY };
    isDragging = false; // Will be set to true if mouse moves beyond threshold

    const handleMouseMove = (e: MouseEvent) => {
      if (canvasRef) {
        // Check if mouse moved beyond threshold to consider it a drag
        const dx = Math.abs(e.clientX - dragStartPos.x);
        const dy = Math.abs(e.clientY - dragStartPos.y);
        if (dx > DRAG_THRESHOLD || dy > DRAG_THRESHOLD) {
          isDragging = true;
        }

        if (isDragging) {
          const rect = canvasRef.getBoundingClientRect();
          const newX = e.clientX - rect.left - dragOffset.x;
          const newY = e.clientY - rect.top - dragOffset.y;
          // Constrain to container bounds (with some padding)
          const constrainedX = Math.max(
            0,
            Math.min(newX, containerWidth - 200),
          );
          const constrainedY = Math.max(
            0,
            Math.min(newY, containerHeight - 100),
          );
          entity.x = constrainedX;
          entity.y = constrainedY;
        }
      }
    };

    const handleMouseUp = () => {
      isDragging = false;
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  }

  // Get connection points for relationship lines
  // Returns the position at the attribute row where the line should connect
  function getConnectionPoint(
    entity: EntityWithRenderingState,
    attribute: string,
    isSource: boolean,
  ) {
    // Entity box dimensions
    const boxWidth = 200;
    const headerHeight = 40;
    const attributeRowHeight = 40;

    const yOffset = !entity.expanded
      ? headerHeight / 2
      : headerHeight +
        entity.attributes.findIndex((a) => a.name === attribute) *
          attributeRowHeight +
        attributeRowHeight / 2;

    // Calculate Y position: header + attribute index * row height + center of row
    const y = entity.y + yOffset;

    // For source (FK), line starts from right edge
    // For target (PK), line ends at left edge
    const x = isSource ? entity.x + boxWidth : entity.x;

    return { x, y };
  }

  const relationships = $derived(getRelationships(entitiesWithState));

  // Find all relationships
  function getRelationships(entities: Array<EntityWithRenderingState>) {
    console.log("getting relationships", entities);
    const relationships: Array<{
      from: EntityWithRenderingState;
      to: EntityWithRenderingState;
      fromAttr: string;
      toAttr: string;
    }> = [];

    entities.forEach((entity) => {
      entity.attributes.forEach((attr: Attribute) => {
        if (attr.foreign_key) {
          const foreignKey = attr.foreign_key;
          // Find the target attribute index
          const targetEntity = entities.find(
            (e) => e.name === foreignKey.entity,
          );
          if (!targetEntity) return;
          const targetAttrIndex =
            targetEntity?.attributes.findIndex(
              (a) => a.name === foreignKey.attribute,
            ) ?? -1;

          if (targetAttrIndex >= 0) {
            relationships.push({
              from: entity,
              to: targetEntity,
              fromAttr: attr.name,
              toAttr: foreignKey.attribute,
            });
          }
        }
      });
    });

    return relationships;
  }
</script>

<div
  bind:this={containerRef}
  class="relative bg-gray-50 font-sans border border-gray-300 rounded-lg w-full"
  style="height: {containerHeight}px;"
>
  <div
    bind:this={canvasRef}
    class="relative w-full"
    style="height: {containerHeight}px;"
  >
    <!-- SVG overlay for relationship lines -->
    <svg class="absolute inset-0 pointer-events-none z-0 w-full h-full">
      {#each relationships as rel}
        {@const fromPos = getConnectionPoint(rel.from, rel.fromAttr, true)}
        {@const toPos = getConnectionPoint(rel.to, rel.toAttr, false)}
        <line
          x1={fromPos.x}
          y1={fromPos.y}
          x2={toPos.x}
          y2={toPos.y}
          stroke="#4B5563"
          stroke-width="2"
          marker-end="url(#arrowhead)"
        />
      {/each}
      <!-- Arrow marker definition -->
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#4B5563" />
        </marker>
      </defs>
    </svg>

    <!-- Entity components -->
    <div class="entities-container relative z-10">
      {#each entitiesWithState as entity}
        <EntityComponent
          {entity}
          showDatatypes={bindings.show_datatypes ?? true}
          truncateLength={bindings.datatype_truncate_length !== undefined
            ? bindings.datatype_truncate_length
            : 30}
          onDragStart={(e) => handleDragStart(entity, e)}
          onDrag={() => {}}
          onDragEnd={() => {}}
          onClick={() => moveEntityToTop(entity)}
          onToggleExpand={() => (entity.expanded = !entity.expanded)}
        />
      {/each}
    </div>
  </div>
</div>
