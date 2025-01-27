from typing import List

import requests
from bs4 import BeautifulSoup
import pandas as pd


# Constants
HEADERS = [
    'Czas', 'Kurs (PLN/MWh)', 'Wolumen (Mwh)'
]


def scrape_tge_given_day(year: str, month: str, day: str, save_to_file: bool = False):
    """
    Scrape the TGE data for a given date
    :param year: string in format 'YYYY'
    :param month: string in format 'MM'
    :param day: string in format 'DD'
    :param save_to_file: if True, save the scraped data to a CSV file
    :return: DataFrame with the scraped data
    """
    if len(year) != 4 or len(month) != 2 or len(day) != 2:
        raise ValueError("Invalid date format")
    if int(month) < 1 or int(month) > 12:
        raise ValueError("Invalid month")
    if int(day) < 1 or int(day) > 31:
        raise ValueError("Invalid day")

    url = "https://tge.pl/energia-elektryczna-rdn-tge-base?date_start=" + year + "-" + month + "-" + day + '&iframe=1'
    print("==================================================================================================\n"
          "Scraping data from:", url)

    # Get the page content
    response = requests.get(url)
    response.raise_for_status()  # Raises an error if the request fails
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the elements that we will need to get the data from
    table = soup.find('div', class_='table-responsive wyniki-table-kontrakty-godzinowe').find('table')
    if table is None:
        raise ValueError("Table not found on the page.")

    # Parse the data rows
    data_rows = []
    for row in table.select("tbody tr"):
        data_cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
        data_rows.append(data_cells)

    # Create the DataFrame
    df = pd.DataFrame(data_rows, columns=HEADERS)

    # Clean the numeric columns by removing commas and converting to float
    for col in HEADERS[1:]:
        df[col] = df[col].str.replace(',', '.').apply(pd.to_numeric, errors='coerce')

    # Convert the 'Czas' column from 0-1, 1-2 to 00:00, 01:00 and add the scraped date
    df['Czas'] = df['Czas'].str.split('-').apply(lambda x: f'{int(x[0]):02d}:00')
    df['Czas'] = pd.to_datetime(year + month + day + df['Czas'], format='%Y%m%d%H:%M')

    if save_to_file:
        df.to_csv(f'tge_data_{year}_{month}_{day}.csv', index=False)

    return df


def scrape_tge_given_period(year: str, month: str, day: str, days: int, save_to_file: bool = False):
    """
    Scrape the TGE data for a given period
    :param year: string in format 'YYYY'
    :param month: string in format 'MM'
    :param day: string in format 'DD'
    :param days: number of days to scrape
    :param save_to_file: if True, save the scraped data to a CSV file
    :return: DataFrame with the scraped data
    """
    if days < 1:
        raise ValueError("Invalid number of days")

    # Create an empty DataFrame
    df = pd.DataFrame(columns=HEADERS)

    # Scrape the data for each day
    for i in range(days):
        date = pd.Timestamp(year + month + day) + pd.DateOffset(days=i)
        date_str = date.strftime('%Y-%m-%d')
        df_day = scrape_tge_given_day(date_str[:4], date_str[5:7], date_str[8:10])
        df = pd.concat([df, df_day], ignore_index=True)

    if save_to_file:
        df.to_csv(f'tge_data_{year}_{month}_{day}__{days}_days_perdiod.csv', index=False)

    return df


def load_data_from_csv(file_path: str):
    """
    Load data from a CSV file
    :param file_path: path to the CSV file
    :return: DataFrame with the data
    """
    df = pd.read_csv(file_path)
    df[HEADERS[0]] = pd.to_datetime(df[HEADERS[0]])
    return df


def cheapest_hour(df, price_column='Kurs (PLN/MWh)'):
    return df.loc[df[price_column].idxmin()][HEADERS[0]]


def n_cheapest_hours(df, top_n=5, price_column='Kurs (PLN/MWh)') -> List[int]:
    """
    Find the hours with the smallest prices to use energy from the grid.
    :param df: DataFrame with the energy prices
    :param top_n: Number of hours to select
    :param price_column: Name of the column with the prices
    :return: List of hours with the smallest prices
    """
    sorted_df = df.sort_values(by=price_column)
    return sorted_df.head(top_n)[HEADERS[0]].dt.hour.tolist()


def quantile_cheapest_hours(df, quantile=0.25, price_column='Kurs (PLN/MWh)') -> List[int]:
    """
    Find the hours with the smallest prices to use energy from the grid.
    :param df: DataFrame with the energy prices
    :param quantile: Quantile to select
    :param price_column: Name of the column with the prices
    :return: List of hours with the smallest prices
    """
    return df[df[price_column] <= df[price_column].quantile(quantile)][HEADERS[0]].dt.hour.tolist()


def expensive_hour(df, price_column='Kurs (PLN/MWh)'):
    return df.loc[df[price_column].idxmax()][HEADERS[0]]


def n_expensive_hours(df, top_n=5, price_column='Kurs (PLN/MWh)') -> List[int]:
    """
    Find the hours with the most expensive prices to sell energy to the grid.
    :param df: DataFrame with the energy prices
    :param top_n: Number of hours to select
    :param price_column: Name of the column with the prices
    :return: List of hours with the most expensive prices
    """
    sorted_df = df.sort_values(by=price_column, ascending=False)
    return sorted_df.head(top_n)[HEADERS[0]].dt.hour.tolist()


def quantile_expensive_hours(df, quantile=0.75, price_column='Kurs (PLN/MWh)') -> List[int]:
    """
    Find the hours with the most expensive prices to sell energy to the grid.
    :param df: DataFrame with the energy prices
    :param quantile: Quantile to select
    :param price_column: Name of the column with the prices
    :return: List of hours with the most expensive prices
    """
    return df[df[price_column] >= df[price_column].quantile(quantile)][HEADERS[0]].dt.hour.tolist()



def compare_prices_to_statistics(df, mean_price, std_dev_price, threshold=1.5, price_column='Kurs (PLN/MWh)'):
    """
    Compare the prices of a given day to the statistics (mean and standard deviation) of the prices up until the previous day.
    :param df: DataFrame with the energy prices for the given day
    :param mean_price: Mean price up until the previous day
    :param std_dev_price: Standard deviation of prices up until the previous day
    :param threshold: Number of standard deviations to consider as significant deviation
    :param price_column: Name of the column with the prices
    :return: Dictionary with lists of hours for cheapest and most expensive prices compared to the statistics
    """
    lower_bound = mean_price - threshold * std_dev_price
    upper_bound = mean_price + threshold * std_dev_price

    cheapest_hours = df[df[price_column] <= lower_bound][HEADERS[0]].dt.hour.tolist()
    expensive_hours = df[df[price_column] >= upper_bound][HEADERS[0]].dt.hour.tolist()

    return {
        'cheapest_hours': cheapest_hours,
        'expensive_hours': expensive_hours
    }

def average_price(df, price_column='Kurs (PLN/MWh)'):
    return df[price_column].mean()


def std_dev_price(df, price_column='Kurs (PLN/MWh)'):
    return df[price_column].std()


def quantile_price(df, quantile=0.5, price_column='Kurs (PLN/MWh)'):
    return df[price_column].quantile(quantile)



if __name__ == '__main__':
    df = load_data_from_csv('tge_data_2024_12_01__31_days_perdiod.csv')
    df['Czas'] = pd.to_datetime(df['Czas'])
    given_day = '2024-12-20'
    df_given_day = df[df['Czas'].dt.strftime('%Y-%m-%d') == given_day]
    df_before_given_day = df[df['Czas'] < given_day]
    print(df_given_day)
    print(df_before_given_day)
    mean_until_given_day = average_price(df_before_given_day)
    std_dev_until_given_day = std_dev_price(df_before_given_day)
    print('Mean price until the given day:', mean_until_given_day)
    print('Standard deviation of prices until the given day:', std_dev_until_given_day)
    print(
        'Cheapest and most expensive hours compared to the statistics:',
        compare_prices_to_statistics(
            df_given_day,
            mean_until_given_day,
            std_dev_until_given_day,
            1.5
        )
    )
    print('Chepest hours without statistics:', quantile_cheapest_hours(df_given_day))
    print('Most expensive hours without statistics:', quantile_expensive_hours(df_given_day))
