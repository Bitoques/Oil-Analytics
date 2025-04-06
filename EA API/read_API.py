import os
import pandas as pd

# this is the timeseries endpoint, which retrieves your
api_timeseries_endpoint = "https://api.energyaspects.com/data/timeseries/"

api_metadata_endpoint = "https://api.energyaspects.com/data/datasets/timeseries/"


def get_metadata(dataset_ids: list, api_key: str) -> pd.DataFrame:
    """
    Retrieves the metadata in a Dataframe for all the provided dataset ids.

    Args:
        dataset_ids: The dataset ids you want to retrieve metadata for

    Returns:
        The metadata in a pandas Data Frame
    """
    metadata_df = pd.DataFrame()
    for _id in dataset_ids:
        response = pd.read_json(api_metadata_endpoint + str(_id) + f'?api_key={api_key}')
        metadata_df[_id] = response.metadata
    metadata_df.loc["release_date", :] = metadata_df.apply(lambda col: col["release_dates"][-1])
    return metadata_df


def get_data_in_long_format(dataset_ids: list, api_key: str, file_format: str = "xlsx") -> pd.DataFrame:
    """
    Gets the data from the API for a given list of dataset ids and then combines with metadata in a long format.

    Args:
        dataset_ids: A list of the dataset ids you want to extract
        file_format: The API endpoint you want to use

    Returns:
        The combined dataset timeseries with the metadata in a long format
    """
    ids_str = ",".join([str(i) for i in dataset_ids])
    query = api_timeseries_endpoint + file_format + f"?api_key={api_key}&dataset_id={ids_str}"
    metadata = get_metadata(dataset_ids)
    if file_format == "xlsx":
        xlsx_header = "dataset_id"
        # this will set the header as the dataset_ids
        query = query + f"&xlsx_header={xlsx_header}"
        # reads the data and sets the dates to datetime object
        df = pd.read_excel(query, parse_dates=["Date"], sheet_name="Data")
        # melt the dataframe so that the dataset_ids are columns
        data_long = df.melt(id_vars="Date", value_name="value", var_name="dataset_id")
        # get the metadata with the dataset_id as a column
        metadata_transposed = metadata.T.reset_index().rename(columns={"index": "dataset_id"})
        # combine in a long format
        df = pd.merge(data_long, metadata_transposed, on="dataset_id", how="left")
    elif file_format == "csv":
        # this will be returned as a dataframe with the Descriptions as the columns. So you will need to merge on
        # description if you use CSV as an option for getting the data
        df = pd.read_csv(query, parse_dates=["Date"])
        # switching to long format
        data_long = df.melt(id_vars="Date", value_name="value", var_name="description")
        # transposing the metadata to merge on long dataframe
        metadata_transposed = metadata.T.reset_index().rename(columns={"index": "dataset_id"})
        # combining metadata and data in long format
        df = pd.merge(data_long, metadata_transposed, on="description", how="left")
    elif file_format == "json":
        # this will return it in a long format with the dates as columns and the metadata next to it.
        df = pd.read_json(query)
        # Reverts the json nested dictionaries for the metadata and data into columns
        df = pd.concat([df["dataset_id"], df.data.apply(pd.Series), df.metadata.apply(pd.Series)], axis=1)
        # Finds all the non timestamp columns.
        id_vars = [i for i in df.columns if not i[0].isdigit()]
        # Melts the dataframe in a long format.
        df = df.melt(id_vars=id_vars, value_name="value", var_name="Date")
    else:
        raise TypeError("Please provide a valid file format")
    # ensure that the forecast_start_date column is also a datetime.
    if "forecast_start_date" in df.columns:
        df.loc[:, "forecast_start_date"] = pd.to_datetime(df["forecast_start_date"])

    return df.sort_values(by=["dataset_id", "Date"])


def get_data(dataset_ids: list, api_key: str, file_format: str = "csv", dataset_id_as_header: bool = False) -> pd.DataFrame:
    """
    Gets the data from the API for a given list of dataset ids and then combines with metadata in a long format.
    Args:
        dataset_ids: A list of the dataset ids you want to extract
        file_format: The API endpoint you want to use
        dataset_id_as_header: If True make the dataset_id as the header. Only used in the csv/xlsx endpoints
    Returns:
        The combined dataset timeseries with the metadata in a wide format
    """
    ids_str = ",".join([str(i) for i in dataset_ids])
    # constructs the API url request link
    query = api_timeseries_endpoint + file_format + f"?api_key={api_key}&dataset_id={ids_str}"
    if file_format == "csv":
        if dataset_id_as_header:
            query += "&column_header=dataset_id"
        # reads the data and sets the dates to datetime object
        df = pd.read_csv(query, parse_dates=["Date"])
    elif file_format == "xlsx":
        if dataset_id_as_header:
            query += "&column_header=dataset_id"
        # reads the data and sets the dates to datetime object
        df = pd.read_excel(query, parse_dates=["Date"], sheet_name="Data")
    elif file_format == "json":
        # this will return it in a long format with the dates as columns and the metadata next to it.
        df = pd.read_json(query)
    else:
        raise TypeError("Please provide a valid file format")
    return df
