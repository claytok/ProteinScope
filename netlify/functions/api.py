import json
import os
import sys
from urllib.parse import parse_qs
import requests
from Bio import PDB
import plotly.graph_objects as go
import plotly.utils
import numpy as np

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProteinAnalyzer:
    def __init__(self):
        self.pdb_parser = PDB.PDBParser(QUIET=True)
        
    def fetch_pdb(self, pdb_id):
        """Fetch PDB structure from RCSB"""
        try:
            url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch PDB structure: {e}")
    
    def parse_structure(self, pdb_data):
        """Parse PDB data into BioPython structure"""
        try:
            # Create a temporary file-like object
            from io import StringIO
            pdb_file = StringIO(pdb_data)
            structure = self.pdb_parser.get_structure("protein", pdb_file)
            return structure
        except Exception as e:
            raise Exception(f"Failed to parse PDB structure: {e}")
    
    def calculate_molecular_weight(self, structure):
        """Calculate molecular weight from atomic composition"""
        atomic_weights = {
            'C': 12.01, 'N': 14.01, 'O': 16.00, 'S': 32.07, 'H': 1.008
        }
        
        total_weight = 0
        for atom in structure.get_atoms():
            element = atom.element
            if element in atomic_weights:
                total_weight += atomic_weights[element]
        
        return round(total_weight, 2)
    
    def calculate_charge(self, structure):
        """Estimate charge at pH 7.4"""
        # Simplified charge calculation
        charged_residues = {
            'ARG': 1, 'LYS': 1, 'HIS': 0.1,  # Positive
            'ASP': -1, 'GLU': -1  # Negative
        }
        
        total_charge = 0
        for residue in structure.get_residues():
            if residue.id[0] == ' ':  # Only amino acid residues
                res_name = residue.get_resname()
                if res_name in charged_residues:
                    total_charge += charged_residues[res_name]
        
        return round(total_charge, 1)
    
    def get_residue_composition(self, structure):
        """Get residue type composition"""
        residue_counts = {}
        for residue in structure.get_residues():
            if residue.id[0] == ' ':  # Only amino acid residues
                res_name = residue.get_resname()
                residue_counts[res_name] = residue_counts.get(res_name, 0) + 1
        
        return residue_counts
    
    def get_secondary_structure_info(self, structure):
        """Get secondary structure information for each residue"""
        # Simplified secondary structure assignment
        # In a real implementation, you'd use DSSP or similar
        secondary_structure = {}
        residue_count = 0
        
        for residue in structure.get_residues():
            if residue.id[0] == ' ':  # Only amino acid residues
                residue_count += 1
                res_id = residue.get_id()[1]
                
                # Simple heuristic: every 4th residue in a helix-like pattern
                if residue_count % 4 == 0:
                    secondary_structure[res_id] = 'helix'
                elif residue_count % 3 == 0:
                    secondary_structure[res_id] = 'sheet'
                else:
                    secondary_structure[res_id] = 'coil'
        
        return secondary_structure
    
    def create_3d_visualization(self, structure, mode='backbone'):
        """Create 3D visualization using Plotly with different modes"""
        print(f"Creating visualization with mode: {mode}")
        
        if mode == 'backbone':
            return self.create_backbone_visualization(structure)
        elif mode == 'surface':
            return self.create_surface_visualization(structure)
        elif mode == 'atoms':
            return self.create_atoms_visualization(structure)
        elif mode == 'secondary':
            return self.create_secondary_structure_visualization(structure)
        else:
            print(f"Unknown mode '{mode}', using backbone")
            return self.create_backbone_visualization(structure)
    
    def create_backbone_visualization(self, structure):
        """Create backbone-focused visualization"""
        print("Creating BACKBONE visualization")
        # Get secondary structure information
        secondary_structure = self.get_secondary_structure_info(structure)
        
        # Create backbone trace with secondary structure coloring
        ca_coords = []
        ca_colors = []
        
        for residue in structure.get_residues():
            if residue.has_id('CA'):
                ca_atom = residue['CA']
                ca_coords.append(ca_atom.coord)
                
                # Determine secondary structure color
                res_id = residue.get_id()[1]
                if res_id in secondary_structure:
                    ss_type = secondary_structure[res_id]
                    if ss_type == 'helix':
                        color = '#FF6B6B'  # Red for helices
                    elif ss_type == 'sheet':
                        color = '#4ECDC4'  # Teal for sheets
                    else:
                        color = '#95A5A6'  # Gray for coils
                else:
                    color = '#95A5A6'  # Default gray
                
                ca_colors.append(color)
        
        traces = []
        
        # Backbone trace
        if ca_coords:
            ca_x, ca_y, ca_z = zip(*ca_coords)
            traces.append(go.Scatter3d(
                x=ca_x, y=ca_y, z=ca_z,
                mode='markers+lines',
                marker=dict(
                    size=4,
                    color=ca_colors,
                    opacity=0.8
                ),
                line=dict(
                    color='#34495E',
                    width=2
                ),
                name='Backbone'
            ))
        
        # Create layout
        layout = go.Layout(
            title='Protein Backbone Structure',
            scene=dict(
                xaxis=dict(title='X (Å)'),
                yaxis=dict(title='Y (Å)'),
                zaxis=dict(title='Z (Å)')
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_surface_visualization(self, structure):
        """Create surface-focused visualization"""
        print("Creating SURFACE visualization")
        
        # Create a surface-like representation using alpha carbons only
        ca_coords = []
        ca_colors = []
        
        for residue in structure.get_residues():
            if residue.has_id('CA'):
                ca_atom = residue['CA']
                ca_coords.append(ca_atom.coord)
                ca_colors.append('#4ECDC4')  # Teal color for surface
        
        traces = []
        
        # Surface representation using alpha carbons
        if ca_coords:
            ca_x, ca_y, ca_z = zip(*ca_coords)
            traces.append(go.Scatter3d(
                x=ca_x, y=ca_y, z=ca_z,
                mode='markers',
                marker=dict(
                    size=8,  # Larger size for surface effect
                    color=ca_colors,
                    opacity=0.7,
                    symbol='sphere'
                ),
                name='Surface'
            ))
        
        # Create layout
        layout = go.Layout(
            title='Protein Surface Representation',
            scene=dict(
                xaxis=dict(title='X (Å)'),
                yaxis=dict(title='Y (Å)'),
                zaxis=dict(title='Z (Å)')
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_atoms_visualization(self, structure):
        """Create detailed atomic visualization"""
        print("Creating ATOMS visualization")
        
        # Create separate traces for different atom types
        carbon_atoms = []
        nitrogen_atoms = []
        oxygen_atoms = []
        sulfur_atoms = []
        other_atoms = []
        
        for atom in structure.get_atoms():
            coord = atom.coord
            if atom.element == 'C':
                carbon_atoms.append(coord)
            elif atom.element == 'N':
                nitrogen_atoms.append(coord)
            elif atom.element == 'O':
                oxygen_atoms.append(coord)
            elif atom.element == 'S':
                sulfur_atoms.append(coord)
            else:
                other_atoms.append(coord)
        
        traces = []
        
        # Carbon atoms (backbone and side chains)
        if carbon_atoms:
            c_x, c_y, c_z = zip(*carbon_atoms)
            traces.append(go.Scatter3d(
                x=c_x, y=c_y, z=c_z,
                mode='markers',
                marker=dict(size=3, color='#95A5A6', opacity=0.8),
                name='Carbon'
            ))
        
        # Nitrogen atoms
        if nitrogen_atoms:
            n_x, n_y, n_z = zip(*nitrogen_atoms)
            traces.append(go.Scatter3d(
                x=n_x, y=n_y, z=n_z,
                mode='markers',
                marker=dict(size=4, color='#3498DB', opacity=0.8),
                name='Nitrogen'
            ))
        
        # Oxygen atoms
        if oxygen_atoms:
            o_x, o_y, o_z = zip(*oxygen_atoms)
            traces.append(go.Scatter3d(
                x=o_x, y=o_y, z=o_z,
                mode='markers',
                marker=dict(size=4, color='#E74C3C', opacity=0.8),
                name='Oxygen'
            ))
        
        # Sulfur atoms
        if sulfur_atoms:
            s_x, s_y, s_z = zip(*sulfur_atoms)
            traces.append(go.Scatter3d(
                x=s_x, y=s_y, z=s_z,
                mode='markers',
                marker=dict(size=5, color='#F39C12', opacity=0.8),
                name='Sulfur'
            ))
        
        # Create layout
        layout = go.Layout(
            title='Protein Atomic Structure',
            scene=dict(
                xaxis=dict(title='X (Å)'),
                yaxis=dict(title='Y (Å)'),
                zaxis=dict(title='Z (Å)')
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_secondary_structure_visualization(self, structure):
        """Create secondary structure-focused visualization"""
        print("Creating SECONDARY STRUCTURE visualization")
        
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
        
        # Helix trace
        if helix_coords:
            h_x, h_y, h_z = zip(*helix_coords)
            traces.append(go.Scatter3d(
                x=h_x, y=h_y, z=h_z,
                mode='markers+lines',
                marker=dict(size=6, color='#E74C3C', opacity=0.8),
                line=dict(color='#C0392B', width=3),
                name='Helix'
            ))
        
        # Sheet trace
        if sheet_coords:
            s_x, s_y, s_z = zip(*sheet_coords)
            traces.append(go.Scatter3d(
                x=s_x, y=s_y, z=s_z,
                mode='markers+lines',
                marker=dict(size=6, color='#3498DB', opacity=0.8),
                line=dict(color='#2980B9', width=3),
                name='Sheet'
            ))
        
        # Coil trace
        if coil_coords:
            c_x, c_y, c_z = zip(*coil_coords)
            traces.append(go.Scatter3d(
                x=c_x, y=c_y, z=c_z,
                mode='markers+lines',
                marker=dict(size=4, color='#95A5A6', opacity=0.6),
                line=dict(color='#7F8C8D', width=1),
                name='Coil'
            ))
        
        # Create layout
        layout = go.Layout(
            title='Protein Secondary Structure',
            scene=dict(
                xaxis=dict(title='X (Å)'),
                yaxis=dict(title='Y (Å)'),
                zaxis=dict(title='Z (Å)')
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def handler(event, context):
    """Netlify serverless function handler"""
    
    # Parse the request
    if event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
            pdb_id = body.get('pdb_id', '').upper()
            viz_mode = body.get('viz_mode', 'backbone')
            
            if not pdb_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'PDB ID is required'})
                }
            
            # Initialize analyzer
            analyzer = ProteinAnalyzer()
            
            # Fetch and parse structure
            pdb_data = analyzer.fetch_pdb(pdb_id)
            structure = analyzer.parse_structure(pdb_data)
            
            # Calculate properties
            molecular_weight = analyzer.calculate_molecular_weight(structure)
            charge = analyzer.calculate_charge(structure)
            residue_composition = analyzer.get_residue_composition(structure)
            
            # Count atoms and residues
            atom_count = len(list(structure.get_atoms()))
            residue_count = len(list(structure.get_residues()))
            
            # Create visualization
            plot_data = analyzer.create_3d_visualization(structure, viz_mode)
            
            # Prepare response
            response_data = {
                'success': True,
                'protein_info': {
                    'molecular_weight': molecular_weight,
                    'charge': charge,
                    'atom_count': atom_count,
                    'residue_count': residue_count,
                    'residue_types': list(residue_composition.keys())
                },
                'plot_data': plot_data
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': str(e)})
            }
    
    elif event['httpMethod'] == 'OPTIONS':
        # Handle CORS preflight requests
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        } 