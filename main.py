import argparse
import json
import sys

import geopandas
import umap.umap_ as umap
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
def run_umap(df, columns):
    # create a new dataframe with just the columns of interest
    df = df[columns + ['lat', 'lon']]
    print("running umap on columns " + str(columns))
    # run UMAP on the dataframe
    # reducer = umap.UMAP()

    embedding = umap.UMAP(n_components=2).fit_transform(df)
    # create a new dataframe with the UMAP results
    umap_df = pandas.DataFrame(embedding, columns=['x', 'y'])
    # return the dataframe
    return umap_df


if __name__ == '__main__':
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description='Summarizes the tracks in a json file using UMAP on the columns of interest')
    # add the column argument with a default value
    parser.add_argument('--columns', nargs='+', default=['sSpeed'])

    # parse the arguments
    args = parser.parse_args()
    iDf = parse_features(sys.stdin)
    print(iDf.columns)
    print(args.columns)
    check_columns(args.columns, iDf)
    oDf = run_umap(iDf, args.columns)
    print(oDf)
