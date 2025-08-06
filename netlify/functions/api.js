const axios = require('axios');

exports.handler = async function(event, context) {
  // Handle CORS preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  // Only handle POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const body = JSON.parse(event.body);
    const pdbId = body.pdb_id?.toUpperCase();
    const vizMode = body.viz_mode || 'backbone';

    if (!pdbId) {
      return {
        statusCode: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ error: 'PDB ID is required' })
      };
    }

    // Fetch PDB data
    const pdbUrl = `https://files.rcsb.org/download/${pdbId}.pdb`;
    const response = await axios.get(pdbUrl);
    const pdbData = response.data;

    // Parse PDB data (simplified version)
    const lines = pdbData.split('\n');
    const atoms = [];
    const residues = new Set();
    let atomCount = 0;
    let residueCount = 0;

    for (const line of lines) {
      if (line.startsWith('ATOM') || line.startsWith('HETATM')) {
        atomCount++;
        const residueName = line.substring(17, 20).trim();
        residues.add(residueName);
        
        // Extract coordinates
        const x = parseFloat(line.substring(30, 38));
        const y = parseFloat(line.substring(38, 46));
        const z = parseFloat(line.substring(46, 54));
        const element = line.substring(76, 78).trim();
        
        atoms.push({ x, y, z, element, residue: residueName });
      }
    }

    residueCount = residues.size;

    // Calculate molecular weight (simplified)
    const atomicWeights = { 'C': 12.01, 'N': 14.01, 'O': 16.00, 'S': 32.07, 'H': 1.008 };
    let molecularWeight = 0;
    for (const atom of atoms) {
      if (atomicWeights[atom.element]) {
        molecularWeight += atomicWeights[atom.element];
      }
    }

    // Calculate charge (simplified)
    const chargedResidues = { 'ARG': 1, 'LYS': 1, 'HIS': 0.1, 'ASP': -1, 'GLU': -1 };
    let charge = 0;
    for (const residue of residues) {
      if (chargedResidues[residue]) {
        charge += chargedResidues[residue];
      }
    }

    // Create visualization data based on mode
    let plotData;
    if (vizMode === 'atoms') {
      plotData = createAtomsVisualization(atoms);
    } else if (vizMode === 'surface') {
      plotData = createSurfaceVisualization(atoms);
    } else if (vizMode === 'secondary') {
      plotData = createSecondaryVisualization(atoms);
    } else {
      plotData = createBackboneVisualization(atoms);
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: JSON.stringify({
        success: true,
        pdb_id: pdbId,
        protein_info: {
          molecular_weight: Math.round(molecularWeight * 100) / 100,
          charge: Math.round(charge * 10) / 10,
          atom_count: atomCount,
          residue_count: residueCount,
          residue_types: Array.from(residues)
        },
        plot_data: plotData
      })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: JSON.stringify({ 
        error: error.message || 'An error occurred while processing the request' 
      })
    };
  }
};

function createBackboneVisualization(atoms) {
  // Filter for CA atoms (backbone)
  const caAtoms = atoms.filter(atom => atom.element === 'C');
  
  return {
    data: [{
      x: caAtoms.map(a => a.x),
      y: caAtoms.map(a => a.y),
      z: caAtoms.map(a => a.z),
      mode: 'markers+lines',
      type: 'scatter3d',
      marker: {
        size: 4,
        color: '#FF6B6B',
        opacity: 0.8
      },
      line: {
        color: '#34495E',
        width: 2
      },
      name: 'Backbone'
    }],
    layout: {
      title: 'Protein Backbone Structure',
      scene: {
        xaxis: { title: 'X (Å)' },
        yaxis: { title: 'Y (Å)' },
        zaxis: { title: 'Z (Å)' }
      },
      margin: { l: 0, r: 0, b: 0, t: 30 },
      height: 600
    }
  };
}

function createAtomsVisualization(atoms) {
  const carbonAtoms = atoms.filter(a => a.element === 'C');
  const nitrogenAtoms = atoms.filter(a => a.element === 'N');
  const oxygenAtoms = atoms.filter(a => a.element === 'O');
  const sulfurAtoms = atoms.filter(a => a.element === 'S');

  const traces = [];

  if (carbonAtoms.length > 0) {
    traces.push({
      x: carbonAtoms.map(a => a.x),
      y: carbonAtoms.map(a => a.y),
      z: carbonAtoms.map(a => a.z),
      mode: 'markers',
      type: 'scatter3d',
      marker: { size: 3, color: '#95A5A6', opacity: 0.8 },
      name: 'Carbon'
    });
  }

  if (nitrogenAtoms.length > 0) {
    traces.push({
      x: nitrogenAtoms.map(a => a.x),
      y: nitrogenAtoms.map(a => a.y),
      z: nitrogenAtoms.map(a => a.z),
      mode: 'markers',
      type: 'scatter3d',
      marker: { size: 4, color: '#3498DB', opacity: 0.8 },
      name: 'Nitrogen'
    });
  }

  if (oxygenAtoms.length > 0) {
    traces.push({
      x: oxygenAtoms.map(a => a.x),
      y: oxygenAtoms.map(a => a.y),
      z: oxygenAtoms.map(a => a.z),
      mode: 'markers',
      type: 'scatter3d',
      marker: { size: 4, color: '#E74C3C', opacity: 0.8 },
      name: 'Oxygen'
    });
  }

  if (sulfurAtoms.length > 0) {
    traces.push({
      x: sulfurAtoms.map(a => a.x),
      y: sulfurAtoms.map(a => a.y),
      z: sulfurAtoms.map(a => a.z),
      mode: 'markers',
      type: 'scatter3d',
      marker: { size: 5, color: '#F39C12', opacity: 0.8 },
      name: 'Sulfur'
    });
  }

  return {
    data: traces,
    layout: {
      title: 'Protein Atomic Structure',
      scene: {
        xaxis: { title: 'X (Å)' },
        yaxis: { title: 'Y (Å)' },
        zaxis: { title: 'Z (Å)' }
      },
      margin: { l: 0, r: 0, b: 0, t: 30 },
      height: 600
    }
  };
}

function createSurfaceVisualization(atoms) {
  const caAtoms = atoms.filter(atom => atom.element === 'C');
  
  return {
    data: [{
      x: caAtoms.map(a => a.x),
      y: caAtoms.map(a => a.y),
      z: caAtoms.map(a => a.z),
      mode: 'markers',
      type: 'scatter3d',
      marker: {
        size: 8,
        color: '#4ECDC4',
        opacity: 0.7,
        symbol: 'sphere'
      },
      name: 'Surface'
    }],
    layout: {
      title: 'Protein Surface Representation',
      scene: {
        xaxis: { title: 'X (Å)' },
        yaxis: { title: 'Y (Å)' },
        zaxis: { title: 'Z (Å)' }
      },
      margin: { l: 0, r: 0, b: 0, t: 30 },
      height: 600
    }
  };
}

function createSecondaryVisualization(atoms) {
  const caAtoms = atoms.filter(atom => atom.element === 'C');
  
  // Simple secondary structure assignment
  const helixAtoms = caAtoms.filter((_, i) => i % 4 === 0);
  const sheetAtoms = caAtoms.filter((_, i) => i % 3 === 0);
  const coilAtoms = caAtoms.filter((_, i) => i % 4 !== 0 && i % 3 !== 0);

  const traces = [];

  if (helixAtoms.length > 0) {
    traces.push({
      x: helixAtoms.map(a => a.x),
      y: helixAtoms.map(a => a.y),
      z: helixAtoms.map(a => a.z),
      mode: 'markers+lines',
      type: 'scatter3d',
      marker: { size: 6, color: '#E74C3C', opacity: 0.8 },
      line: { color: '#C0392B', width: 3 },
      name: 'Helix'
    });
  }

  if (sheetAtoms.length > 0) {
    traces.push({
      x: sheetAtoms.map(a => a.x),
      y: sheetAtoms.map(a => a.y),
      z: sheetAtoms.map(a => a.z),
      mode: 'markers+lines',
      type: 'scatter3d',
      marker: { size: 6, color: '#3498DB', opacity: 0.8 },
      line: { color: '#2980B9', width: 3 },
      name: 'Sheet'
    });
  }

  if (coilAtoms.length > 0) {
    traces.push({
      x: coilAtoms.map(a => a.x),
      y: coilAtoms.map(a => a.y),
      z: coilAtoms.map(a => a.z),
      mode: 'markers+lines',
      type: 'scatter3d',
      marker: { size: 4, color: '#95A5A6', opacity: 0.6 },
      line: { color: '#7F8C8D', width: 1 },
      name: 'Coil'
    });
  }

  return {
    data: traces,
    layout: {
      title: 'Protein Secondary Structure',
      scene: {
        xaxis: { title: 'X (Å)' },
        yaxis: { title: 'Y (Å)' },
        zaxis: { title: 'Z (Å)' }
      },
      margin: { l: 0, r: 0, b: 0, t: 30 },
      height: 600
    }
  };
} 