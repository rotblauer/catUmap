import argparse
import json
import sys

import geopandas
import umap as umap
import pandas


# example usage:
# python3 main.py --columns Name Activity --output output.csv < input.json

# parses an input stream of new line delimited json features
# extracts the columns of interest from the features
# creates a geopandas dataframe from the features
# returns a pandas dataframe
def parse_features(input_stream):
    # read a line from the input stream
    features = [json.loads(line) for line in input_stream]
    # create a pandas dataframe from the features
    df = geopandas.GeoDataFrame.from_features(features)
    # add lat and lon columns
    df['lat'] = df.geometry.y
    df['lon'] = df.geometry.x

    return df


# make sure that all columns of interest exist in the dataframe
def check_columns(columns, df):
    for column in columns:
        # if the column does not exist in the dataframe, throw an error
        if column not in df.columns:
            raise ValueError('Column ' + column + ' not found in dataframe')


# run UMAP on the columns of interest and the lat and lon columns
# returns a pandas dataframe with the UMAP results
# https://umap-learn.readthedocs.io/en/latest/embedding_space.html/
def run_umap(df, columns, metric, components):
    # create a new dataframe with just the columns of interest
    print("running umap on columns " + str(columns) + " and lat/lon")
    embedding = umap.UMAP(n_components=components, output_metric=metric,
                          verbose=True, n_jobs=8).fit_transform(
        df[columns + ['lat', 'lon']])

    # name the columns of the UMAP results
    for i in range(components):
        df['umap_' + str(i)] = embedding[:, i]
    return df


if __name__ == '__main__':
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description='Summarizes the tracks in a json file using UMAP on the columns of interest')
    # add the column argument with a default value
    parser.add_argument('--columns', nargs='+', default=[])
    # specify the output file
    parser.add_argument('--output', type=str, default='output/out.umap.tsv.gz')
    parser.add_argument('--metric', type=str, default='euclidean')  # 'euclidean' or 'haversine'
    parser.add_argument('--components', type=int, default=2)  # 2 or 3
    # parse the arguments
    args = parser.parse_args()
    iDf = parse_features(sys.stdin)
    check_columns(args.columns, iDf)
    oDf = run_umap(iDf, args.columns, args.metric, args.components)
    # write the dataframe to a tsv.gz file
    oDf.to_csv(args.output, sep='\t', compression='gzip', index=False)
