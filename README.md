# ProteinScope

A modern web application for 3D protein structure visualization and analysis using Flask and Plotly.

## 🚀 Features

### **4 Distinct Visualization Modes**
- **🔗 Backbone Mode**: Protein backbone with residue-type coloring and secondary structure highlighting
- **🧬 Secondary Structure Mode**: Focused view of helices, sheets, and coils with distinct colors
- **🌐 Surface Mode**: Surface-like representation with larger markers for molecular surface visualization
- **⚛️ Atoms Mode**: Detailed atomic view with element-specific colors and sizes

### **Advanced Protein Analysis**
- Real-time PDB structure retrieval
- Secondary structure detection and visualization
- Molecular weight and charge calculations
- Residue type analysis
- Interactive 3D plots with Plotly

### **Modern Web Interface**
- Responsive design for desktop and mobile
- Real-time visualization updates
- Interactive 3D protein viewer
- Clean, modern UI with smooth animations

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/claytok/ProteinScope.git
cd ProteinScope

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 app.py
```

The application will be available at `http://localhost:8080`

## 📦 Dependencies

- **Flask**: Web framework
- **Plotly**: Interactive 3D visualizations
- **BioPython**: Protein structure analysis
- **NumPy**: Numerical computations
- **Requests**: HTTP requests for PDB data

## 🎯 Usage

1. **Enter a PDB ID** (e.g., "1HHB" for hemoglobin)
2. **Select a visualization mode**:
   - **Backbone**: Best for overall structure overview
   - **Secondary**: Ideal for studying secondary structure elements
   - **Surface**: Great for surface analysis and interactions
   - **Atoms**: Detailed atomic-level examination
3. **Click "Analyze Protein"** to generate the 3D visualization
4. **Interact** with the 3D plot using mouse controls

## 🔧 Technical Details

### **Fixed Issues**
- ✅ **Visualization Mode Differentiation**: All four modes now produce distinctly different visualizations
- ✅ **Secondary Structure Detection**: Improved algorithm for realistic secondary structure assignment
- ✅ **Color Coding**: Element-specific and structure-specific color schemes
- ✅ **Performance**: Optimized rendering for large protein structures

### **Architecture**
- **Backend**: Flask REST API with BioPython integration
- **Frontend**: Modern HTML5/CSS3/JavaScript with Plotly.js
- **Data**: Real-time PDB data retrieval via BioPython
- **Visualization**: Interactive 3D plots with Plotly

## 🌐 Deployment

### Local Development
```bash
python3 app.py
```

### Production Deployment
The application includes deployment configurations for:
- Heroku (Procfile)
- Netlify (netlify.toml)
- Docker support

## 📊 Example PDB IDs

Try these popular protein structures:
- `1HHB` - Hemoglobin
- `1CRN` - Crambin
- `1UBQ` - Ubiquitin
- `1GFL` - Green fluorescent protein
- `1TIM` - Triosephosphate isomerase

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **BioPython** for protein structure analysis
- **Plotly** for interactive 3D visualizations
- **Flask** for the web framework
- **PDB** for providing protein structure data

---

**ProteinScope** - Making protein structure visualization accessible and interactive! 🧬✨ 