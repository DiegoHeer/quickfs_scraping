import pandas as pd
import numpy as np
import openpyxl


def get_rule_number1_ratios(df, data_source):
    # Initialize a dictionary to store Rule #1 ratios
    rule1_dict = dict()

    # Remove unnecessary columns from dataframe, including 'TTM'
    for header in df.columns.values:
        # if not header.isnumeric() and header != 'TTM' and header != 'Category':
        if not header.isnumeric() and header != 'API Parameter':
            del df[header]

    # Change API Parameter column to index
    df = df.set_index('API Parameter')

    # Obtain year list that is going to be used with the calculations
    year_list = list(df.columns.values)
    year_list.sort()

    # Calculate first the MOAT numbers

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
    total_assets = df.loc['total_assets'].to_dict()

    # TODO: Continue here
    # if data_source == 'scraping':
    #     # Because the ROIC uses the income statement and balance sheet, and the income statement doesn't have a TTM
    #     # column, and the balance sheet doesn't have the first year, those elements will be removed from the year list.
    #     # Also, the standard maximum analysis years will be 9
    #     minimal_year_list = year_list[1:]
    #     minimal_year_list.remove('TTM')
    #     max_year = 9
    # else:
    #     minimal_year_list = year_list
    #     max_year = 10
    #
    # # Process list
    # roic = list()
    #
    # # Calculations
    # for year in minimal_year_list:
    #     tax_rate = abs(income_tax[year]) / income_before_tax[year]
    #     nopat = operating_profit[year] * (1 - tax_rate)
    #     interest_bearing_debt = short_term_debt[year] + long_term_debt[year]
    #     invested_capital = interest_bearing_debt + shareholder_equity[year]
    #     # invested_capital = total_assets[year]
    #
    #     roic.append(nopat / invested_capital)
    #
    # # Calculate the ROIC averages
    # rule1_dict['ROIC'] = {}
    # rule1_dict['ROIC']['10-year'] = np.mean(roic[-10:])
    # rule1_dict['ROIC']['5-year'] = np.mean(roic[-5:])
    # rule1_dict['ROIC']['3-year'] = np.mean(roic[-3:])
    # rule1_dict['ROIC']['1-year'] = np.mean(roic[-1:])
    #
    # # Calculate the Equity Growth Rate
    # # BVPS: Book Value per Share = Book Value/Shares(Diluted)
    # # Book Value = Shareholders' Equity
    #
    # # Input dictionaries
    # book_value = shareholder_equity
    # shares_diluted = df.loc[df['Category'] == "Shares (Diluted)"].to_dict('records')[0]
    #
    # # Process list
    # bvps = list()
    #
    # # Calculations
    # for year in minimal_year_list:
    #     bvps.append(book_value[year] / shares_diluted[year])
    #
    # # Calculate the equity growth numbers
    # # Growth rate formula: Growth Rate = (Future Value/Current Value)^(1/Time(years)) - 1
    # rule1_dict['Equity Growth Rate'] = {}
    # rule1_dict['Equity Growth Rate'][f'{max_year}-year'] = (bvps[-1] / bvps[-(1 + max_year)]) ** (1 / max_year) - 1
    # rule1_dict['Equity Growth Rate']['5-year'] = (bvps[-1] / bvps[-6]) ** (1 / 5) - 1
    # rule1_dict['Equity Growth Rate']['3-year'] = (bvps[-1] / bvps[-4]) ** (1 / 3) - 1
    # rule1_dict['Equity Growth Rate']['1-year'] = (bvps[-1] / bvps[-2]) ** (1 / 1) - 1
    #
    # # Input list
    # diluted_eps = df.loc[df['Category'] == "EPS (Diluted)"].values.flatten().tolist()[1:]
    #
    # # Calculate the EPS growth numbers
    # rule1_dict['EPS Growth Rate'] = {}
    # rule1_dict['EPS Growth Rate']['10-year'] = (diluted_eps[-1] / diluted_eps[-11]) ** (1 / 10) - 1
    # rule1_dict['EPS Growth Rate']['5-year'] = (diluted_eps[-1] / diluted_eps[-6]) ** (1 / 5) - 1
    # rule1_dict['EPS Growth Rate']['3-year'] = (diluted_eps[-1] / diluted_eps[-4]) ** (1 / 3) - 1
    # rule1_dict['EPS Growth Rate']['1-year'] = (diluted_eps[-1] / diluted_eps[-2]) ** (1 / 1) - 1
    #
    # # Calculate the Sales Growth Rate
    # # Sales = Revenue
    #
    # # Input list
    # sales = df.loc[df['Category'] == 'Revenue'].values.flatten().tolist()[1:]
    #
    # # Calculate the Sales growth numbers
    # rule1_dict['Sales Growth Rate'] = {}
    # rule1_dict['Sales Growth Rate']['10-year'] = (sales[-1] / sales[-11]) ** (1 / 10) - 1
    # rule1_dict['Sales Growth Rate']['5-year'] = (sales[-1] / sales[-6]) ** (1 / 5) - 1
    # rule1_dict['Sales Growth Rate']['3-year'] = (sales[-1] / sales[-4]) ** (1 / 3) - 1
    # rule1_dict['Sales Growth Rate']['1-year'] = (sales[-1] / sales[-2]) ** (1 / 1) - 1
    #
    # # Calculate Free Cash Flow Growth Rate
    # # Free Cash Flow: FCF = OCF - PPE
    # # OCF: Operating Cash Flow
    # # PPE: Property, Plant & Equipment
    #
    # # Input dictionaries
    # ocf = df_cf.loc[df_cf['Category'] == 'Cash From Operations'].to_dict('records')[0]
    # ppe = df_cf.loc[df_cf['Category'] == 'Property, Plant, & Equipment'].to_dict('records')[0]
    #
    # # Process list
    # fcf = list()
    #
    # # Calculations
    # for year in year_list[1:]:
    #     fcf.append(ocf[year] - abs(ppe[year]))
    #
    # # Calculate the Free Cash Flow growth numbers
    # rule1_dict['FCF Growth Rate'] = {}
    # rule1_dict['FCF Growth Rate']['10-year'] = (fcf[-1] / fcf[-11]) ** (1 / 10) - 1
    # rule1_dict['FCF Growth Rate']['5-year'] = (fcf[-1] / fcf[-6]) ** (1 / 5) - 1
    # rule1_dict['FCF Growth Rate']['3-year'] = (fcf[-1] / fcf[-4]) ** (1 / 3) - 1
    # rule1_dict['FCF Growth Rate']['1-year'] = (fcf[-1] / fcf[-2]) ** (1 / 1) - 1
    #
    # # Calculate Operating Cash Flow Growth Rate
    # # OCF: Operating Cash Flow
    #
    # # Process list
    # ocf_list = df_cf.loc[df_cf['Category'] == 'Cash From Operations'].values.flatten().tolist()[1:]
    #
    # # Calculate the Operating Cash Flow growth numbers
    # rule1_dict['OCF Growth Rate'] = {}
    # rule1_dict['OCF Growth Rate']['10-year'] = (ocf_list[-1] / ocf_list[-11]) ** (1 / 10) - 1
    # rule1_dict['OCF Growth Rate']['5-year'] = (ocf_list[-1] / ocf_list[-6]) ** (1 / 5) - 1
    # rule1_dict['OCF Growth Rate']['3-year'] = (ocf_list[-1] / ocf_list[-4]) ** (1 / 3) - 1
    # rule1_dict['OCF Growth Rate']['1-year'] = (ocf_list[-1] / ocf_list[-2]) ** (1 / 1) - 1
    #
    # # Obtain the latest long-term debt and see if it can pay it back in at least 3 years with Free Cash Flow
    # # current_debt = long_term_debt['TTM']
    # current_debt = long_term_debt[list(long_term_debt)[-1]]
    # current_fcf = fcf[-1]
    # debt_fcf_ratio = abs(current_debt / current_fcf)
    #
    # if debt_fcf_ratio <= 3:
    #     debt_payoff_possible = True
    # else:
    #     debt_payoff_possible = False
    #
    # rule1_dict['Debt'] = {}
    # rule1_dict['Debt']['Current Long-Term Debt'] = current_debt
    # rule1_dict['Debt']['Debt Payoff Possible'] = debt_payoff_possible
    #
    # # Print all MOAT numbers
    # print('ROIC 10-year average: ' + str('{percent:.2%}'.format(percent=rule1_dict['ROIC']['10-year'])))
    # print('ROIC 5-year average:  ' + str('{percent:.2%}'.format(percent=rule1_dict['ROIC']['5-year'])))
    # print('ROIC 3-year average:  ' + str('{percent:.2%}'.format(percent=rule1_dict['ROIC']['3-year'])))
    # print('ROIC 1-year average:  ' + str('{percent:.2%}'.format(percent=rule1_dict['ROIC']['1-year'])))
    # print('-'*100)
    # print('Equity Growth Rate 10-year: ' + str('{percent:.2%}'.format(percent=rule1_dict['Equity Growth Rate'][f'{max_year}-year'])))
    # print('Equity Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Equity Growth Rate']['5-year'])))
    # print('Equity Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Equity Growth Rate']['3-year'])))
    # print('Equity Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Equity Growth Rate']['1-year'])))
    # print('-' * 100)
    # print('Sales Growth Rate 10-year: ' + str('{percent:.2%}'.format(percent=rule1_dict['Sales Growth Rate']['10-year'])))
    # print('Sales Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Sales Growth Rate']['5-year'])))
    # print('Sales Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Sales Growth Rate']['3-year'])))
    # print('Sales Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['Sales Growth Rate']['1-year'])))
    # print('-' * 100)
    # print('FCF Growth Rate 10-year: ' + str('{percent:.2%}'.format(percent=rule1_dict['FCF Growth Rate']['10-year'])))
    # print('FCF Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['FCF Growth Rate']['5-year'])))
    # print('FCF Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['FCF Growth Rate']['3-year'])))
    # print('FCF Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['FCF Growth Rate']['1-year'])))
    # print('-' * 100)
    # print('OCF Growth Rate 10-year: ' + str('{percent:.2%}'.format(percent=rule1_dict['OCF Growth Rate']['10-year'])))
    # print('OCF Growth Rate 5-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['OCF Growth Rate']['5-year'])))
    # print('OCF Growth Rate 3-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['OCF Growth Rate']['3-year'])))
    # print('OCF Growth Rate 1-year:  ' + str('{percent:.2%}'.format(percent=rule1_dict['OCF Growth Rate']['1-year'])))
    # print('-' * 100)
    # # print('Current Long-Term Debt: ' + str(rule1_dict['Debt']['Current Long-Term Debt']))
    # print('Debt Payoff Possible: ' + str(rule1_dict['Debt']['Debt Payoff Possible']))
    #
    # # TODO: Discover how to correct TTM values from dataframes
    #
    # # Calculate the Margin of Safety Number
    # # MOS: Margin of Safety = 0.5 * Sticker Price
    # # Sticker Price: The "intrinsic value" of the company
    # # Sticker Price = Future Market Price / (1 + MARR) ^ Time(years)
    # # Future Market Price = Future PE * Future EPS
    # # MARR: Minimum Acceptable Rate of Return - For Rule Number #1 it's always 15%
    # # Future PE: Future Price to Earnings Ratio = Min(Default PE, Average Historical PE)
    # # Default PE: 2 * EPS Growth Rate * 100 (To remove percentage)
    # # Average Historical PE: 10-year average of the last Price to Earnings Ratio
    # # Future EPS = Current EPS * (1 + EPS Growth Rate) ^ Time(years)
    # # EPS Growth Rate = Min(Equity Growth Rate, Analysts Estimated Growth Rate)
    # # Equity Growth Rate = Average(10-year, 5-year, 3-year, and 1-year Equity Growth Rate)
    # # Analyst Growth Rate: Data scraped from the internet
    # # Current EPS: The TTM Earning Per Share
    # # Time (year): For long term investing, it's always 10 years
    #
    # # Input:
    # time = 10
    # marr = 0.15
    #
    # # Calculations
    # # current_eps = df.loc[df['Category'] == 'EPS (Diluted)']['TTM'].values[0]
    # current_eps = df.loc[df['Category'] == 'EPS (Diluted)'][df.columns.values.tolist()[-1]].values[0]
    # # print(df.loc[df['Category'] == 'EPS (Diluted)'].values)
    # # print(current_eps)
    #
    # # TODO: get analyst growth rate from yahoo finance or other API
    # analyst_growth_rate = 0.123
    #
    # # print(list(rule1_dict['Equity Growth Rate'].values()))
    #
    # equity_growth_rate = np.mean(list(rule1_dict['Equity Growth Rate'].values()))
    #
    # eps_growth_rate = min([analyst_growth_rate, equity_growth_rate])
    # future_eps = current_eps * (1 + eps_growth_rate) ** time
    #
    # average_historical_pe = df.loc[df['Category'] == "Price-to-Earnings"].values.flatten().tolist()[-time:]
    # average_historical_pe = np.mean(average_historical_pe)
    #
    # default_pe = 2 * eps_growth_rate * 100
    #
    # future_pe = min(default_pe, average_historical_pe)
    #
    # future_market_price = future_pe * future_eps
    #
    # sticker_price = future_market_price / ((1 + marr) ** time)
    #
    # margin_of_safety = 0.5 * sticker_price
    #
    # # Print all MOS calculations
    # # print('Current EPS: ' + str(current_eps))
    # # print('Future EPS: ' + str(future_eps))
    # # print('Analyst Growth Rate: ' + str(analyst_growth_rate))
    # # print('Equity Growth Rate: ' + str(equity_growth_rate))
    # # print('EPS Growth Rate: ' + str(eps_growth_rate))
    # # print('Average Historical Price to Earnings Ratio: ' + str(average_historical_pe))
    # # print('Default Price to Earnings Ratio: ' + str(default_pe))
    # # print('Future Price to Earnings Ratio: ' + str(future_pe))
    # # print('Future Market Price: ' + str(future_market_price))
    # # print('Sticker Price: ' + str(sticker_price))
    # # print('Margin of Safety: ' + str(margin_of_safety))
