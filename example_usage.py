#!/usr/bin/env python3
"""
Example usage of the dimensionality reduction tools for catUmap.

This script demonstrates how to use the new dimensionality reduction techniques
with geospatial data from GeoJSON features.
"""

import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and print the output"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with return code: {result.returncode}")
        return False
    
    return True

def main():
    # Ensure we're in the right directory
    os.chdir('/home/runner/work/catUmap/catUmap')
    
    # Create output directory
    Path('output').mkdir(exist_ok=True)
    
    print("CATMAP DIMENSIONALITY REDUCTION EXAMPLE")
    print("This example demonstrates various dimensionality reduction techniques")
    print("that can be applied to geospatial tracking data.")
    
    # Step 1: Generate test data (simulating outputRaw from main.py)
    print("\n" + "="*60)
    print("STEP 1: Generating test geospatial data")
    print("="*60)
    
    run_command("python3 generate_test_data.py", "Generate sample geospatial data")
    
    # Step 2: Apply PCA and SVD (fast linear methods)
    print("\n" + "="*60)
    print("STEP 2: Applying fast linear dimensionality reduction (PCA + SVD)")
    print("="*60)
    
    cmd = ("python3 dimensionality_reduction.py "
           "--input output/test_raw.tsv.gz "
           "--output output/linear_methods.tsv.gz "
           "--columns lat lon Speed Elevation "
           "--methods pca svd "
           "--standardize "
           "--add_clusters --n_clusters 6")
    
    run_command(cmd, "Apply PCA and SVD with clustering")
    
    # Step 3: Apply ICA (for independent components)
    print("\n" + "="*60)
    print("STEP 3: Applying Independent Component Analysis (ICA)")
    print("="*60)
    
    cmd = ("python3 dimensionality_reduction.py "
           "--input output/test_raw.tsv.gz "
           "--output output/ica_method.tsv.gz "
           "--columns lat lon Speed "
           "--methods ica "
           "--standardize")
    
    run_command(cmd, "Apply ICA for independent components")
    
    # Step 4: Apply t-SNE (non-linear, good for visualization)
    print("\n" + "="*60)
    print("STEP 4: Applying t-SNE (non-linear visualization)")
    print("="*60)
    
    cmd = ("python3 dimensionality_reduction.py "
           "--input output/test_raw.tsv.gz "
           "--output output/tsne_method.tsv.gz "
           "--columns lat lon Speed "
           "--methods tsne "
           "--standardize "
           "--sample 2000 "  # Sample for faster t-SNE
           "--tsne_perplexity 50 "
           "--tsne_learning_rate 200")
    
    run_command(cmd, "Apply t-SNE with custom parameters")
    
    # Step 5: Create comprehensive analysis with all methods
    print("\n" + "="*60) 
    print("STEP 5: Comprehensive analysis with multiple methods")
    print("="*60)
    
    cmd = ("python3 dimensionality_reduction.py "
           "--input output/test_raw.tsv.gz "
           "--output output/comprehensive_analysis.tsv.gz "
           "--columns lat lon Speed Accuracy "
           "--methods pca svd ica "
           "--components 3 "  # 3D reduction
           "--standardize "
           "--add_clusters --n_clusters 8")
    
    run_command(cmd, "Comprehensive analysis with 3D reduction")
    
    # Step 6: Generate visualizations
    print("\n" + "="*60)
    print("STEP 6: Creating visualizations")
    print("="*60)
    
    # Plot linear methods
    cmd = ("python3 plot_dim_reduction.py "
           "--input output/linear_methods.tsv.gz "
           "--output output/linear_methods_plot.png "
           "--methods pca svd "
           "--color_by Activity")
    
    run_command(cmd, "Plot PCA and SVD results")
    
    # Plot comprehensive analysis
    cmd = ("python3 plot_dim_reduction.py "
           "--input output/comprehensive_analysis.tsv.gz "
           "--output output/comprehensive_plot.png "
           "--methods pca svd ica "
           "--color_by Name")
    
    run_command(cmd, "Plot comprehensive analysis results")
    
    # Plot t-SNE results
    cmd = ("python3 plot_dim_reduction.py "
           "--input output/tsne_method.tsv.gz "
           "--output output/tsne_plot.png "
           "--methods tsne "
           "--color_by Activity")
    
    run_command(cmd, "Plot t-SNE results")
    
    # Summary
    print("\n" + "="*60)
    print("EXAMPLE COMPLETED!")
    print("="*60)
    print("\nGenerated files:")
    print("- output/test_raw.tsv.gz (sample raw data)")
    print("- output/linear_methods.tsv.gz (PCA + SVD results)")
    print("- output/ica_method.tsv.gz (ICA results)")
    print("- output/tsne_method.tsv.gz (t-SNE results)")
    print("- output/comprehensive_analysis.tsv.gz (multiple methods)")
    print("\nGenerated plots:")
    print("- output/linear_methods_plot.png")
    print("- output/comprehensive_plot.png")
    print("- output/tsne_plot.png")
    
    print("\nNext steps:")
    print("1. Examine the generated plots to compare different methods")
    print("2. Use the clustering results for further analysis")
    print("3. Apply these techniques to your actual geospatial data")
    print("4. Experiment with different column combinations and parameters")

if __name__ == '__main__':
    main()