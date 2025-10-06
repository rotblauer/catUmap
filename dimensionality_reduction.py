#!/usr/bin/env python3
"""
Additional dimensionality reduction techniques for geospatial data.
Processes outputRaw files from main.py and applies various dimensionality reduction methods.

Supports: PCA, t-SNE, Truncated SVD, and other techniques for clustering millions of geojson features.
"""

import argparse
import sys
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA, TruncatedSVD, FastICA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings

# Suppress some common warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def standardize_columns(df, columns):
    """
    Standardize the specified columns to mean=0, std=1
    Returns the dataframe with new standardized columns and the list of new column names
    """
    scaler = StandardScaler()
    new_columns = []
    
    for column in columns:
        if column in df.columns:
            new_column = column + '_standardized'
            df[new_column] = scaler.fit_transform(df[[column]])
            new_columns.append(new_column)
        else:
            print(f"Warning: Column '{column}' not found in data")
    
    return df, new_columns


def run_pca(df, columns, components, standardize=True):
    """
    Apply Principal Component Analysis (PCA)
    Fast linear technique, good for initial exploration
    """
    operating_columns = columns.copy()
    
    if standardize:
        print(f"Standardizing columns for PCA: {operating_columns}")
        df, operating_columns = standardize_columns(df, operating_columns)
    
    print(f"Running PCA on columns: {operating_columns} with {components} components")
    
    pca = PCA(n_components=components, random_state=42)
    embedding = pca.fit_transform(df[operating_columns])
    
    # Add PCA results to dataframe
    for i in range(components):
        df[f'pca_{i}'] = embedding[:, i]
    
    # Print explained variance ratio
    explained_var = pca.explained_variance_ratio_
    total_explained = sum(explained_var)
    print(f"PCA explained variance ratio per component: {explained_var}")
    print(f"Total explained variance: {total_explained:.3f}")
    
    return df


def run_tsne(df, columns, components, standardize=True, perplexity=30, learning_rate=200, max_iter=1000):
    """
    Apply t-Distributed Stochastic Neighbor Embedding (t-SNE)
    Non-linear technique, excellent for visualization but slower
    """
    operating_columns = columns.copy()
    
    if standardize:
        print(f"Standardizing columns for t-SNE: {operating_columns}")
        df, operating_columns = standardize_columns(df, operating_columns)
    
    print(f"Running t-SNE on columns: {operating_columns} with {components} components")
    print(f"Parameters: perplexity={perplexity}, learning_rate={learning_rate}, max_iter={max_iter}")
    
    # For large datasets, we might want to sample first
    if len(df) > 10000:
        print(f"Large dataset ({len(df)} rows). Consider using --sample for faster t-SNE computation.")
    
    tsne = TSNE(n_components=components, perplexity=perplexity, 
                learning_rate=learning_rate, max_iter=max_iter, random_state=42, verbose=1)
    embedding = tsne.fit_transform(df[operating_columns])
    
    # Add t-SNE results to dataframe
    for i in range(components):
        df[f'tsne_{i}'] = embedding[:, i]
    
    return df


def run_truncated_svd(df, columns, components, standardize=True):
    """
    Apply Truncated Singular Value Decomposition (SVD)
    Very fast linear technique, excellent for large datasets
    """
    operating_columns = columns.copy()
    
    if standardize:
        print(f"Standardizing columns for Truncated SVD: {operating_columns}")
        df, operating_columns = standardize_columns(df, operating_columns)
    
    print(f"Running Truncated SVD on columns: {operating_columns} with {components} components")
    
    svd = TruncatedSVD(n_components=components, random_state=42)
    embedding = svd.fit_transform(df[operating_columns])
    
    # Add SVD results to dataframe
    for i in range(components):
        df[f'svd_{i}'] = embedding[:, i]
    
    # Print explained variance ratio
    explained_var = svd.explained_variance_ratio_
    total_explained = sum(explained_var)
    print(f"SVD explained variance ratio per component: {explained_var}")
    print(f"Total explained variance: {total_explained:.3f}")
    
    return df


def run_ica(df, columns, components, standardize=True):
    """
    Apply Independent Component Analysis (ICA)
    Good for finding independent source signals
    """
    operating_columns = columns.copy()
    
    if standardize:
        print(f"Standardizing columns for ICA: {operating_columns}")
        df, operating_columns = standardize_columns(df, operating_columns)
    
    print(f"Running ICA on columns: {operating_columns} with {components} components")
    
    ica = FastICA(n_components=components, random_state=42, max_iter=1000)
    embedding = ica.fit_transform(df[operating_columns])
    
    # Add ICA results to dataframe
    for i in range(components):
        df[f'ica_{i}'] = embedding[:, i]
    
    return df


def add_kmeans_clusters(df, columns, n_clusters=8, standardize=True):
    """
    Add K-means clustering results using the specified columns
    """
    operating_columns = columns.copy()
    
    if standardize:
        df_temp, operating_columns = standardize_columns(df.copy(), operating_columns)
    else:
        df_temp = df.copy()
    
    print(f"Running K-means clustering with {n_clusters} clusters on columns: {operating_columns}")
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(df_temp[operating_columns])
    
    df['kmeans_cluster'] = clusters
    
    return df


def load_data(input_file):
    """Load data from TSV.gz file"""
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file, sep='\t', compression='gzip')
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    return df


def main():
    parser = argparse.ArgumentParser(
        description='Apply various dimensionality reduction techniques to geospatial data'
    )
    
    # Input/Output arguments
    parser.add_argument('--input', type=str, required=True,
                       help='Input TSV.gz file (outputRaw from main.py)')
    parser.add_argument('--output', type=str, required=True,
                       help='Output TSV.gz file with dimensionality reduction results')
    
    # Column selection
    parser.add_argument('--columns', nargs='+', default=['lat', 'lon', 'Speed'],
                       help='Columns to use for dimensionality reduction')
    
    # Dimensionality reduction methods
    parser.add_argument('--methods', nargs='+', 
                       choices=['pca', 'tsne', 'svd', 'ica'],
                       default=['pca', 'svd'],
                       help='Dimensionality reduction methods to apply')
    
    # General parameters
    parser.add_argument('--components', type=int, default=2,
                       help='Number of components/dimensions to reduce to')
    parser.add_argument('--standardize', action='store_true',
                       help='Standardize columns before applying techniques')
    
    # Sampling for large datasets
    parser.add_argument('--sample', type=int, default=None,
                       help='Sample N rows for faster computation (useful for t-SNE)')
    
    # t-SNE specific parameters
    parser.add_argument('--tsne_perplexity', type=float, default=30,
                       help='t-SNE perplexity parameter')
    parser.add_argument('--tsne_learning_rate', type=float, default=200,
                       help='t-SNE learning rate')
    parser.add_argument('--tsne_max_iter', type=int, default=1000,
                       help='t-SNE maximum number of iterations')
    
    # Clustering
    parser.add_argument('--add_clusters', action='store_true',
                       help='Add K-means clustering results')
    parser.add_argument('--n_clusters', type=int, default=8,
                       help='Number of clusters for K-means')
    
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.input)
    
    # Check if required columns exist
    missing_columns = [col for col in args.columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns in data: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Sample data if requested
    if args.sample and args.sample < len(df):
        print(f"Sampling {args.sample} rows from {len(df)} total rows")
        df = df.sample(n=args.sample, random_state=42).reset_index(drop=True)
    
    # Apply dimensionality reduction methods
    for method in args.methods:
        print(f"\n{'='*50}")
        print(f"Applying {method.upper()}")
        print(f"{'='*50}")
        
        if method == 'pca':
            df = run_pca(df, args.columns, args.components, args.standardize)
        elif method == 'tsne':
            df = run_tsne(df, args.columns, args.components, args.standardize,
                         args.tsne_perplexity, args.tsne_learning_rate, args.tsne_max_iter)
        elif method == 'svd':
            df = run_truncated_svd(df, args.columns, args.components, args.standardize)
        elif method == 'ica':
            df = run_ica(df, args.columns, args.components, args.standardize)
    
    # Add clustering if requested
    if args.add_clusters:
        print(f"\n{'='*50}")
        print("Adding K-means clustering")
        print(f"{'='*50}")
        df = add_kmeans_clusters(df, args.columns, args.n_clusters, args.standardize)
    
    # Save results
    print(f"\nSaving results to: {args.output}")
    df.to_csv(args.output, sep='\t', compression='gzip', index=False)
    print(f"Final dataset has {len(df)} rows and {len(df.columns)} columns")
    print(f"New columns added: {[col for col in df.columns if any(method in col for method in args.methods)]}")


if __name__ == '__main__':
    main()