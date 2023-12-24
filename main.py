import argparse
import json
import sys

import geopandas


# parses an input stream of new line delimited json features
# extracts the columns of interest from the features
# creates a geopandas dataframe from the features
# returns the geopandas dataframe
def parse_features(input_stream):
    # read a line from the input stream
    features = [json.loads(line) for line in input_stream]
    # create a pandas dataframe from the features
    df = geopandas.GeoDataFrame.from_features(features)
    # return the dataframe
    return df


if __name__ == '__main__':
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description='Summarizes the tracks in a json file using UMAP on the columns of interest')
    parsed = parse_features(sys.stdin)
    print(parsed)
    print(parsed.columns)
