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
    business_record = business_df[business_df.business_id == business_id]
    business_state = business_record.state.iloc[0]
    same_state_businesses_keep = business_df[business_df.state == business_state]
    sim = cosine_similarity(same_state_businesses_keep[bool_attrs].to_numpy(), business_record[bool_attrs].to_numpy()).squeeze()
    idx = np.argsort(sim)[::-1][0:n]
    return same_state_businesses_keep.iloc[idx,:]
