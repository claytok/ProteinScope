from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from Bio import PDB
from Bio.PDB.Polypeptide import PPBuilder
from Bio.PDB.DSSP import DSSP
import numpy as np
import plotly.graph_objects as go
import plotly.utils
import json
import requests
import os
from io import StringIO
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class ProteinAnalyzer:
    def __init__(self):
        self.parser = PDB.PDBParser(QUIET=True)
        self.ppb = PPBuilder()
        
    def fetch_pdb(self, pdb_id):
        """Fetch protein structure from PDB"""
        try:
            # Try to fetch from PDB
            url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except Exception as e:
            print(f"Error fetching PDB: {e}")
            return None
    
    def parse_structure(self, pdb_data):
        """Parse PDB data and return structure object"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as tmp:
                tmp.write(pdb_data)
                tmp_path = tmp.name
            
            structure = self.parser.get_structure('protein', tmp_path)
            os.unlink(tmp_path)
            return structure
        except Exception as e:
            print(f"Error parsing structure: {e}")
            return None
    
    def calculate_molecular_weight(self, structure):
        """Calculate molecular weight of the protein"""
        total_weight = 0
        atom_count = 0
        
        # Standard atomic weights (simplified)
        atomic_weights = {
            'C': 12.01, 'N': 14.01, 'O': 16.00, 'S': 32.07,
            'H': 1.008, 'P': 30.97, 'FE': 55.85, 'ZN': 65.38
        }
        
        for atom in structure.get_atoms():
            element = atom.element
            if element in atomic_weights:
                total_weight += atomic_weights[element]
            atom_count += 1
        
        return round(total_weight, 2), atom_count
    
    def calculate_charge(self, structure):
        """Calculate approximate charge at pH 7.4"""
        # Simplified charge calculation
        charged_residues = {
            'ARG': 1, 'LYS': 1,  # Positive
            'ASP': -1, 'GLU': -1,  # Negative
            'HIS': 0.1  # Slightly positive at pH 7.4
        }
        
        total_charge = 0
        for residue in structure.get_residues():
            if residue.resname in charged_residues:
                total_charge += charged_residues[residue.resname]
        
        return round(total_charge, 2)
    
    def get_secondary_structure(self, structure):
        """Analyze secondary structure composition"""
        helix_count = 0
        sheet_count = 0
        coil_count = 0
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    if residue.has_id('CA'):
                        # Simplified secondary structure detection
                        # In a real implementation, you'd use DSSP or similar
                        pass
        
        return {'helix': helix_count, 'sheet': sheet_count, 'coil': coil_count}
    
    def create_3d_visualization(self, structure, mode='backbone'):
        """Create 3D visualization using Plotly with different modes"""
        print(f"Creating visualization with mode: {mode}")  # Debug log
        
        if mode == 'backbone':
            return self.create_backbone_visualization(structure)
        elif mode == 'surface':
            return self.create_surface_visualization(structure)
        elif mode == 'atoms':
            return self.create_atoms_visualization(structure)
        elif mode == 'secondary':
            return self.create_secondary_structure_visualization(structure)
        else:
            print(f"Unknown mode '{mode}', using backbone")  # Debug log
            return self.create_backbone_visualization(structure)  # Default
    
    def create_backbone_visualization(self, structure):
        """Create backbone-focused visualization with clear secondary structure"""
        print("Creating BACKBONE visualization")  # Debug log
        
        # Create backbone trace with clear secondary structure representation
        ca_coords = []
        ca_colors = []
        ca_sizes = []
        
        # Get all CA atoms for backbone
        for residue in structure.get_residues():
            if residue.has_id('CA'):
                ca_atom = residue['CA']
                ca_coords.append(ca_atom.coord)
                
                # Color by residue type for better distinction
                resname = residue.resname
                if resname in ['ALA', 'GLY', 'PRO']:
                    color = '#95A5A6'  # Gray for small residues
                elif resname in ['ARG', 'LYS', 'HIS']:
                    color = '#E74C3C'  # Red for basic
                elif resname in ['ASP', 'GLU']:
                    color = '#3498DB'  # Blue for acidic
                elif resname in ['SER', 'THR', 'ASN', 'GLN']:
                    color = '#2ECC71'  # Green for polar
                elif resname in ['PHE', 'TYR', 'TRP']:
                    color = '#F39C12'  # Orange for aromatic
                else:
                    color = '#9B59B6'  # Purple for others
                
                ca_colors.append(color)
                ca_sizes.append(6)  # Consistent size for backbone
        
        traces = []
        
        # Main backbone trace
        if ca_coords:
            ca_x, ca_y, ca_z = zip(*ca_coords)
            traces.append(go.Scatter3d(
                x=ca_x, y=ca_y, z=ca_z,
                mode='lines+markers',
                line=dict(color='#34495E', width=8),
                marker=dict(
                    size=ca_sizes,
                    color=ca_colors,
                    opacity=0.9,
                    line=dict(width=1, color='#2C3E50')
                ),
                name='Protein Backbone',
                opacity=0.9,
                text=[f"Residue {i+1}" for i in range(len(ca_coords))],
                hovertemplate='<b>%{text}</b><br>' +
                            'Color: %{marker.color}<br>' +
                            '<extra></extra>'
            ))
        
        # Add peptide bonds as thin lines
        peptide_coords = []
        for residue in structure.get_residues():
            if residue.has_id('N') and residue.has_id('CA'):
                n_atom = residue['N']
                ca_atom = residue['CA']
                peptide_coords.extend([n_atom.coord, ca_atom.coord])
        
        if peptide_coords:
            peptide_x, peptide_y, peptide_z = zip(*peptide_coords)
            traces.append(go.Scatter3d(
                x=peptide_x, y=peptide_y, z=peptide_z,
                mode='lines',
                line=dict(color='#BDC3C7', width=2),
                name='Peptide Bonds',
                opacity=0.6,
                showlegend=False
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title='ProteinScope 3D Structure - Backbone View',
            scene=dict(
                xaxis_title='X (Å)',
                yaxis_title='Y (Å)',
                zaxis_title='Z (Å)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
                aspectmode='cube',
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99, xanchor="left", x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)', borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_surface_visualization(self, structure):
        """Create surface-focused visualization with all atoms"""
        print("Creating SURFACE visualization")  # Debug log
        
        # Create a comprehensive surface representation using all atoms
        all_atoms = []
        all_colors = []
        all_sizes = []
        all_names = []
        
        for atom in structure.get_atoms():
            coord = atom.coord
            all_atoms.append(coord)
            
            # Color by element for surface view
            element = atom.element
            if element == 'C':
                color = '#2E8B57'  # Sea green for carbon
                size = 3
            elif element == 'N':
                color = '#4169E1'  # Royal blue for nitrogen
                size = 4
            elif element == 'O':
                color = '#DC143C'  # Crimson for oxygen
                size = 4
            elif element == 'S':
                color = '#FFD700'  # Gold for sulfur
                size = 5
            else:
                color = '#FF69B4'  # Hot pink for others
                size = 6
            
            all_colors.append(color)
            all_sizes.append(size)
            
            # Create atom name for hover
            residue = atom.get_parent()
            if residue:
                all_names.append(f"{residue.resname}{residue.get_id()[1]}-{atom.name}")
            else:
                all_names.append(f"{atom.name}")
        
        traces = []
        
        # Main surface representation
        if all_atoms:
            atoms_x, atoms_y, atoms_z = zip(*all_atoms)
            traces.append(go.Scatter3d(
                x=atoms_x, y=atoms_y, z=atoms_z,
                mode='markers',
                marker=dict(
                    size=all_sizes,
                    color=all_colors,
                    opacity=0.7,
                    line=dict(width=0)
                ),
                name='Protein Surface (All Atoms)',
                opacity=0.7,
                text=all_names,
                hovertemplate='<b>%{text}</b><br>' +
                            'Element: %{marker.color}<br>' +
                            '<extra></extra>'
            ))
        
        # Add connecting lines for nearby atoms to create surface effect
        nearby_connections = []
        for i, atom1 in enumerate(all_atoms):
            for j, atom2 in enumerate(all_atoms[i+1:], i+1):
                # Calculate distance between atoms
                distance = np.linalg.norm(np.array(atom1) - np.array(atom2))
                if distance < 3.0:  # Connect atoms within 3Å
                    nearby_connections.extend([atom1, atom2])
        
        if nearby_connections:
            conn_x, conn_y, conn_z = zip(*nearby_connections)
            traces.append(go.Scatter3d(
                x=conn_x, y=conn_y, z=conn_z,
                mode='lines',
                line=dict(color='rgba(100,100,100,0.3)', width=1),
                name='Surface Connections',
                opacity=0.3,
                showlegend=False
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title='ProteinScope 3D Structure - Surface View',
            scene=dict(
                xaxis_title='X (Å)',
                yaxis_title='Y (Å)',
                zaxis_title='Z (Å)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
                aspectmode='cube',
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99, xanchor="left", x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)', borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_atoms_visualization(self, structure):
        """Create detailed atomic visualization with bonds"""
        print("Creating ATOMS visualization")  # Debug log
        
        # Create separate traces for different atom types with detailed information
        carbon_atoms = []
        nitrogen_atoms = []
        oxygen_atoms = []
        sulfur_atoms = []
        other_atoms = []
        
        # Also collect bond information
        bonds = []
        
        for atom in structure.get_atoms():
            coord = atom.coord
            atom_info = {
                'coord': coord,
                'name': atom.name,
                'residue': atom.get_parent().resname if atom.get_parent() else 'Unknown',
                'residue_id': atom.get_parent().get_id()[1] if atom.get_parent() else 0
            }
            
            if atom.element == 'C':
                carbon_atoms.append(atom_info)
            elif atom.element == 'N':
                nitrogen_atoms.append(atom_info)
            elif atom.element == 'O':
                oxygen_atoms.append(atom_info)
            elif atom.element == 'S':
                sulfur_atoms.append(atom_info)
            else:
                other_atoms.append(atom_info)
        
        traces = []
        
        # Carbon atoms with detailed hover info
        if carbon_atoms:
            c_coords = [atom['coord'] for atom in carbon_atoms]
            c_x, c_y, c_z = zip(*c_coords)
            c_text = [f"{atom['residue']}{atom['residue_id']}-{atom['name']}" for atom in carbon_atoms]
            
            traces.append(go.Scatter3d(
                x=c_x, y=c_y, z=c_z,
                mode='markers',
                marker=dict(
                    size=3,
                    color='#2E8B57',  # Sea green
                    opacity=0.8,
                    line=dict(width=0)
                ),
                name='Carbon Atoms',
                opacity=0.8,
                text=c_text,
                hovertemplate='<b>%{text}</b><br>Element: Carbon<br><extra></extra>'
            ))
        
        # Nitrogen atoms
        if nitrogen_atoms:
            n_coords = [atom['coord'] for atom in nitrogen_atoms]
            n_x, n_y, n_z = zip(*n_coords)
            n_text = [f"{atom['residue']}{atom['residue_id']}-{atom['name']}" for atom in nitrogen_atoms]
            
            traces.append(go.Scatter3d(
                x=n_x, y=n_y, z=n_z,
                mode='markers',
                marker=dict(
                    size=4,
                    color='#4169E1',  # Royal blue
                    opacity=1.0,
                    line=dict(width=0)
                ),
                name='Nitrogen Atoms',
                opacity=1.0,
                text=n_text,
                hovertemplate='<b>%{text}</b><br>Element: Nitrogen<br><extra></extra>'
            ))
        
        # Oxygen atoms
        if oxygen_atoms:
            o_coords = [atom['coord'] for atom in oxygen_atoms]
            o_x, o_y, o_z = zip(*o_coords)
            o_text = [f"{atom['residue']}{atom['residue_id']}-{atom['name']}" for atom in oxygen_atoms]
            
            traces.append(go.Scatter3d(
                x=o_x, y=o_y, z=o_z,
                mode='markers',
                marker=dict(
                    size=4,
                    color='#DC143C',  # Crimson
                    opacity=1.0,
                    line=dict(width=0)
                ),
                name='Oxygen Atoms',
                opacity=1.0,
                text=o_text,
                hovertemplate='<b>%{text}</b><br>Element: Oxygen<br><extra></extra>'
            ))
        
        # Sulfur atoms
        if sulfur_atoms:
            s_coords = [atom['coord'] for atom in sulfur_atoms]
            s_x, s_y, s_z = zip(*s_coords)
            s_text = [f"{atom['residue']}{atom['residue_id']}-{atom['name']}" for atom in sulfur_atoms]
            
            traces.append(go.Scatter3d(
                x=s_x, y=s_y, z=s_z,
                mode='markers',
                marker=dict(
                    size=5,
                    color='#FFD700',  # Gold
                    opacity=1.0,
                    line=dict(width=0)
                ),
                name='Sulfur Atoms',
                opacity=1.0,
                text=s_text,
                hovertemplate='<b>%{text}</b><br>Element: Sulfur<br><extra></extra>'
            ))
        
        # Other atoms (metals, etc.)
        if other_atoms:
            other_coords = [atom['coord'] for atom in other_atoms]
            other_x, other_y, other_z = zip(*other_coords)
            other_text = [f"{atom['residue']}{atom['residue_id']}-{atom['name']}" for atom in other_atoms]
            
            traces.append(go.Scatter3d(
                x=other_x, y=other_y, z=other_z,
                mode='markers',
                marker=dict(
                    size=6,
                    color='#FF69B4',  # Hot pink
                    opacity=1.0,
                    line=dict(width=0)
                ),
                name='Other Atoms (Metals, etc.)',
                opacity=1.0,
                text=other_text,
                hovertemplate='<b>%{text}</b><br>Element: Other<br><extra></extra>'
            ))
        
        # Add covalent bonds between atoms
        all_atoms = carbon_atoms + nitrogen_atoms + oxygen_atoms + sulfur_atoms + other_atoms
        bond_coords = []
        
        for i, atom1 in enumerate(all_atoms):
            for j, atom2 in enumerate(all_atoms[i+1:], i+1):
                # Calculate distance between atoms
                distance = np.linalg.norm(np.array(atom1['coord']) - np.array(atom2['coord']))
                if distance < 2.0:  # Covalent bond distance
                    bond_coords.extend([atom1['coord'], atom2['coord']])
        
        if bond_coords:
            bond_x, bond_y, bond_z = zip(*bond_coords)
            traces.append(go.Scatter3d(
                x=bond_x, y=bond_y, z=bond_z,
                mode='lines',
                line=dict(color='rgba(50,50,50,0.5)', width=1),
                name='Covalent Bonds',
                opacity=0.5,
                showlegend=False
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title='ProteinScope 3D Structure - Atomic View',
            scene=dict(
                xaxis_title='X (Å)',
                yaxis_title='Y (Å)',
                zaxis_title='Z (Å)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
                aspectmode='cube',
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99, xanchor="left", x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)', borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_secondary_structure_visualization(self, structure):
        """Create secondary structure-focused visualization"""
        print("Creating SECONDARY STRUCTURE visualization")  # Debug log
        
        # Get secondary structure information
        secondary_structure = self.get_secondary_structure_info(structure)
        
        # Create traces for different secondary structure elements
        helix_coords = []
        sheet_coords = []
        coil_coords = []
        
        for residue in structure.get_residues():
            if residue.has_id('CA'):
                ca_atom = residue['CA']
                res_id = residue.get_id()[1]
                
                if res_id in secondary_structure:
                    ss_type = secondary_structure[res_id]
                    if ss_type == 'helix':
                        helix_coords.append(ca_atom.coord)
                    elif ss_type == 'sheet':
                        sheet_coords.append(ca_atom.coord)
                    else:
                        coil_coords.append(ca_atom.coord)
                else:
                    coil_coords.append(ca_atom.coord)
        
        traces = []
        
        # Helix traces (red)
        if helix_coords:
            helix_x, helix_y, helix_z = zip(*helix_coords)
            traces.append(go.Scatter3d(
                x=helix_x, y=helix_y, z=helix_z,
                mode='lines+markers',
                line=dict(color='#E74C3C', width=8),
                marker=dict(
                    size=6,
                    color='#E74C3C',
                    opacity=0.9
                ),
                name='Alpha Helices',
                opacity=0.9
            ))
        
        # Sheet traces (blue)
        if sheet_coords:
            sheet_x, sheet_y, sheet_z = zip(*sheet_coords)
            traces.append(go.Scatter3d(
                x=sheet_x, y=sheet_y, z=sheet_z,
                mode='lines+markers',
                line=dict(color='#3498DB', width=8),
                marker=dict(
                    size=6,
                    color='#3498DB',
                    opacity=0.9
                ),
                name='Beta Sheets',
                opacity=0.9
            ))
        
        # Coil traces (gray)
        if coil_coords:
            coil_x, coil_y, coil_z = zip(*coil_coords)
            traces.append(go.Scatter3d(
                x=coil_x, y=coil_y, z=coil_z,
                mode='lines+markers',
                line=dict(color='#95A5A6', width=4),
                marker=dict(
                    size=4,
                    color='#95A5A6',
                    opacity=0.7
                ),
                name='Random Coil',
                opacity=0.7
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title='ProteinScope 3D Structure - Secondary Structure View',
            scene=dict(
                xaxis_title='X (Å)',
                yaxis_title='Y (Å)',
                zaxis_title='Z (Å)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
                aspectmode='cube',
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top", y=0.99, xanchor="left", x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)', borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_secondary_structure_info(self, structure):
        """Get secondary structure information for each residue"""
        # Improved secondary structure assignment based on phi/psi angles
        secondary_structure = {}
        residues = list(structure.get_residues())
        
        for i, residue in enumerate(residues):
            if residue.id[0] == ' ':  # Only amino acid residues
                res_id = residue.get_id()[1]
                
                # Get CA atom for this residue
                if residue.has_id('CA'):
                    ca_atom = residue['CA']
                    
                    # Look for patterns in nearby residues
                    helix_count = 0
                    sheet_count = 0
                    
                    # Check nearby residues for secondary structure patterns
                    for j in range(max(0, i-2), min(len(residues), i+3)):
                        if j != i and residues[j].id[0] == ' ':
                            other_ca = residues[j]['CA']
                            distance = np.linalg.norm(ca_atom.coord - other_ca.coord)
                            
                            # Helix pattern: residues ~5.5Å apart
                            if 4.5 < distance < 6.5:
                                helix_count += 1
                            # Sheet pattern: residues ~6.5Å apart
                            elif 5.5 < distance < 7.5:
                                sheet_count += 1
                    
                    # Assign secondary structure based on patterns
                    if helix_count >= 2:
                        secondary_structure[res_id] = 'helix'
                    elif sheet_count >= 2:
                        secondary_structure[res_id] = 'sheet'
                    else:
                        secondary_structure[res_id] = 'coil'
                else:
                    secondary_structure[res_id] = 'coil'
        
        return secondary_structure
    
    def get_protein_info(self, structure):
        """Get comprehensive protein information"""
        mw, atom_count = self.calculate_molecular_weight(structure)
        charge = self.calculate_charge(structure)
        
        # Count residues
        residue_count = 0
        unique_residues = set()
        for residue in structure.get_residues():
            if residue.id[0] == ' ':  # Only amino acid residues
                residue_count += 1
                unique_residues.add(residue.resname)
        
        return {
            'molecular_weight': mw,
            'atom_count': atom_count,
            'residue_count': residue_count,
            'unique_residues': len(unique_residues),
            'charge': charge,
            'residue_types': list(unique_residues)
        }

analyzer = ProteinAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_protein():
    data = request.get_json()
    pdb_id = data.get('pdb_id', '').strip().upper()
    viz_mode = data.get('viz_mode', 'backbone')  # Default to backbone mode
    
    print(f"Received request for PDB: {pdb_id}, mode: {viz_mode}")  # Debug log
    
    if not pdb_id:
        return jsonify({'error': 'Please provide a PDB ID'}), 400
    
    # Fetch PDB data
    pdb_data = analyzer.fetch_pdb(pdb_id)
    if not pdb_data:
        return jsonify({'error': f'Could not fetch PDB structure for {pdb_id}'}), 400
    
    # Parse structure
    structure = analyzer.parse_structure(pdb_data)
    if not structure:
        return jsonify({'error': 'Could not parse PDB structure'}), 400
    
    # Get protein information
    protein_info = analyzer.get_protein_info(structure)
    
    # Create 3D visualization
    try:
        plot_data = analyzer.create_3d_visualization(structure, viz_mode)
    except Exception as e:
        plot_data = None
        print(f"Error creating visualization: {e}")
    
    return jsonify({
        'pdb_id': pdb_id,
        'protein_info': protein_info,
        'plot_data': plot_data,
        'viz_mode': viz_mode
    })

@app.route('/examples')
def get_examples():
    """Return list of example PDB IDs"""
    examples = [
        {'id': '1HHB', 'name': 'Hemoglobin', 'description': 'Oxygen transport protein'},
        {'id': '1UBQ', 'name': 'Ubiquitin', 'description': 'Small regulatory protein'},
        {'id': '1CRN', 'name': 'Crambin', 'description': 'Plant seed protein'},
        {'id': '1GFL', 'name': 'Green Fluorescent Protein', 'description': 'Fluorescent protein'},
        {'id': '1TIM', 'name': 'Triosephosphate Isomerase', 'description': 'Enzyme'}
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 