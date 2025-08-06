#!/usr/bin/env python3
"""
Simple test script for the Protein Structure Visualizer
"""

import requests
import json
import time

def test_app():
    """Test the Flask application endpoints"""
    base_url = "http://localhost:8080"
    
    print("🧬 Testing ProteinScope...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the app with: python app.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    # Test 2: Get examples
    try:
        response = requests.get(f"{base_url}/examples")
        if response.status_code == 200:
            examples = response.json()
            print(f"✅ Examples endpoint working - {len(examples)} examples loaded")
            for example in examples:
                print(f"   - {example['id']}: {example['name']}")
        else:
            print(f"❌ Examples endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing examples: {e}")
    
    # Test 3: Analyze a protein (1HHB - Hemoglobin)
    try:
        print("\n🔬 Testing protein analysis...")
        response = requests.post(
            f"{base_url}/analyze",
            json={"pdb_id": "1HHB"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Protein analysis successful!")
            print(f"   PDB ID: {data['pdb_id']}")
            print(f"   Molecular Weight: {data['protein_info']['molecular_weight']} Da")
            print(f"   Atoms: {data['protein_info']['atom_count']}")
            print(f"   Residues: {data['protein_info']['residue_count']}")
            print(f"   Charge: {data['protein_info']['charge']}")
            print(f"   3D Plot: {'✅' if data['plot_data'] else '❌'}")
        else:
            print(f"❌ Protein analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing protein analysis: {e}")
    
    print("\n🎉 Test completed!")
    print("🌐 Open http://localhost:8080 in your browser to use the application")

if __name__ == "__main__":
    test_app() 