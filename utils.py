import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def transform_spending_df(df, spending_range, growth_range):
    spend_col = "Average Government Expenditure as % of GDP ({0} - {1})".format(
        spending_range[0], spending_range[1]
    )
    growth_col = (
        "Annualized percentage change in GDP per capita USD ({0} - {1})".format(
            growth_range[0], growth_range[1]
        )
    )

    average_spend_df = (
        (
            df.loc[
                df["Year"].isin(list(range(spending_range[0], spending_range[1] + 1))),
                :,
            ]
            .groupby(["Country"])["Government Expenditure (IMF, Wiki, Statistica)"]
            .mean()
        )
        .reset_index()
        .rename(columns={"Government Expenditure (IMF, Wiki, Statistica)": spend_col})
    )

    df = pd.merge(
        left=df,
        right=average_spend_df,
        left_on=["Country"],
        right_on=["Country"],
        how="outer",
    )

    # Fill NA values before calling pct_change using ffill()
    df["GDP per capita (OWiD)"] = df.groupby("Country")["GDP per capita (OWiD)"].ffill()

    df[growth_col] = df.groupby(["Country"])["GDP per capita (OWiD)"].pct_change(
        periods=(growth_range[1] - growth_range[0]), fill_method=None
    ) * (100 / (growth_range[1] - growth_range[0]))

    ### Filter to most recent growth range year
    df = df.loc[df["Year"] == growth_range[1]]
    return df, spend_col, growth_col


def get_scatter_df(df, long_range, sub_period):
    x_title_no_brackets = "Average Government Expenditure as % of GDP"
    y_title_no_brackets = "Annualized percentage change in GDP per capita USD"
    all_subperiod_df_list = []
    nPeriods = long_range[1] - (long_range[0] + sub_period) + 1
    for p in range(nPeriods):
        sg_range = (long_range[0] + p, long_range[0] + p + sub_period)
        subperiod_df, spend_col, growth_col = transform_spending_df(
            df=df, spending_range=sg_range, growth_range=sg_range
        )
        subperiod_df = subperiod_df.loc[
            :, ["Country", "Region", "Population", spend_col, growth_col]
        ].rename(
            columns={
                spend_col: x_title_no_brackets,
                growth_col: y_title_no_brackets,
            }
        )
        subperiod_df["start_year"] = sg_range[0]
        subperiod_df["end_year"] = sg_range[1]
        all_subperiod_df_list.append(subperiod_df)
    all_subperiod_df = pd.concat(all_subperiod_df_list).reset_index(drop=True)
    return all_subperiod_df


def make_region_avg_df(spending_df, weight_pop):
    if weight_pop:
        wm = lambda x: np.average(x, weights=spending_df.loc[x.index, "Population"])
        region_avg_spending_df = (
            spending_df.groupby(["Region", "Year"])
            .agg(
                **{
                    "Population": ("Population", "sum"),
                    "GDP per capita (OWiD)": ("GDP per capita (OWiD)", wm),
                    "Government Expenditure (IMF, Wiki, Statistica)": (
                        "Government Expenditure (IMF, Wiki, Statistica)",
                        wm,
                    ),
                }
            )
            .reset_index()
        )
    else:
        region_avg_spending_df = (
            spending_df.groupby(["Region", "Year"])
            .agg(
                {
                    "Population": "sum",
                    "GDP per capita (OWiD)": "mean",
                    "Government Expenditure (IMF, Wiki, Statistica)": "mean",
                }
            )
            .reset_index()
        )
    region_avg_spending_df["Country"] = region_avg_spending_df["Region"] + "_avg"
    return region_avg_spending_df


def create_country_group(
    df, countries, new_country_name, new_region_name, weight_pop=True
):
    # Filter the dataframe to include only the specified countries
    filtered_df = df[df["Country"].isin(countries)]

    # Find the overlapping years
    overlapping_years = set.intersection(
        *[
            set(filtered_df[filtered_df["Country"] == country]["Year"])
            for country in countries
        ]
    )

    # Filter the dataframe to include only the overlapping years
    filtered_df = filtered_df[filtered_df["Year"].isin(overlapping_years)]

    # Group by Year
    grouped = filtered_df.groupby("Year")

    # Calculate means based on pop_weight flag
    if weight_pop:
        # Weighted mean
        means = grouped.apply(
            lambda x: pd.Series(
                {
                    "GDP per capita (OWiD)": np.average(
                        x["GDP per capita (OWiD)"], weights=x["Population"]
                    ),
                    "Government Expenditure (IMF, Wiki, Statistica)": np.average(
                        x["Government Expenditure (IMF, Wiki, Statistica)"],
                        weights=x["Population"],
                    ),
                    "Population": x["Population"].sum(),
                }
            )
        )
    else:
        # Unweighted mean
        means = grouped.agg(
            {
                "GDP per capita (OWiD)": "mean",
                "Government Expenditure (IMF, Wiki, Statistica)": "mean",
                "Population": "sum",
            }
        )

    # Reset index to make Year a column
    means = means.reset_index()

    # Add new country information
    means["Country"] = new_country_name
    means["Region"] = new_region_name

    # Ensure the new dataframe has the same columns as the original
    for col in df.columns:
        if col not in means.columns:
            means[col] = None

    # Reorder columns to match the original dataframe
    means = means[df.columns]

    # Concatenate the new country data with the original dataframe
    result_df = pd.concat([df, means], ignore_index=True)

    return result_df


def add_binned_columns(scatter_df, bin_groups, filter_start_years=None):
    binned_data = []
    for (country, region), country_data in scatter_df.groupby(["Country", "Region"]):
        if filter_start_years:
            gdp_col = "av_gdp_change_mp_filtered"
        else:
            gdp_col = "av_gdp_change_mp"

        country_data["av_gov_exp_mp"] = np.nan
        country_data[gdp_col] = np.nan
        for mid_point, [lower, upper] in bin_groups.items():
            country_data["av_gov_exp_mp"] = np.where(
                country_data["Average Government Expenditure as % of GDP"].between(
                    lower, upper, inclusive="left"
                ),
                mid_point,
                country_data["av_gov_exp_mp"],
            )

            if filter_start_years:
                filter_cond = (country_data["av_gov_exp_mp"] == mid_point) & (
                    ~country_data["start_year"].isin(filter_start_years)
                )
            else:
                filter_cond = country_data["av_gov_exp_mp"] == mid_point

            country_data[gdp_col] = np.where(
                country_data["av_gov_exp_mp"] == mid_point,
                country_data.loc[
                    filter_cond,
                    "Annualized percentage change in GDP per capita USD",
                ].mean(),
                country_data[gdp_col],
            )

        binned_data.append(country_data)

    # Create the binned dataframe using pd.DataFrame constructor
    binned_df = pd.concat(binned_data)
    return binned_df


def add_kmeans_clusters(scatter_df, n_clusters):
    def cluster(X, n_clusters):
        k_means = KMeans(n_clusters=n_clusters, random_state=37)
        y = k_means.fit_predict(X)
        return y, k_means

    all_country_data = []
    for (country, region), country_data in scatter_df.groupby(["Country", "Region"]):
        if country != "G7":
            continue

        country_data = country_data.dropna(
            subset=[
                "Average Government Expenditure as % of GDP",
                "Annualized percentage change in GDP per capita USD",
            ]
        )
        arr = np.array(
            country_data.loc[
                :,
                [
                    "Average Government Expenditure as % of GDP",
                    "Annualized percentage change in GDP per capita USD",
                ],
            ]
        )
        culster_result = cluster(arr, n_clusters)[1]
        country_data.loc[:, "Cluster"] = culster_result.labels_
        country_data.loc[:, "centroid_x"] = culster_result.cluster_centers_[
            culster_result.labels_
        ][:, 0]
        country_data.loc[:, "centroid_y"] = culster_result.cluster_centers_[
            culster_result.labels_
        ][:, 1]
        all_country_data.append(country_data)

    clustered_df = pd.concat(all_country_data)

    return clustered_df


def add_line_of_best_fit(df, x_col, y_col, degree):
    coefficients = np.polyfit(df[x_col], df[y_col], degree)
    polynomial = np.poly1d(coefficients)
    df["line_of_best_fit"] = polynomial(df[x_col])
    return df


def add_moving_average(df, x_col, y_col, window):
    df["moving_average"] = df[y_col].rolling(window=window).mean()
    # First use backward fill to handle NaN values at the beginning
    df["moving_average"] = (
        df["moving_average"].fillna(method="bfill").fillna(method="ffill")
    )
    return df
