#######################################
#              ScanChIP-P             #
#         By: Ashley Doerfler         #
#######################################

from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt

def main():
    """
    Read inputs and creates output TADs
    """
    
    # Setup parser
    parser = setup_parser()
    args = parse_arguments(parser)
    
    # read HP contact matrix
    print("Read data")
    data = pd.read_csv(args.input, header=None, sep='\t')
    data = data.to_numpy()
    # print(data[1, :])
    
    window_length = len(data) // args.windowproportion
    # Create feature data from contact matrix with specified window size
    print("Create features")
    features = create_feature_data(data, window_length)
    
    # Cluster TADs
    print("Make clusters")
    clusters = DBSCAN(eps=k_distance(features, window_length), min_samples=min_pnts(args.minsize, args.binsize)).fit(data)
    print(clusters.labels_)

#######################################
#          Feature Extraction         #
#######################################
            
def create_feature_data(matrix, window_length):
    """
    Create a window for feature extraction to exclude a lot of the noise

    Args:
        matrix (np matrix): Contact Matrix
        window (float): Portion of the data to focus on

    Returns:
        array: Features, N_features = (2 * window_length) * len(matrix)
    """
    features = []

    for diag in range(0, len(matrix)):

        # Finds end position of window
        window = window_length + diag
        
    # Collect row and column features

        # If window is out of bounds
        if (window > len(matrix)):
            for i in range(0, window_length): 
                # rows
                for j in range(0, window_length):
                    # col
                    features.append(matrix[diag - i, diag - j])
        else:   
            for j in range(diag, window): 
                # rows
                for i in range(diag, window):
                    # col
                    features.append(matrix[i, j])
    # print(features, "length: ", len(features))
    return features

#######################################
#          DBScan Clustering          #
#######################################

def k_distance(features, window_length):
    """
    Calculate the k-distance for each window in the given features.

    Args:
        features (array): Features obtained from create_feature_data function.
        k (int): The desired distance (k) to calculate.

    Returns:
        array: The k-distances for each window.
    """
    num_windows = len(features) // (2 * window_length)
    k_distances = []

    for window_idx in range(num_windows):
        start_idx = window_idx * 2 * window_length
        end_idx = start_idx + 2 * window_length
        window_data = features[start_idx:end_idx]
        distance = np.linalg.norm(np.array(window_data[:-1]) - np.array(window_data[1:]))
        k_distances.append(distance)
    
    return find_elbow_point(k_distances)

def find_elbow_point(k_distances):
    """
    Find the elbow point in the k-distances curve using the elbow method.

    Args:
        k_distances (array): The k-distances obtained from the k_distance function.

    Returns:
        int: The index of the elbow point in the k-distances array.
    """
    distortions = []
    for i in range(1, len(k_distances)):
        # Calculate the squared distance between each k-distance and its previous one
        distortion = (k_distances[i] - k_distances[i - 1]) ** 2
        distortions.append(distortion)

    # Plot the distortions to find the elbow point
    plt.plot(range(1, len(k_distances)), distortions, marker='o')
    plt.xlabel('k')
    plt.ylabel('Distortion')
    plt.title('Elbow Method for Optimal k')
    plt.show()

    # Find the index of the elbow point where the slope starts to decrease significantly
    elbow_point_index = distortions.index(max(distortions))
    return elbow_point_index + 1  # Add 1 to get the actual k value for the elbow point

def min_pnts(min_tad_size, resolution):
    """
    Calculate min_points ~or~ min_bins (min tad size / bin resolution)

    Args:
        min_tad_size (_type_): Minimum size of a TAD default=120k
        resolution (_type_): Binsize default=40kb

    Returns:
        int: returns the amout of bins required to be considered a TAD
    """
    return min_tad_size // resolution

#######################################
#            Generate TADs            #
#######################################

def generate_tad():
    """
    Generate TADs based on how many bins are required for the minimum size of a TAD
    """
    return

#######################################
#        Evaluate TAD Quality         #
#######################################

def measure_of_concordance(tad_1, tad_2):
    """
    Computes the Measure of Concordance (MoC) between two sets of TAD regions.

    Parameters:
    tad_1 (list): The first set of TAD regions.
    tad_2 (list): The second set of TAD regions.

    Returns:
    float: The Measure of Concordance (MoC) between A and B.
    """
    n_tad_1 = len(tad_1)
    n_tad_2 = len(tad_2)

    sum_term = 0

    for i in range(n_tad_1):
        for j in range(n_tad_2):
            common_bins = len(set(tad_1[i]) & set(B[j]))
            sum_term += (common_bins ** 2) / (len(tad_1[i]) * len(tad_2[j]) - 1)

    moc = (1 / (n_tad_1 * n_tad_2 - 1)) * sum_term
    return moc


def modified_jaccard_index(tad_1, tad_2):
    """
    Computes the modified Jaccard's index between two sets of TAD boundaries.

    Parameters:
    tad_1 (set): The first set of TAD boundaries.
    tad_2 (set): The second set of TAD boundaries.

    Returns:
    float: The modified Jaccard's index between A and B.
    """
    intersecting_set = set()
    double_counted_boundaries = set()

    for boundary in tad_1:
        for offset in range(-1, 2):
            shifted_boundary = boundary + offset
            if shifted_boundary in tad_2:
                if shifted_boundary not in double_counted_boundaries:
                    intersecting_set.add(shifted_boundary)
                    double_counted_boundaries.add(shifted_boundary)

    union_size = len(tad_1) + len(tad_2) - len(intersecting_set)
    jaccard_index = len(intersecting_set) / union_size if union_size != 0 else 0

    return jaccard_index


def length_quality():
    """
    Find the quality of the TAD predictions based on length of the TADs
    """
    return

def amount_identified_quality():
    """
    Find the quality of the TAD predictions based on the number of identified TAD's
    """
    return

def interaction_quality():
    """
    Intra- and inter- Cluster (TAD) similarity
    """
    return

#######################################
#            Set Up Parser            #
#######################################
def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input contact matrix file', required=True)
    parser.add_argument('-w', '--windowproportion', help='window proportion', type=int)
    parser.add_argument('-m', '--minsize', help='minimum size of a TAD', default=120000, type=int)
    parser.add_argument('-b', '--binsize', help='bin size, default = 40000', default=40000, type=int)
    return parser

def parse_arguments(parser):
    args = parser.parse_args()
    print('Contact matrix specified:', args.input)
    print('Creating window:', 1 / args.windowproportion)
    print('Binsize:', args.binsize)
    print('Minimum TAD size', args.minsize)
    return args

main()