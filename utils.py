import pandas as pd
import numpy as np


def transform_spending_df(df, spending_range, growth_range):
    spend_col = "Average Government Expenditure as % of GDP ({0} - {1})".format(
        spending_range[0], spending_range[1]
    )
    growth_col = "Average percentage change in GDP per capita USD ({0} - {1})".format(
        growth_range[0], growth_range[1]
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
    y_title_no_brackets = "Average percentage change in GDP per capita USD"
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


def add_binned_columns(scatter_df, bin_groups):
    binned_data = []
    for (country, region), country_data in scatter_df.groupby(["Country", "Region"]):
        country_data["av_gov_exp_mp"] = np.nan
        country_data["av_gdp_change_mp"] = np.nan
        for mid_point, [lower, upper] in bin_groups.items():
            country_data["av_gov_exp_mp"] = np.where(
                country_data["Average Government Expenditure as % of GDP"].between(
                    lower, upper, inclusive="left"
                ),
                mid_point,
                country_data["av_gov_exp_mp"],
            )
            country_data["av_gdp_change_mp"] = np.where(
                country_data["av_gov_exp_mp"] == mid_point,
                country_data.loc[
                    country_data["av_gov_exp_mp"] == mid_point,
                    "Average percentage change in GDP per capita USD",
                ].mean(),
                country_data["av_gdp_change_mp"],
            )

        binned_data.append(country_data)

    # Create the binned dataframe using pd.DataFrame constructor
    binned_df = pd.concat(binned_data)
    return binned_df
