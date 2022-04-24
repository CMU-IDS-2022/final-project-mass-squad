from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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


def similarity(business_id, business_df, n):
    """
    Takes in the business id for which similarity scores must be computed and
    returns a subset of the business df containing the n most similar rows
    :param business_id: business id of the business to which similarity must be computed
    :param business_df: the business dataframe
    :param n: the number of most similar business
    :return: a pruned business df containing only businesses that are most similar to business with id business_id
    """
    business_record = business_df[business_df.business_id == business_id]
    business_state = business_record.state.iloc[0]
    same_state_businesses_keep = business_df[business_df.state == business_state]
    sim = cosine_similarity(same_state_businesses_keep[bool_attrs].to_numpy(),
                            business_record[bool_attrs].to_numpy()).squeeze()

    if len(sim) < n:
        idx = np.argsort(sim)[::-1]
    else:
        idx = np.argsort(sim)[::-1][0:n]
    return same_state_businesses_keep.iloc[idx, :]


def get_exclusive_attrs(business_id_1, business_id_2, business_df):
    """
    Returns boolean attribute names of business 2 that business 2 does not have
    :param business_id_1: own business
    :param business_id_2: competitior business
    :param business_df: business dataframe
    :return: a list of attribute names that business 2 has that business 1 does not
    """
    business_1 = business_df[business_df.business_id == business_id_1][bool_attrs]
    business_2 = business_df[business_df.business_id == business_id_2][bool_attrs]

    exclusive_attrs = []
    for attr in bool_attrs:
        if business_2[attr].iloc[0] == 1 and business_1[attr].iloc[0] == 0:
            exclusive_attrs.append(attr[attr.index('.')+1:])

    return exclusive_attrs
