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
            .groupby(["Country"])["Government Expenditure (IMF & Wiki)"]
            .mean()
        )
        .reset_index()
        .rename(columns={"Government Expenditure (IMF & Wiki)": spend_col})
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
                    "Government Expenditure (IMF & Wiki)": (
                        "Government Expenditure (IMF & Wiki)",
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
                    "Government Expenditure (IMF & Wiki)": "mean",
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
                    "Government Expenditure (IMF & Wiki)": np.average(
                        x["Government Expenditure (IMF & Wiki)"],
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
                "Government Expenditure (IMF & Wiki)": "mean",
                "Population": "sum",
            }
        )

    # Reset index to make Year a column
    means = means.reset_index()

    # Add new country information
    means["Country"] = new_country_name
    means["Region"] = (
        new_region_name  # You might want to adjust this based on your needs
    )

    # Ensure the new dataframe has the same columns as the original
    for col in df.columns:
        if col not in means.columns:
            means[col] = None

    # Reorder columns to match the original dataframe
    means = means[df.columns]

    # Concatenate the new country data with the original dataframe
    result_df = pd.concat([df, means], ignore_index=True)

    return result_df


def calculate_generation_group_averages(scatter_df, generation_groups, filter_country=None):
    # Create a copy of the dataframe to avoid modifying the original
    df = scatter_df.copy()

    # Create a new column "Generation" based on the start_year
    df["Generation"] = pd.cut(
        df["start_year"],
        bins=[group[0] for group in generation_groups.values()]
        + [2020],  # Add upper bound
        labels=generation_groups.keys(),
        right=False,
    )

    # Group by "Country" and "Generation", and calculate the mean
    grouped = (
        df.groupby(["Country", "Generation"])
        .agg(
            {
                "Average Government Expenditure as % of GDP": "mean",
                "Average percentage change in GDP per capita USD": "mean",
            }
        )
        .reset_index()
    )

    # Rename columns for clarity
    grouped.columns = [
        "Country",
        "Generation",
        "Average Government Expenditure as % of GDP",
        "Average percentage change in GDP per capita USD",
    ]

    # Filter to only include the focus country if filter_country is specified
    if filter_country:
        df = df.loc[df["Country"] == filter_country, :]
        grouped = grouped.loc[grouped["Country"] == filter_country, :]

    # Add start_year and end_year columns to the grouped dataframe
    grouped["start_year"] = grouped["Generation"].map({k: v[0] for k, v in generation_groups.items()})
    grouped["end_year"] = grouped["Generation"].map({k: v[1] if len(v) > 1 else 2019 for k, v in generation_groups.items()})
    
    return df, grouped
