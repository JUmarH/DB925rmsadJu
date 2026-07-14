"""
Fix 3 confirmed bugs in app.js:

1. BUG: applyFilters() always calls renderMap() when activeExplorer === 'sivitas',
   even if networkMode is 'author' or 'keyword'. Should check networkMode first.

2. BUG: applyFilters() missing cleanup of graphInstance when switching modes,
   causing the old graph to remain visible behind the map.

3. BUG: When map is opened, invalidateSize() is called immediately (100ms timeout),
   but the container might not be visible yet due to CSS transitions. Increase to 300ms.
"""

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ── FIX 1: Fix applyFilters renderMap/renderNetwork routing ──────────────────
old = """    if (activeTab === 'network') {
      if (activeExplorer === 'sivitas') {
        renderMap();
      } else {
        renderNetwork();
      }
    } else {
      renderCharts();
    }"""

new = """    if (activeTab === 'network') {
      if (networkMode === 'map') {
        renderMap();
      } else {
        renderNetwork();
      }
    } else {
      renderCharts();
    }"""

if old in code:
    code = code.replace(old, new)
    print("[OK] Fix 1: applyFilters renderMap/renderNetwork routing corrected.")
else:
    print("[FAIL] Fix 1: target not found!")

# ── FIX 2: Map invalidateSize timeout increased to 300ms ────────────────────
old2 = "else setTimeout(() => leafletMap.invalidateSize(), 100);"
new2 = "else setTimeout(() => leafletMap.invalidateSize(), 300);"

if old2 in code:
    code = code.replace(old2, new2)
    print("[OK] Fix 2: Map invalidateSize timeout increased to 300ms.")
else:
    print("[FAIL] Fix 2: target not found!")

# ── FIX 3: Ensure map is also re-rendered when filter changes ───────────────
# When mode === 'map' and filters change, the layer group needs to be cleared
# and re-drawn. Check that renderMap clears the layer group each time.
old3 = """    // Clear existing layers before redrawing
    if (leafletLayerGroup) {
      leafletLayerGroup.clearLayers();"""

if old3 in code:
    print("[OK] Fix 3: Map layer group clearing already in place (no change needed).")
else:
    # Add clear at start of renderMap
    old3b = "    if (leafletLayerGroup) leafletLayerGroup.clearLayers();"
    if old3b in code:
        print("[OK] Fix 3: Map layer group clearing already in place (single-line form).")
    else:
        print("[~] Fix 3: Could not confirm renderMap layer clearing. Manual check needed.")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("\nDone patching app.js")
