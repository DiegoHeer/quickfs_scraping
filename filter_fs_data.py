import numpy as np
import pymsgbox
from yahoofinancials import YahooFinancials

import web_scraping


# Formula for calculating compound growth rates
def cagr(future_value, current_value, time_period_years):
    if current_value > 0 and future_value > 0:
        return (future_value / current_value) ** (1 / time_period_years) - 1
    elif current_value < 0 and future_value < 0:
        return -((future_value / current_value) ** (1 / time_period_years) - 1)
    elif current_value < 0 and future_value > 0:
        return ((future_value - current_value) / abs(current_value)) ** (1 / time_period_years)
    elif current_value > 0 and future_value < 0:
        return ((future_value + 2 * abs(future_value)) / (current_value + 2 * abs(future_value))) ** (
                1 / time_period_years) - 1
    else:
        return 0


# Formula to calculate compound future values
def fv(current_value, interest_rate, time_period_years):
    if current_value < 0 and interest_rate > 0:
        return current_value * (interest_rate ** time_period_years)
    elif current_value < 0 and interest_rate < 0:
        return current_value * ((1 - interest_rate) ** time_period_years)
    else:
        return current_value * ((1 + interest_rate) ** time_period_years)


# Function to calculate all MOAT ratios
def get_moat_ratios(df, ticker):
    # Initialize a dictionary to store the MOAT numbers
    moat_dict = dict()

    # Obtain year list that is going to be used with the calculations
    year_list = list(df.columns.values)
    year_list.sort()

    # Inform user if company has less then 7 years of available stock data
    if len(year_list) <= 5:
        pymsgbox.alert(
            f"Be aware that {ticker} has less then 6 years of available stock data. The amount available is only "
            f"{len(year_list)}. The code cannot be further executed.")
        exit()

    # Calculate the ROIC
    # ROIC: Return on Invested Capital = NOPAT/Invested Capital
    # NOPAT: Net Operating Profit after Tax = Operating Profit * (1 - Tax Rate)
    # Tax Rate = abs(Income Tax)/Income before tax
    # Invested Capital = Interest Bearing Debt + Shareholders' Equity
    # Interest Bearing Debt = Short-Term Debt + Long-Term Debt

    # Input dictionaries
    operating_profit = df.loc['operating_income'].to_dict()
    income_tax = df.loc['income_tax'].to_dict()
    income_before_tax = df.loc['pretax_income'].to_dict()
    short_term_debt = df.loc['st_debt'].to_dict()
    long_term_debt = df.loc['lt_debt'].to_dict()
    shareholder_equity = df.loc['total_equity'].to_dict()
    # total_assets = df.loc['total_assets'].to_dict()

    # It should be noted that there is also an ROIC metric already available.
    # The calculated ROIC will be compared with that one
    roic_quickfs = df.loc['roic'].tolist()

    # Process list
    roic = list()

    # Calculations
    for year in year_list:
        if income_tax[year] == 0:
            tax_rate = 0
        else:
            tax_rate = abs(income_tax[year]) / income_before_tax[year]

        nopat = operating_profit[year] * (1 - tax_rate)
        interest_bearing_debt = short_term_debt[year] + long_term_debt[year]
        invested_capital = interest_bearing_debt + shareholder_equity[year]
        # invested_capital = total_assets[year]

        if abs(invested_capital) > 0:
            roic.append(nopat / invested_capital)
        else:
            roic.append(0)

    # Calculate the ROIC averages

    if len(year_list) < 10:
        max_roic_period = len(year_list)
    else:
        max_roic_period = 10

    moat_dict['ROIC'] = {}
    moat_dict['ROIC'][f'{max_roic_period}-year'] = np.mean(roic[-max_roic_period:])
    moat_dict['ROIC']['5-year'] = np.mean(roic[-5:])
    moat_dict['ROIC']['3-year'] = np.mean(roic[-3:])
    moat_dict['ROIC']['1-year'] = np.mean(roic[-1:])

    moat_dict['ROIC QuickFS'] = {}
    moat_dict['ROIC QuickFS'][f'{max_roic_period}-year'] = np.mean(roic_quickfs[-max_roic_period:])
    moat_dict['ROIC QuickFS']['5-year'] = np.mean(roic_quickfs[-5:])
    moat_dict['ROIC QuickFS']['3-year'] = np.mean(roic_quickfs[-3:])
    moat_dict['ROIC QuickFS']['1-year'] = np.mean(roic_quickfs[-1:])

    # Calculate all growth rates

    # maximum year period needs to be modified since the calculation of growth rates
    # depends on previous years for calculations
    if len(year_list) < 11:
        max_growth_period = len(year_list) - 1
    else:
        max_growth_period = 10

    # Input for Equity Growth Rate
    # BVPS: Book Value per Share = Book Value/Shares(Diluted)
    # Book Value = Shareholders' Equity

    book_value = shareholder_equity
    shares_diluted = df.loc['shares_diluted'].to_dict()
    bvps = list()

    # Calculations
    for year in year_list:
        bvps.append(book_value[year] / shares_diluted[year])

    # Book Value per Share calculated by QuickFS
    bvps_quickfs = df.loc['book_value_per_share'].tolist()

    # Input for EPS Growth Rate
    eps = df.loc['eps_diluted'].tolist()

    # Input for Sales Growth Rate
    # Sales = Revenue
    sales = df.loc['revenue'].tolist()

    # Input for Free Cash Flow Growth Rate
    # Free Cash Flow: FCF = OCF - PPE
    # OCF: Operating Cash Flow
    # PPE: Property, Plant & Equipment
    ocf = df.loc['cf_cfo'].to_dict()
    ppe = df.loc['cfi_ppe_net'].to_dict()
    fcf = list()

    for year in year_list:
        fcf.append(ocf[year] - abs(ppe[year]))

    # Free Cash Flow calculated by QuickFS
    fcf_quickfs = df.loc['fcf'].tolist()

    # Input for Operating Cash Flow Growth Rate
    # OCF: Operating Cash Flow
    ocf_list = df.loc['cf_cfo'].tolist()

    # Calculation of all growth rates
    key_list_growth_rates = ['Equity', 'Equity QuickFS', 'EPS', 'Sales', 'FCF', 'FCF QuickFS', 'OCF']
    value_list_growth_rates = [bvps, bvps_quickfs, eps, sales, fcf, fcf_quickfs, ocf_list]

    for i, value in enumerate(value_list_growth_rates):
        # Current value and max future value
        cv = value[-1]
        max_fv = value[-(1 + max_growth_period)]

        # Enter calculated growth rates in dictionary
        moat_dict[f'{key_list_growth_rates[i]} Growth Rate'] = {}
        moat_dict[f'{key_list_growth_rates[i]} Growth Rate'][f'{max_growth_period}-year'] = cagr(cv, max_fv,
                                                                                                  max_growth_period)
        moat_dict[f'{key_list_growth_rates[i]} Growth Rate']['5-year'] = cagr(value[-1], value[-6], 5)
        moat_dict[f'{key_list_growth_rates[i]} Growth Rate']['3-year'] = cagr(value[-1], value[-4], 3)
        moat_dict[f'{key_list_growth_rates[i]} Growth Rate']['1-year'] = cagr(value[-1], value[-2], 1)

    # Obtain the latest long-term debt and see if it can pay it back in at least 3 years with Free Cash Flow
    # current_debt = long_term_debt['TTM']
    current_debt = long_term_debt[list(long_term_debt)[-1]]
    current_fcf = fcf[-1]
    debt_fcf_ratio = abs(current_debt / current_fcf)

    if debt_fcf_ratio <= 3:
        debt_payoff_possible = True
    else:
        debt_payoff_possible = False

    moat_dict['Debt'] = {}
    moat_dict['Debt']['Current Long-Term Debt'] = current_debt
    moat_dict['Debt']['Debt Payoff Possible'] = debt_payoff_possible

    # Print all MOAT numbers
    print(f'All MOAT numbers for {ticker}')

    print('-' * 100)

    print(f'ROIC {max_roic_period}-year average: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['ROIC'][f'{max_roic_period}-year'])))
    print('ROIC 5-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC']['5-year'])))
    print('ROIC 3-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC']['3-year'])))
    print('ROIC 1-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC']['1-year'])))

    print('-' * 100)

    print(f'ROIC QuickFS {max_roic_period}-year average: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['ROIC QuickFS'][f'{max_roic_period}-year'])))
    print('ROIC QuickFS 5-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC QuickFS']['5-year'])))
    print('ROIC QuickFS 3-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC QuickFS']['3-year'])))
    print('ROIC QuickFS 1-year average:  ' + str('{percent:.2%}'.format(percent=moat_dict['ROIC QuickFS']['1-year'])))

    print('-' * 100)

    print(f'Equity Growth Rate {max_growth_period}-year: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['Equity Growth Rate'][f'{max_growth_period}-year'])))
    print('Equity Growth Rate 5-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['Equity Growth Rate']['5-year'])))
    print('Equity Growth Rate 3-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['Equity Growth Rate']['3-year'])))
    print('Equity Growth Rate 1-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['Equity Growth Rate']['1-year'])))

    print('-' * 100)

    print(f'EPS Growth Rate {max_growth_period}-year: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['EPS Growth Rate'][f'{max_growth_period}-year'])))
    print('EPS Growth Rate 5-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['EPS Growth Rate']['5-year'])))
    print('EPS Growth Rate 3-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['EPS Growth Rate']['3-year'])))
    print('EPS Growth Rate 1-year:  ' + str(
        '{percent:.2%}'.format(percent=moat_dict['EPS Growth Rate']['1-year'])))

    print('-' * 100)

    print(f'Sales Growth Rate {max_growth_period}-year: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['Sales Growth Rate'][f'{max_growth_period}-year'])))
    print(
        'Sales Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['Sales Growth Rate']['5-year'])))
    print(
        'Sales Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['Sales Growth Rate']['3-year'])))
    print(
        'Sales Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['Sales Growth Rate']['1-year'])))

    print('-' * 100)

    print(f'FCF Growth Rate {max_growth_period}-year: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['FCF Growth Rate'][f'{max_growth_period}-year'])))
    print('FCF Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['FCF Growth Rate']['5-year'])))
    print('FCF Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['FCF Growth Rate']['3-year'])))
    print('FCF Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['FCF Growth Rate']['1-year'])))

    print('-' * 100)

    print(f'OCF Growth Rate {max_growth_period}-year: ' + str(
        '{percent:.2%}'.format(percent=moat_dict['OCF Growth Rate'][f'{max_growth_period}-year'])))
    print('OCF Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['OCF Growth Rate']['5-year'])))
    print('OCF Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['OCF Growth Rate']['3-year'])))
    print('OCF Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=moat_dict['OCF Growth Rate']['1-year'])))

    print('-' * 100)

    # print('Current Long-Term Debt: ' + str(rule1_dict['Debt']['Current Long-Term Debt']))
    print('Debt Payoff Possible: ' + str(moat_dict['Debt']['Debt Payoff Possible']))

    return moat_dict


def get_mos_ratio(df, moat_dict, ticker):
    # Calculate the Margin of Safety Number
    # MOS: Margin of Safety = 0.5 * Sticker Price
    # Sticker Price: The "intrinsic value" of the company
    # Sticker Price = Future Market Price / (1 + MARR) ^ Time(years)
    # Future Market Price = Future PE * Future EPS
    # MARR: Minimum Acceptable Rate of Return - For Rule Number #1 it's always 15%
    # Future PE: Future Price to Earnings Ratio = Min(Default PE, Average Historical PE)
    # Default PE: 2 * EPS Growth Rate * 100 (To remove percentage)
    # Average Historical PE: 10-year average of the last Price to Earnings Ratio
    # Future EPS = Current EPS * (1 + EPS Growth Rate) ^ Time(years)
    # EPS Growth Rate = Min(Equity Growth Rate, Analysts Estimated Growth Rate)
    # Equity Growth Rate = Average(10-year, 5-year, 3-year, and 1-year Equity Growth Rate)
    # Analyst Growth Rate: Data scraped from the internet
    # Current EPS: The TTM Earning Per Share
    # Time (year): For long term investing, it's always 10 years

    # Input:
    time = 10
    marr = 0.15

    # Calculations
    # Current (TTM) EPS from yahoo finance
    current_eps = YahooFinancials(ticker).get_earnings_per_share()

    if current_eps is None:
        current_eps = df.loc['eps_diluted'].tolist()[-1]

    # 5 Year growth rate (per annum) scraped from yahoo finance website
    analyst_growth_rate = web_scraping.scrape_yahoo_analyst_growth_rate(ticker)

    # Rest of the calculations described in the notes above
    equity_growth_rate = np.mean(list(moat_dict['Equity Growth Rate'].values()))
    eps_growth_rate = min([analyst_growth_rate, equity_growth_rate])
    future_eps = fv(current_eps, eps_growth_rate, time)
    average_historical_pe = float(np.mean(df.loc['price_to_earnings'].tolist()[-time:]))
    default_pe = 2 * eps_growth_rate * 100
    future_pe = min(default_pe, average_historical_pe)
    future_market_price = future_pe * future_eps
    sticker_price = future_market_price / ((1 + marr) ** time)
    margin_of_safety = 0.5 * sticker_price

    # Print all MOS calculations
    print('-' * 100)
    print('Current EPS: ' + str(round(margin_of_safety, 2)))
    print('Future EPS: ' + str(round(future_eps, 2)))
    print('Analyst Growth Rate: ' + str('{percent:.2%}'.format(percent=analyst_growth_rate)))
    print('Equity Growth Rate: ' + str('{percent:.2%}'.format(percent=equity_growth_rate)))
    print('EPS Growth Rate: ' + str('{percent:.2%}'.format(percent=eps_growth_rate)))
    print('Average Historical Price to Earnings Ratio: ' + str(round(average_historical_pe, 2)))
    print('Default Price to Earnings Ratio: ' + str(round(default_pe, 2)))
    print('Future Price to Earnings Ratio: ' + str(round(future_pe, 2)))
    print('Future Market Price: ' + str(round(future_market_price, 2)))
    print('Sticker Price: ' + str(round(sticker_price, 2)))
    print('Margin of Safety: ' + str(round(margin_of_safety, 2)))


def get_rule_number1_ratios(df, ticker):
    # Remove unnecessary columns from dataframe, including 'TTM'
    for header in df.columns.values:
        # if not header.isnumeric() and header != 'TTM' and header != 'Category':
        if not header.isnumeric() and header != 'API Parameter':
            del df[header]

    # Change API Parameter column to index
    df = df.set_index('API Parameter')

    # Execute the functions to obtain the ratios
    moat_dict = get_moat_ratios(df, ticker)
    get_mos_ratio(df, moat_dict, ticker)