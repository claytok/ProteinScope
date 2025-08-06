// ProteinScope - JavaScript

class ProteinVisualizer {
    constructor() {
        // Configure backend URL - change this for deployment
        this.backendUrl = this.getBackendUrl();
        this.initializeElements();
        this.bindEvents();
        this.checkBackendStatus();
        this.loadExamples();
    }

    getBackendUrl() {
        // For local development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8080';
        }
        
        // For Netlify deployment - use the serverless function
        return '/.netlify/functions/api';
    }

    initializeElements() {
        this.pdbInput = document.getElementById('pdbInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        this.examplesGrid = document.getElementById('examplesGrid');
        this.plotContainer = document.getElementById('plotContainer');
        
        // Optional elements that might not exist in static version
        this.backendStatus = document.getElementById('backendStatus');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        
        // Info card elements
        this.molecularWeight = document.getElementById('molecularWeight');
        this.atomCount = document.getElementById('atomCount');
        this.residueCount = document.getElementById('residueCount');
        this.charge = document.getElementById('charge');
        this.proteinName = document.getElementById('proteinName');
        this.residueList = document.getElementById('residueList');
        this.errorMessage = document.getElementById('errorMessage');
    }

    bindEvents() {
        // Analyze button click
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeProtein();
        });

        // Enter key in input field
        this.pdbInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeProtein();
            }
        });

        // Input field focus
        this.pdbInput.addEventListener('focus', () => {
            this.pdbInput.parentElement.style.transform = 'scale(1.02)';
        });

        this.pdbInput.addEventListener('blur', () => {
            this.pdbInput.parentElement.style.transform = 'scale(1)';
        });

        // Visualization mode buttons
        this.bindVisualizationModeButtons();
    }

    bindVisualizationModeButtons() {
        const modeButtons = document.querySelectorAll('.viz-mode-btn');
        
        modeButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Add loading state
                button.style.opacity = '0.6';
                button.style.pointerEvents = 'none';
                
                // Remove active class from all buttons
                modeButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                button.classList.add('active');
                
                // Get the mode
                const mode = button.getAttribute('data-mode');
                
                // If we have current plot data, request new visualization from backend
                if (this.currentPdbId) {
                    this.analyzeProteinWithMode(mode);
                }
                
                // Remove loading state after a short delay
                setTimeout(() => {
                    button.style.opacity = '1';
                    button.style.pointerEvents = 'auto';
                }, 300);
            });
        });
    }

    async checkBackendStatus() {
        // Skip backend status check if elements don't exist (static version)
        if (!this.backendStatus || !this.statusDot || !this.statusText) {
            return;
        }
        
        try {
            const response = await fetch(`${this.backendUrl}/examples`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                this.statusDot.className = 'status-dot connected';
                this.statusText.textContent = 'Backend connected';
                this.backendStatus.style.display = 'none'; // Hide if connected
            } else {
                this.statusDot.className = 'status-dot disconnected';
                this.statusText.textContent = 'Backend unavailable';
            }
        } catch (error) {
            this.statusDot.className = 'status-dot disconnected';
            this.statusText.textContent = 'Backend unavailable';
            console.warn('Backend not available:', error);
        }
    }

    async loadExamples() {
        // For static version, always use fallback examples
        if (this.backendUrl.includes('netlify')) {
            this.renderExamples([
                {id: '1HHB', name: 'Hemoglobin', description: 'Oxygen transport protein'},
                {id: '1UBQ', name: 'Ubiquitin', description: 'Small regulatory protein'},
                {id: '1CRN', name: 'Crambin', description: 'Plant seed protein'},
                {id: '1GFL', name: 'Green Fluorescent Protein', description: 'Fluorescent protein'},
                {id: '1TIM', name: 'Triosephosphate Isomerase', description: 'Enzyme'}
            ]);
            return;
        }
        
        try {
            const response = await fetch(`${this.backendUrl}/examples`);
            const examples = await response.json();
            this.renderExamples(examples);
        } catch (error) {
            console.error('Error loading examples:', error);
            // Fallback examples if backend is unavailable
            this.renderExamples([
                {id: '1HHB', name: 'Hemoglobin', description: 'Oxygen transport protein'},
                {id: '1UBQ', name: 'Ubiquitin', description: 'Small regulatory protein'},
                {id: '1CRN', name: 'Crambin', description: 'Plant seed protein'},
                {id: '1GFL', name: 'Green Fluorescent Protein', description: 'Fluorescent protein'},
                {id: '1TIM', name: 'Triosephosphate Isomerase', description: 'Enzyme'}
            ]);
        }
    }

    renderExamples(examples) {
        this.examplesGrid.innerHTML = '';
        
        examples.forEach(example => {
            const exampleCard = document.createElement('div');
            exampleCard.className = 'example-card fade-in';
            exampleCard.innerHTML = `
                <div class="example-id">${example.id}</div>
                <div class="example-name">${example.name}</div>
                <div class="example-desc">${example.description}</div>
            `;
            
            exampleCard.addEventListener('click', () => {
                this.pdbInput.value = example.id;
                this.analyzeProtein();
            });
            
            this.examplesGrid.appendChild(exampleCard);
        });
    }

    async analyzeProtein() {
        const pdbId = this.pdbInput.value.trim().toUpperCase();
        
        if (!pdbId) {
            this.showError('Please enter a PDB ID');
            return;
        }

        this.setLoading(true);
        this.hideError();
        this.hideResults();

        // Get current visualization mode
        const activeButton = document.querySelector('.viz-mode-btn.active');
        const vizMode = activeButton ? activeButton.getAttribute('data-mode') : 'backbone';

        try {
            const response = await fetch(`${this.backendUrl}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    pdb_id: pdbId,
                    viz_mode: vizMode
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'An error occurred while analyzing the protein');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError(`Network error: ${error.message}. Please check if the backend is running.`);
        } finally {
            this.setLoading(false);
        }
    }

    async analyzeProteinWithMode(mode) {
        if (!this.currentPdbId) return;
        
        try {
            const response = await fetch(`${this.backendUrl}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    pdb_id: this.currentPdbId,
                    viz_mode: mode
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success && data.plot_data) {
                // Update only the visualization, not the entire results
                this.currentPlotData = data.plot_data;
                this.create3DVisualization(data.plot_data, mode);
            } else {
                console.error('Error switching visualization mode:', data.error);
            }
        } catch (error) {
            console.error('Error switching visualization mode:', error);
        }
    }

    displayResults(data) {
        const { pdb_id, protein_info, plot_data } = data;

        // Store current PDB ID for mode switching
        this.currentPdbId = pdb_id;

        // Update protein name
        this.proteinName.textContent = pdb_id;

        // Update info cards with animation
        this.animateValue(this.molecularWeight, protein_info.molecular_weight);
        this.animateValue(this.atomCount, protein_info.atom_count);
        this.animateValue(this.residueCount, protein_info.residue_count);
        this.animateValue(this.charge, protein_info.charge);

        // Update residue list
        this.updateResidueList(protein_info.residue_types);

        // Create 3D visualization
        if (plot_data) {
            console.log('Received plot_data:', plot_data);
            this.currentPlotData = plot_data;
            this.create3DVisualization(plot_data, 'backbone'); // Default to backbone mode
        } else {
            console.error('No plot_data received from API');
            this.plotContainer.innerHTML = `
                <div class="plot-placeholder">
                    <div class="placeholder-icon">⚠️</div>
                    <p>No visualization data received</p>
                </div>
            `;
        }

        // Show results with animation
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // Scroll to results
        setTimeout(() => {
            this.resultsSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }

    animateValue(element, targetValue) {
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            
            element.textContent = this.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = this.formatNumber(targetValue);
            }
        };

        requestAnimationFrame(animate);
    }

    formatNumber(value) {
        if (typeof value === 'number') {
            if (value >= 1000) {
                return value.toLocaleString();
            }
            return value.toFixed(2);
        }
        return value;
    }

    updateResidueList(residues) {
        this.residueList.innerHTML = '';
        
        residues.forEach(residue => {
            const tag = document.createElement('span');
            tag.className = 'residue-tag fade-in';
            tag.textContent = residue;
            this.residueList.appendChild(tag);
        });
    }

    create3DVisualization(plotData, mode = 'backbone') {
        try {
            console.log('Creating 3D visualization with data:', plotData);
            
            // plotData is already a JavaScript object, no need to parse
            const plotConfig = plotData;
            
            // Validate plot data structure
            if (!plotConfig || !plotConfig.data || !plotConfig.layout) {
                throw new Error('Invalid plot data structure');
            }
            
            // Clear previous plot
            this.plotContainer.innerHTML = '';
            
            // Create new plot with the data from backend
            Plotly.newPlot(this.plotContainer, plotConfig.data, plotConfig.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false
            });
            
            // Update active button
            this.updateActiveModeButton(mode);
            
        } catch (error) {
            console.error('Error creating 3D visualization:', error);
            this.plotContainer.innerHTML = `
                <div class="plot-placeholder">
                    <div class="placeholder-icon">⚠️</div>
                    <p>Could not create 3D visualization</p>
                </div>
            `;
        }
    }

    updateActiveModeButton(mode) {
        const modeButtons = document.querySelectorAll('.viz-mode-btn');
        
        modeButtons.forEach(button => {
            button.classList.remove('active');
            if (button.getAttribute('data-mode') === mode) {
                button.classList.add('active');
            }
        });
    }

    setLoading(loading) {
        if (loading) {
            this.analyzeBtn.classList.add('loading');
            this.analyzeBtn.disabled = true;
        } else {
            this.analyzeBtn.classList.remove('loading');
            this.analyzeBtn.disabled = false;
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        this.errorSection.classList.add('fade-in');
        
        setTimeout(() => {
            this.errorSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }

    hideError() {
        this.errorSection.style.display = 'none';
        this.errorSection.classList.remove('fade-in');
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
        this.resultsSection.classList.remove('fade-in');
    }

    // Utility method to add smooth scrolling
    smoothScrollTo(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProteinVisualizer();
});

// Add some additional interactive features
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.info-card, .example-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Hide results/error sections
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('errorSection').style.display = 'none';
        }
    });

    // Add touch feedback for mobile
    if ('ontouchstart' in window) {
        const buttons = document.querySelectorAll('button, .example-card');
        buttons.forEach(button => {
            button.addEventListener('touchstart', () => {
                button.style.transform = 'scale(0.95)';
            });
            
            button.addEventListener('touchend', () => {
                button.style.transform = '';
            });
        });
    }
}); 