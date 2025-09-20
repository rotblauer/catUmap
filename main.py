import argparse
import json
import sys

import geopandas
import umap.umap_ as umap


# example usage:
# python3 main.py --columns Name Activity --output output.csv < input.json

# standardize the columns of interest to a mean of 0 and a standard deviation of 1
def standardize_columns(df, columns):
    # standardize the columns of interest to a mean of 0 and a standard deviation of 1
    new_columns = []
    for column in columns:
        new_column = column + '_standardized'
        df[new_column] = (df[column] - df[column].mean()) / df[column].std()
        new_columns.append(new_column)
    return df, new_columns


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
    # remove the geometry column
    df = df.drop(columns=['geometry'])
    return df


# run UMAP on the columns of interest and the lat and lon columns
# returns a pandas dataframe with the UMAP results
# https://umap-learn.readthedocs.io/en/latest/embedding_space.html/


def run_umap(df, columns, metric_umap, components, n_neighbors, n_epochs, standardize):
    operating_columns = columns + ['lat', 'lon']
    if standardize:
        print("standardizing columns " + str(operating_columns))
        df, operating_columns = standardize_columns(df, operating_columns)

    print("running umap on columns " + str(operating_columns) + " with metric " + metric_umap)
    embedding = umap.UMAP(n_components=components, output_metric=metric_umap,
                          verbose=True, low_memory=False, transform_seed=42, n_neighbors=n_neighbors,
                          n_epochs=n_epochs).fit_transform(
        df[operating_columns])

    # name the columns of the UMAP results
    for i in range(components):
        df['umap_' + metric_umap + str(i)] = embedding[:, i]
    return df


if __name__ == '__main__':
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description='Summarizes the tracks in a json file using UMAP on the columns of interest')
    # add the column argument with a default value
    parser.add_argument('--columns', nargs='+', default=[])
    parser.add_argument('--metrics', nargs='+', default=["euclidean", "haversine"])
    parser.add_argument('--components', type=int, default=2)  # 2 or 3
    # argument whether to save the raw data
    parser.add_argument('--outputRaw', type=str, default=None)
    parser.add_argument('--output', type=str, default='output/out.umap.tsv.gz')
    parser.add_argument('--n_neighbors', type=int, default=15)
    # add arument for n_epochs
    parser.add_argument('--n_epochs', type=int, default=200)
    # add flag whether to normalize the columns of interest
    parser.add_argument('--standardize', action='store_true')

    # parse the arguments
    args = parser.parse_args()

    iDf = parse_features(sys.stdin)
    if args.outputRaw is not None:
        # write the dataframe to a tsv.gz file
        iDf.to_csv(args.outputRaw, sep='\t', compression='gzip', index=False)
    print(args.metrics)
    # if metrics is "none", exit
    if args.metrics == ["none"]:
        sys.exit(0)

    for metric in args.metrics:
        iDf = run_umap(iDf, args.columns, metric, args.components, args.n_neighbors, args.n_epochs, args.standardize)
    # write the dataframe to a tsv.gz file
    iDf.to_csv(args.output, sep='\t', compression='gzip', index=False)
