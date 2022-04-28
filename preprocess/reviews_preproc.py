import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--in-file", type=str)
parser.add_argument("--out-file", type=str)
parser.add_argument("--business-file", type=str)


def filter(in_file, out_file, business_ids):
    """
    Retain only those reviews that correspond to businesses included in the cleaned business file
    :param in_file: the raw reviews file
    :param out_file: the file to which the cleaned reviews file must be written
    :param business_ids: the  business ids included in the cleaned business file
    :return: the cleaned reviews file
    """
    header = 1
    pruned_file = out_file
    for chunk in pd.read_json(in_file, chunksize=1000, lines=True):
        data = chunk[chunk.business_id.isin(business_ids)]
        data = data.drop(['useful', 'funny', 'cool', 'user_id', 'review_id'], axis=1)
        if (header):
            data.to_csv(pruned_file, mode='a')
            header = 0
        else:
            data.to_csv(pruned_file, mode='a', header=False)


if __name__ == "__main__":
    args = parser.parse_args()

    business_ids = list(pd.read_csv(args.business_file).business_id)
    filter(args.in_file, args.out_file, business_ids)
