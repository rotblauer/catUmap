#!/usr/bin/env python3
"""
Simple plotting script for dimensionality reduction results.
Creates scatter plots for PCA, t-SNE, SVD, and ICA results.
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_data(input_file):
    """Load the dimensionality reduction results"""
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file, sep='\t', compression='gzip')
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    return df

def create_plots(df, methods, color_by='Activity', output_file='plots.png', figsize=(16, 12)):
    """Create scatter plots for each dimensionality reduction method"""
    
    # Filter available methods
    available_methods = []
    for method in methods:
        x_col = f'{method}_0'
        y_col = f'{method}_1'
        if x_col in df.columns and y_col in df.columns:
            available_methods.append(method)
        else:
            print(f"Warning: Method '{method}' not found in data")
    
    if not available_methods:
        print("Error: No valid methods found in data")
        return
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("Set1")
    
    # Create subplots
    n_methods = len(available_methods)
    if n_methods == 1:
        fig, axes = plt.subplots(1, 1, figsize=figsize)
        axes = [axes]
    elif n_methods <= 4:
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()
    
    # Color mapping
    if color_by in df.columns:
        unique_colors = df[color_by].unique()
        color_map = dict(zip(unique_colors, sns.color_palette("Set1", len(unique_colors))))
        colors = [color_map[val] for val in df[color_by]]
    else:
        print(f"Warning: Color column '{color_by}' not found, using default colors")
        colors = 'blue'
    
    # Create plots for each method
    for i, method in enumerate(available_methods):
        x_col = f'{method}_0'
        y_col = f'{method}_1'
        
        ax = axes[i]
        
        # Create scatter plot
        if color_by in df.columns:
            for category in df[color_by].unique():
                mask = df[color_by] == category
                ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col], 
                          label=category, alpha=0.6, s=20)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        else:
            ax.scatter(df[x_col], df[y_col], alpha=0.6, s=20, color='blue')
        
        ax.set_xlabel(f'{method.upper()} Component 1')
        ax.set_ylabel(f'{method.upper()} Component 2')
        ax.set_title(f'{method.upper()} Dimensionality Reduction')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(available_methods), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    return fig

def print_summary(df, methods):
    """Print summary statistics for the dimensionality reduction results"""
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    for method in methods:
        x_col = f'{method}_0'
        y_col = f'{method}_1'
        
        if x_col in df.columns and y_col in df.columns:
            print(f"\n{method.upper()}:")
            print(f"  Component 1: mean={df[x_col].mean():.3f}, std={df[x_col].std():.3f}")
            print(f"  Component 2: mean={df[y_col].mean():.3f}, std={df[y_col].std():.3f}")
    
    # Clustering summary if available
    if 'kmeans_cluster' in df.columns:
        print(f"\nK-MEANS CLUSTERING:")
        cluster_counts = df['kmeans_cluster'].value_counts().sort_index()
        for cluster, count in cluster_counts.items():
            pct = 100 * count / len(df)
            print(f"  Cluster {cluster}: {count} points ({pct:.1f}%)")

def main():
    parser = argparse.ArgumentParser(
        description='Plot dimensionality reduction results'
    )
    
    parser.add_argument('--input', type=str, required=True,
                       help='Input TSV.gz file with dimensionality reduction results')
    parser.add_argument('--output', type=str, default='dim_reduction_plots.png',
                       help='Output plot file')
    parser.add_argument('--methods', nargs='+', 
                       choices=['pca', 'tsne', 'svd', 'ica'],
                       default=['pca', 'svd', 'ica'],
                       help='Methods to plot')
    parser.add_argument('--color_by', type=str, default='Activity',
                       help='Column to use for coloring points')
    parser.add_argument('--figsize', nargs=2, type=float, default=[16, 12],
                       help='Figure size (width height)')
    
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.input)
    
    # Create plots
    fig = create_plots(df, args.methods, args.color_by, args.output, tuple(args.figsize))
    
    # Print summary
    print_summary(df, args.methods)
    
    print(f"\nDone! Plot saved to {args.output}")

if __name__ == '__main__':
    main()