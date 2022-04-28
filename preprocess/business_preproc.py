import pandas as pd
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--in-file", type=str)
parser.add_argument("--out-file", type=str)

keep_attrs = ['business_id', 'name', 'address', 'city', 'state', 'postal_code',
              'latitude', 'longitude', 'stars', 'review_count', 'is_open', 'categories', 'attributes.WiFi']

bool_attrs = [
    'attributes.ByAppointmentOnly',
    'attributes.BusinessAcceptsCreditCards',
    'attributes.BikeParking',
    'attributes.CoatCheck',
    'attributes.RestaurantsTakeOut',
    'attributes.RestaurantsDelivery',
    'attributes.Caters',
    'attributes.WheelchairAccessible',
    'attributes.HappyHour',
    'attributes.OutdoorSeating',
    'attributes.HasTV',
    'attributes.RestaurantsReservations',
    'attributes.DogsAllowed',
    'attributes.GoodForKids',
    'attributes.BusinessAcceptsBitcoin',
]


def load_json(path):
    """
    Loads the business/reviews json
    :param path: path to json file
    :return: dataframe of business/reviews
    """
    f = open(path)
    data = [json.loads(line) for line in f]
    raw_business_df = pd.json_normalize(data, max_level=5)
    return raw_business_df


def clean_wifi(df):
    """
    Preprocess the WiFi attribute of the busienss dataframe
    :param df: the business dataframe
    :return: business dataframe with cleaned WiFi attribute
    """
    wifi_categories = {"u'free'": "'free'", "u'no'": "'no'", "u'paid'": "'paid'"}
    df['attributes.WiFi'] = df['attributes.WiFi'].replace(wifi_categories)
    df['attributes.WiFi'] = df['attributes.WiFi'].fillna("'no'")
    return df


def clean_categories(df):
    """
    Preprocess the categories attribute of the business dataframe
    :param df: business dataframe
    :return: business dataframe with cleaned category attribute
    """
    df['categories'] = df['categories'].apply(lambda x: str(x).split(','))
    return df


def clean_name(df):
    """
    Preprocess the name attribute of the business dataframe
    :param df: business dataframe
    :return: business dataframe with cleaned name attribute
    """
    df['name'] = df['name'].apply(lambda x: x.replace('"', ''))
    return df


def filter(df):
    """
    Retain only restaurant businesses that are open
    :param df: business dataframe
    :return: restaurant business dataframe
    """
    df = df[df['is_open'] == True]
    df = df[df.categories.notna()]
    df = df[df['categories'].str.contains("Restaurant|Restaurants|Food") == True]
    return df


def clean_bool(df):
    """
    Correctly format boolean attributes
    :param df: the business dataframe
    :return: the cleaned business dataframe
    """
    for attribute in bool_attrs:
        df[attribute] = df[attribute].replace({'False': 0, 'True': 1, False: 0, True: 1, 'None': 0})
    return df


if __name__ == "__main__":
    args = parser.parse_args()

    df = load_json(args.in_file)
    df = filter(df)
    df = clean_name(df)
    # df = clean_categories(df)  # Uncomment if you want to split categories into a list
    df = clean_wifi(df)

    df[bool_attrs] = df[bool_attrs].fillna(False)
    df = clean_bool(df)
    all_attrs = keep_attrs + bool_attrs
    df = df[all_attrs]

    df.to_csv(args.out_file, header=True)
