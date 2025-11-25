<script>
  import "./widget.css";
  import Entity from "./Entity.svelte";

  /** @type {{ bindings: { entities: Array<any>, width: number, height: number, show_datatypes: boolean, datatype_truncate_length: number } }}*/
  let { bindings } = $props();

  // Entity positions (x, y coordinates)
  let entityPositions = $state(new Map());

  // Drag state
  let draggedEntity = $state(null);
  let dragOffset = $state({ x: 0, y: 0 });
  let isDragging = $state(false);
  let dragStartPos = $state({ x: 0, y: 0 });
  const DRAG_THRESHOLD = 5; // pixels

  // Layer system: tracks the layer index for each entity
  // Higher layer index = rendered on top
  let entityLayers = $state(new Map());
  let nextLayerIndex = $state(10); // Start at 10, increment for each selection

  // Container and canvas dimensions
  let containerRef = $state(null);
  let canvasRef = $state(null);
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

  // Initialize positions when entities change
  $effect(() => {
    const entities = bindings.entities || [];
    if (entities.length > 0) {
      // Check if we need to initialize positions for new entities
      const currentEntityNames = new Set(Array.from(entityPositions.keys()));
      const newEntityNames = new Set(entities.map((e) => e.name));

      // If entities changed, reset and re-layout
      if (
        currentEntityNames.size !== newEntityNames.size ||
        ![...currentEntityNames].every((name) => newEntityNames.has(name))
      ) {
        autoLayout(entities);
        // Initialize layers for new entities (keep existing layer indices)
        const newLayers = new Map(entityLayers);
        entities.forEach((entity, i) => {
          if (!newLayers.has(entity.name)) {
            newLayers.set(entity.name, i); // Base layer for unselected entities
          }
        });
        entityLayers = newLayers;
      }
    }
  });

  // Auto-layout: arrange entities in a circular or grid pattern
  function autoLayout(entities) {
    const positions = new Map();
    const centerX = containerWidth / 2;
    const centerY = containerHeight / 2;
    const radius = Math.min(containerWidth, containerHeight) / 3;

    if (entities.length === 1) {
      positions.set(entities[0].name, { x: centerX - 100, y: centerY - 100 });
    } else {
      entities.forEach((entity, index) => {
        const angle = (2 * Math.PI * index) / entities.length;
        const x = centerX + radius * Math.cos(angle) - 100;
        const y = centerY + radius * Math.sin(angle) - 100;
        positions.set(entity.name, { x, y });
      });
    }

    entityPositions = positions;
  }

  // Get entity position
  function getEntityPosition(entityName) {
    return entityPositions.get(entityName) || { x: 100, y: 100 };
  }

  // Set entity position
  function setEntityPosition(entityName, x, y) {
    const newPositions = new Map(entityPositions);
    newPositions.set(entityName, { x, y });
    entityPositions = newPositions;
  }

  // Handle entity selection - move to top layer
  function handleEntityClick(entityName) {
    const newLayers = new Map(entityLayers);
    newLayers.set(entityName, nextLayerIndex);
    entityLayers = newLayers;
    nextLayerIndex += 1;
  }

  // Get layer index for an entity (defaults to 0 if not set)
  function getEntityLayer(entityName) {
    return entityLayers.get(entityName) ?? 0;
  }

  // Drag handlers
  function handleDragStart(entityName, event) {
    if (!canvasRef) return;

    const pos = getEntityPosition(entityName);
    const rect = canvasRef.getBoundingClientRect();

    draggedEntity = entityName;
    dragOffset = {
      x: event.clientX - rect.left - pos.x,
      y: event.clientY - rect.top - pos.y,
    };
    dragStartPos = { x: event.clientX, y: event.clientY };
    isDragging = false; // Will be set to true if mouse moves beyond threshold

    const handleMouseMove = (e) => {
      if (draggedEntity && canvasRef) {
        // Check if mouse moved beyond threshold to consider it a drag
        const dx = Math.abs(e.clientX - dragStartPos.x);
        const dy = Math.abs(e.clientY - dragStartPos.y);
        if (dx > DRAG_THRESHOLD || dy > DRAG_THRESHOLD) {
          isDragging = true;
          // Move dragged entity to top layer
          const newLayers = new Map(entityLayers);
          newLayers.set(draggedEntity, nextLayerIndex);
          entityLayers = newLayers;
          nextLayerIndex += 1;
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
          setEntityPosition(draggedEntity, constrainedX, constrainedY);
        }
      }
    };

    const handleMouseUp = () => {
      // If it was a click (not a drag), move entity to top layer
      if (draggedEntity && !isDragging) {
        const newLayers = new Map(entityLayers);
        newLayers.set(draggedEntity, nextLayerIndex);
        entityLayers = newLayers;
        nextLayerIndex += 1;
      }
      isDragging = false;
      draggedEntity = null;
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  }

  // Get connection points for relationship lines
  // Returns the position at the attribute row where the line should connect
  function getConnectionPoint(entityName, attributeIndex, isSource) {
    const pos = getEntityPosition(entityName);
    const entity = bindings.entities?.find((e) => e.name === entityName);

    if (!entity) return { x: pos.x, y: pos.y };

    // Entity box dimensions
    const boxWidth = 200;
    const headerHeight = 40;
    const attributeRowHeight = 40;

    // Calculate Y position: header + attribute index * row height + center of row
    const y =
      pos.y +
      headerHeight +
      attributeIndex * attributeRowHeight +
      attributeRowHeight / 2;

    // For source (FK), line starts from right edge
    // For target (PK), line ends at left edge
    const x = isSource ? pos.x + boxWidth : pos.x;

    return { x, y };
  }

  // Find all relationships
  function getRelationships() {
    const entities = bindings.entities || [];
    const relationships = [];

    entities.forEach((entity) => {
      entity.attributes.forEach((attr, attrIndex) => {
        if (attr.foreign_key) {
          // Find the target attribute index
          const targetEntity = entities.find(
            (e) => e.name === attr.foreign_key.entity,
          );
          const targetAttrIndex =
            targetEntity?.attributes.findIndex(
              (a) => a.name === attr.foreign_key.attribute,
            ) ?? -1;

          if (targetAttrIndex >= 0) {
            relationships.push({
              from: entity.name,
              to: attr.foreign_key.entity,
              fromAttr: attr.name,
              toAttr: attr.foreign_key.attribute,
              fromAttrIndex: attrIndex,
              toAttrIndex: targetAttrIndex,
            });
          }
        }
      });
    });

    return relationships;
  }

  // Get all entities sorted by layer (lowest layer first, so highest renders on top)
  function getEntities() {
    const entities = bindings.entities || [];
    // Sort by layer index (ascending) so entities with higher layers render last (on top)
    return [...entities].sort((a, b) => {
      const layerA = getEntityLayer(a.name);
      const layerB = getEntityLayer(b.name);
      return layerA - layerB;
    });
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
      {#each getRelationships() as rel}
        {@const fromPos = getConnectionPoint(rel.from, rel.fromAttrIndex, true)}
        {@const toPos = getConnectionPoint(rel.to, rel.toAttrIndex, false)}
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
      {#each getEntities() as entity}
        {@const pos = getEntityPosition(entity.name)}
        {@const layer = getEntityLayer(entity.name)}
        <Entity
          {entity}
          x={pos.x}
          y={pos.y}
          {layer}
          showDatatypes={bindings.show_datatypes ?? true}
          truncateLength={bindings.datatype_truncate_length !== undefined
            ? bindings.datatype_truncate_length
            : 30}
          onDragStart={(e) => handleDragStart(entity.name, e)}
          onDrag={() => {}}
          onDragEnd={() => {}}
          onClick={() => handleEntityClick(entity.name)}
        />
      {/each}
    </div>
  </div>

  <!-- Auto-layout button -->
  <button
    class="absolute bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors z-20"
    onclick={() => autoLayout(getEntities())}
  >
    Auto Layout
  </button>
</div>
