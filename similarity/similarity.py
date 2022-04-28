from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import altair as alt

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


def compare_businesses(df_reviews, df_business, business_id_1, business_id_2):
    """
    Returns an Altair plot comparing ratings of business 1 and business 2 over time
    :param df_reviews: reviews dataframe
    :param df_business: business dataframe
    :param business_id_1: own business
    :param business_id_2: competitor business
    :return: Interactive Altair chart
    """
    business_subset = df_reviews[df_reviews.business_id.isin([business_id_1, business_id_2])][['business_id', 'avg_stars', 'date']]
    business_subset = business_subset.merge(df_business, on="business_id", how="left")

    legend_selection = alt.selection_multi(fields=['name'], bind='legend')
    lines = alt.Chart(business_subset).mark_line().encode(
        alt.X('date:T', axis=alt.Axis(title='Date')),
        alt.Y('avg_stars:Q'),
        alt.Color('name:N'),
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
    ).properties(title="Comparison of Your Ratings with Your Competitors over Time")

    nearest_selector = alt.selection(type='single', nearest=True, on='mouseover',
                                     fields=['date'], empty='none')

    selectors = alt.Chart(business_subset).mark_point().encode(
        x='date:T',
        opacity=alt.value(0),
    ).add_selection(nearest_selector)

    points = lines.mark_point().encode(
        opacity=alt.condition(nearest_selector, alt.value(1), alt.value(0))
    )

    text = lines.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest_selector, 'avg_stars:Q', alt.value(' '))
    )

    rules = alt.Chart(business_subset).mark_rule(color='gray').encode(
        x='date:T',
    ).transform_filter(nearest_selector)

    layered_chart = alt.layer(
        lines, selectors, points, rules, text
    ).add_selection(
        legend_selection
    ).properties(
        width=400, height=300
    )

    return layered_chart