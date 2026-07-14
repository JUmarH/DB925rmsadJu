import sys

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add map button DOM element
content = content.replace(
    "const netModeKeywordBtn = document.getElementById('net-mode-keyword-btn');",
    "const netModeKeywordBtn = document.getElementById('net-mode-keyword-btn');\n  const netModeMapBtn = document.getElementById('net-mode-map-btn');"
)

# 2. Add map button Event listener
content = content.replace(
    "netModeKeywordBtn.addEventListener('click', () => switchNetworkMode('keyword'));",
    "netModeKeywordBtn.addEventListener('click', () => switchNetworkMode('keyword'));\n    netModeMapBtn.addEventListener('click', () => switchNetworkMode('map'));"
)

# 3. Modify switchExplorer
old_explorer = """      // Update canvas visibility: Sivitas shows Leaflet Map, others show force-graph
      if (explorerName === 'sivitas') {
        mapContainer.style.display = 'block';
        graphCanvas.style.display = 'none';
        
        // Hide co-authorship / keyword co-occurrence buttons as they are not needed on map
        document.querySelector('.section-controls').style.visibility = 'hidden';
        document.querySelector('.graph-legend').style.display = 'none';
      } else {
        mapContainer.style.display = 'none';
        graphCanvas.style.display = 'block';
        document.querySelector('.section-controls').style.visibility = 'visible';
        document.querySelector('.graph-legend').style.display = 'flex';
        // Show/hide relevant legends
        document.getElementById('legend-etd').style.display = (explorerName === 'etd') ? 'flex' : 'none';
        document.getElementById('legend-sivitas').style.display = (explorerName === 'sivitas') ? 'flex' : 'none';
        document.getElementById('legend-koran').style.display = (explorerName === 'koran') ? 'flex' : 'none';
      }"""

new_explorer = """      // Update Map Button visibility
      netModeMapBtn.style.display = (explorerName === 'sivitas') ? 'inline-block' : 'none';
      
      // Auto-switch modes when navigating
      if (explorerName === 'sivitas') {
         if (networkMode !== 'map' && networkMode !== 'author' && networkMode !== 'keyword') {
            networkMode = 'map';
         }
      } else {
         if (networkMode === 'map') {
            networkMode = 'author';
         }
      }
      
      // Show/hide relevant legends
      document.getElementById('legend-etd').style.display = (explorerName === 'etd') ? 'flex' : 'none';
      document.getElementById('legend-sivitas').style.display = (explorerName === 'sivitas') ? 'flex' : 'none';
      document.getElementById('legend-koran').style.display = (explorerName === 'koran') ? 'flex' : 'none';
      
      // Force UI sync
      const currentMode = networkMode;
      networkMode = null; 
      switchNetworkMode(currentMode);"""

content = content.replace(old_explorer, new_explorer)

# 4. Modify applyFilters
old_apply = """    if (activeTab === 'network') {
      if (activeExplorer === 'sivitas') {
        renderMap();
      } else {
        renderNetwork();
      }
    } else if (activeTab === 'analytics') {"""

new_apply = """    if (activeTab === 'network') {
      if (networkMode === 'map') {
        renderMap();
      } else {
        renderNetwork();
      }
    } else if (activeTab === 'analytics') {"""

content = content.replace(old_apply, new_apply)

# 5. Modify switchNetworkMode
old_switch_net = """  function switchNetworkMode(mode) {
    if (networkMode === mode) return;
    
    networkMode = mode;
    
    if (mode === 'author') {
      netModeAuthorBtn.classList.add('active');
      netModeKeywordBtn.classList.remove('active');
      nodeFreqSlider.min = 1;
      nodeFreqSlider.max = 15;
      nodeFreqSlider.value = 3;
      freqValLabel.textContent = "3";
    } else {
      netModeAuthorBtn.classList.remove('active');
      netModeKeywordBtn.classList.add('active');
      nodeFreqSlider.min = 2;
      nodeFreqSlider.max = 30;
      nodeFreqSlider.value = 5;
      freqValLabel.textContent = "5";
    }
    
    renderNetwork();
  }"""

new_switch_net = """  function switchNetworkMode(mode) {
    if (networkMode === mode) return;
    networkMode = mode;
    
    netModeAuthorBtn.classList.remove('active');
    netModeKeywordBtn.classList.remove('active');
    netModeMapBtn.classList.remove('active');
    
    if (mode === 'author') {
      netModeAuthorBtn.classList.add('active');
      nodeFreqSlider.min = 1;
      nodeFreqSlider.max = 15;
      nodeFreqSlider.value = 3;
      freqValLabel.textContent = "3";
    } else if (mode === 'keyword') {
      netModeKeywordBtn.classList.add('active');
      nodeFreqSlider.min = 2;
      nodeFreqSlider.max = 30;
      nodeFreqSlider.value = 5;
      freqValLabel.textContent = "5";
    } else if (mode === 'map') {
      netModeMapBtn.classList.add('active');
    }
    
    // Update canvas visibility based on mode
    if (mode === 'map') {
      mapContainer.style.display = 'block';
      graphCanvas.style.display = 'none';
      document.querySelector('.graph-legend').style.display = 'none';
      document.querySelector('.frequency-control').style.visibility = 'hidden';
      if (!mapInstance) initMap();
      else setTimeout(() => mapInstance.invalidateSize(), 100);
    } else {
      mapContainer.style.display = 'none';
      graphCanvas.style.display = 'block';
      document.querySelector('.graph-legend').style.display = 'flex';
      document.querySelector('.frequency-control').style.visibility = 'visible';
    }
    
    // Re-render
    if (mode === 'map') {
       renderMap();
    } else {
       renderNetwork();
    }
  }"""

content = content.replace(old_switch_net, new_switch_net)

# 6. Modify Author nodes logic for ETD roles
old_author = """    if (networkMode === 'author') {
      // Co-authorship
      const authorFreq = {};
      const authorDocSources = {}; // store source databases mapped to authors
      
      // Calculate author frequency
      docsToProcess.forEach(d => {
        if (!d.authors) return;
        d.authors.forEach(auth => {
          authorFreq[auth] = (authorFreq[auth] || 0) + 1;
          
          if (!authorDocSources[auth]) authorDocSources[auth] = new Set();
          authorDocSources[auth].add(d.source);
        });
      });
      
      // Filter authors by min frequency
      const validAuthors = Object.keys(authorFreq).filter(auth => authorFreq[auth] >= minFreq);
      const validAuthorsSet = new Set(validAuthors);
      
      // Build Nodes
      validAuthors.forEach(auth => {
        // Determine primary source
        const sources = Array.from(authorDocSources[auth]);
        let primarySource = 'mixed';
        if (sources.length === 1) {
          primarySource = sources[0];
        }
        
        graphData.nodes.push({
          id: auth,
          name: auth,
          val: authorFreq[auth], // size
          source: primarySource,
          count: authorFreq[auth]
        });
      });"""

new_author = """    if (networkMode === 'author') {
      // Co-authorship
      const authorFreq = {};
      const authorDocSources = {}; // store source databases mapped to authors
      const authorEtdRole = {};
      
      // Calculate author frequency
      docsToProcess.forEach(d => {
        if (!d.authors) return;
        d.authors.forEach((auth, index) => {
          authorFreq[auth] = (authorFreq[auth] || 0) + 1;
          
          if (!authorDocSources[auth]) authorDocSources[auth] = new Set();
          authorDocSources[auth].add(d.source);
          
          if (d.source === 'etd') {
              authorEtdRole[auth] = authorEtdRole[auth] || { s1:0, s2:0, s3:0, dosen:0 };
              if (index === 0) {
                 if (d.type === 'Skripsi') authorEtdRole[auth].s1++;
                 else if (d.type === 'Tesis') authorEtdRole[auth].s2++;
                 else if (d.type === 'Disertasi') authorEtdRole[auth].s3++;
                 else authorEtdRole[auth].s1++; // default to s1
              } else {
                 authorEtdRole[auth].dosen++;
              }
          }
        });
      });
      
      // Filter authors by min frequency
      const validAuthors = Object.keys(authorFreq).filter(auth => authorFreq[auth] >= minFreq);
      const validAuthorsSet = new Set(validAuthors);
      
      // Build Nodes
      validAuthors.forEach(auth => {
        // Determine primary source
        const sources = Array.from(authorDocSources[auth]);
        let primarySource = 'mixed';
        if (sources.length === 1) {
          primarySource = sources[0];
        }
        
        let role = null;
        if (primarySource === 'etd' && authorEtdRole[auth]) {
           const r = authorEtdRole[auth];
           const maxRole = Object.keys(r).reduce((a, b) => r[a] > r[b] ? a : b);
           if (maxRole === 's1') role = 'S1';
           else if (maxRole === 's2') role = 'S2';
           else if (maxRole === 's3') role = 'S3';
           else if (maxRole === 'dosen') role = 'Dosen';
        }
        
        graphData.nodes.push({
          id: auth,
          name: auth,
          val: authorFreq[auth], // size
          source: primarySource,
          role: role,
          count: authorFreq[auth]
        });
      });"""

content = content.replace(old_author, new_author)

# 7. Modify Color and Label for nodes
old_colors = """    const sourceColors = {
      etd: '#06b6d4',      // Cyan
      sivitas: '#a855f7',  // Purple
      koran: '#f97316',    /* Orange */
      mixed: '#64748b'     /* Gray */
    };
    
    // Draw force-graph
    graphInstance = ForceGraph()(canvasContainer)
      .graphData(graphData)
      .nodeId('id')
      .nodeVal('val')
      .nodeLabel(node => `${node.name} (${node.count} dokumen)`)
      .nodeColor(node => sourceColors[node.source] || '#64748b')"""

new_colors = """    const sourceColors = {
      etd: '#06b6d4',      // Default ETD (Cyan)
      etd_s1: '#3b82f6',   // Blue for S1
      etd_s2: '#22c55e',   // Green for S2
      etd_s3: '#eab308',   // Yellow for S3
      etd_dosen: '#ef4444',// Red for Dosen/Pembimbing
      sivitas: '#a855f7',  // Purple
      koran: '#f97316',    /* Orange */
      mixed: '#64748b'     /* Gray */
    };
    
    // Draw force-graph
    graphInstance = ForceGraph()(canvasContainer)
      .graphData(graphData)
      .nodeId('id')
      .nodeVal('val')
      .nodeLabel(node => {
         let roleStr = '';
         if (node.source === 'etd') {
            if (node.role === 'S1') roleStr = ' - Mahasiswa S1';
            else if (node.role === 'S2') roleStr = ' - Mahasiswa S2';
            else if (node.role === 'S3') roleStr = ' - Mahasiswa S3';
            else if (node.role === 'Dosen') roleStr = ' - Dosen/Pembimbing';
         }
         return `${node.name}${roleStr} (${node.count} dokumen)`;
      })
      .nodeColor(node => {
         if (node.source === 'etd' && node.role) {
            if (node.role === 'S1') return sourceColors.etd_s1;
            if (node.role === 'S2') return sourceColors.etd_s2;
            if (node.role === 'S3') return sourceColors.etd_s3;
            if (node.role === 'Dosen') return sourceColors.etd_dosen;
         }
         return sourceColors[node.source] || '#64748b';
      })"""
      
content = content.replace(old_colors, new_colors)

# Also update the legend to show the ETD colors!
old_legend = """<div class="legend-item" id="legend-etd"><span class="color-dot src-etd"></span> ETD</div>"""
new_legend = """<div class="legend-item" id="legend-etd" style="flex-wrap: wrap;">
              <span class="color-dot src-etd" style="background-color: #3b82f6;"></span> Mhs S1
              <span class="color-dot src-etd" style="background-color: #22c55e; margin-left: 8px;"></span> Mhs S2
              <span class="color-dot src-etd" style="background-color: #eab308; margin-left: 8px;"></span> Mhs S3
              <span class="color-dot src-etd" style="background-color: #ef4444; margin-left: 8px;"></span> Dosen
            </div>"""

# we need to do this in index.html, not app.js, so let's write to a separate file or just do it with replace_file_content

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.js updated successfully")
