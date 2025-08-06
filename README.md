# ProteinScope

A modern, Apple-inspired web application for visualizing and analyzing protein structures from the Protein Data Bank (PDB). Built with Python Flask, BioPython, and Plotly for interactive 3D visualizations.

## 🧬 Features

### Core Functionality
- **3D Protein Visualization**: Interactive 3D plots using Plotly
- **Molecular Analysis**: Calculate molecular weight, charge, and structural properties
- **Real-time PDB Fetching**: Direct access to Protein Data Bank structures
- **Comprehensive Metrics**: Atom count, residue composition, and more

### Apple-Inspired Design
- **Clean Typography**: SF Pro Display font family
- **Subtle Animations**: Smooth transitions and hover effects
- **Glass Morphism**: Backdrop blur and translucent elements
- **Responsive Layout**: Optimized for all device sizes
- **Minimalist Interface**: Focus on content with elegant styling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
       git clone <repository-url>
    cd proteinscope
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8080`

## 🎯 How to Use

### Basic Usage
1. Enter a PDB ID (e.g., `1HHB` for hemoglobin)
2. Click "Analyze" or press Enter
3. View the 3D structure and protein properties

### Example Proteins
The app includes several example proteins to try:
- **1HHB**: Hemoglobin (oxygen transport)
- **1UBQ**: Ubiquitin (regulatory protein)
- **1CRN**: Crambin (plant protein)
- **1GFL**: Green Fluorescent Protein
- **1TIM**: Triosephosphate Isomerase (enzyme)

### Features Explained

#### 3D Visualization
- **Interactive Plot**: Rotate, zoom, and pan the protein structure
- **Color-coded Atoms**: Different elements shown in distinct colors
- **Responsive Design**: Works on desktop and mobile devices

#### Protein Analysis
- **Molecular Weight**: Calculated from atomic composition
- **Net Charge**: Estimated charge at pH 7.4
- **Residue Count**: Total amino acid residues
- **Atom Count**: Total number of atoms in structure

## 🛠 Technical Details

### Backend (Python/Flask)
- **BioPython**: Protein structure parsing and analysis
- **Plotly**: 3D visualization generation
- **Flask**: Web server and API endpoints
- **Requests**: PDB data fetching

### Frontend (HTML/CSS/JavaScript)
- **Vanilla JavaScript**: No framework dependencies
- **CSS Grid/Flexbox**: Modern layout techniques
- **Plotly.js**: Client-side 3D plotting
- **Responsive Design**: Mobile-first approach

### Key Components

#### ProteinAnalyzer Class
```python
class ProteinAnalyzer:
    def fetch_pdb(self, pdb_id)          # Fetch from PDB
    def parse_structure(self, pdb_data)   # Parse PDB format
    def calculate_molecular_weight(self)   # Calculate MW
    def calculate_charge(self)            # Estimate charge
    def create_3d_visualization(self)     # Generate 3D plot
```

#### Frontend JavaScript
```javascript
class ProteinVisualizer {
    async analyzeProtein()           # API communication
    displayResults(data)            # Update UI
    create3DVisualization(plotData) # Render 3D plot
    animateValue(element, value)    # Smooth animations
}
```

## 🎨 Design Philosophy

### Apple-Inspired Elements
- **Typography**: SF Pro Display for clean, readable text
- **Color Palette**: Subtle grays with blue accents
- **Shadows**: Soft, layered depth effects
- **Animations**: Smooth, purposeful transitions
- **Spacing**: Generous whitespace for clarity

### User Experience
- **Progressive Disclosure**: Information revealed as needed
- **Loading States**: Clear feedback during processing
- **Error Handling**: Helpful error messages
- **Accessibility**: Keyboard navigation and screen reader support

## 🔬 Scientific Accuracy

### Molecular Weight Calculation
Uses standard atomic weights:
- Carbon (C): 12.01 Da
- Nitrogen (N): 14.01 Da
- Oxygen (O): 16.00 Da
- Sulfur (S): 32.07 Da
- Hydrogen (H): 1.008 Da

### Charge Estimation
Simplified calculation at pH 7.4:
- **Positive**: Arginine (ARG), Lysine (LYS)
- **Negative**: Aspartic acid (ASP), Glutamic acid (GLU)
- **Neutral**: Histidine (HIS) - slightly positive

## 🚀 Performance Features

### Optimization
- **Lazy Loading**: 3D plots generated on-demand
- **Caching**: PDB data cached during session
- **Responsive Images**: Optimized for different screen sizes
- **Minimal Dependencies**: Lightweight, fast loading

### Browser Compatibility
- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Support**: Touch gestures and responsive design
- **Progressive Enhancement**: Works without JavaScript (basic features)

## 🔧 Customization

### Adding New Features
1. **Backend**: Extend `ProteinAnalyzer` class
2. **Frontend**: Add new UI components
3. **Styling**: Modify CSS variables for theming

### Example: Add Hydrophobicity Analysis
```python
def calculate_hydrophobicity(self, structure):
    # Add hydrophobicity calculation
    pass
```

## 📊 Comparison with PyMOL

### Advantages of This Tool
- **Web-based**: No installation required
- **Accessible**: Works on any device with a browser
- **Educational**: Simplified interface for learning
- **Customizable**: Easy to modify and extend
- **Modern UI**: Apple-inspired design aesthetic

### PyMOL Advantages
- **Professional-grade**: Industry standard
- **Advanced Features**: Complex analysis tools
- **Performance**: Optimized for large structures
- **Scripting**: Extensive automation capabilities

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ with consistent formatting
- **CSS**: BEM methodology for class names
- **Documentation**: Clear docstrings and comments

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **BioPython**: For protein structure handling
- **Plotly**: For 3D visualization capabilities
- **Protein Data Bank**: For structural data
- **Apple Design Guidelines**: For UI/UX inspiration

## 📞 Support

For questions or issues:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Include system information and error messages

---

**Built with ❤️ for the structural biology community** 