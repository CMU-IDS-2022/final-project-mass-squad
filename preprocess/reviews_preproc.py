import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--in-file", type=str)
parser.add_argument("--out-file", type=str)
parser.add_argument("--business-file", type=str)


def filter(in_file, out_file, business_ids):
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
