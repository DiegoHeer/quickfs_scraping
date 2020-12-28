import pandas as pd
import numpy as np
import openpyxl


def get_rule_number1_ratios(df_dict):
    # Initialize a dictionary to store Rule #1 ratios
    rule1_dict = dict()

    # Get the appropriate dataframes
    df_is = df_dict['income statement']
    df_bs = df_dict['balance sheet']
    df_cf = df_dict['cash flow']

    # Obtain year list that is going to be used with the calculations
    year_list = df_is.columns.values.tolist() + df_bs.columns.values.tolist() + df_cf.columns.values.tolist()
    year_list = list(set(year_list))
    year_list.remove('Category')
    year_list.sort()

    # Calculate first the MOAT numbers

    # Calculate the ROIC
    # ROIC: Return on Invested Capital = NOPAT/Invested Capital
    # NOPAT: Net Operating Profit after Tax = Operating Profit * (1 - Tax Rate)
    # Tax Rate = abs(Income Tax)/Income before tax
    # Invested Capital = Interest Bearing Debt + Shareholders' Equity
    # Interest Bearing Debt = Short-Term Debt + Long-Term Debt

    # Input dictionaries
    operating_profit = df_is.loc[df_is['Category'] == 'Operating Profit'].to_dict('records')[0]
    income_tax = df_is.loc[df_is['Category'] == 'Income Tax'].to_dict('records')[0]
    income_before_tax = df_is.loc[df_is['Category'] == 'Pre-Tax Income'].to_dict('records')[0]
    short_term_debt = df_bs.loc[df_bs['Category'] == 'Short-Term Debt'].to_dict('records')[0]
    long_term_debt = df_bs.loc[df_bs['Category'] == 'Long-Term Debt'].to_dict('records')[0]
    shareholder_equity = df_bs.loc[df_bs['Category'] == "Shareholders' Equity"].to_dict('records')[0]
    # total_assets = df_bs.loc[df_bs['Category'] == "Total Assets"].to_dict('records')[0]

    # Because the ROIC uses the income statement and balance sheet, and the income statement doesn't have a TTM column,
    # and the balance sheet doesn't have the first year, those elements will be removed from the year list
    minimal_year_list = year_list[1:]
    minimal_year_list.remove('TTM')

    # Process list
    roic = list()

    # Calculations
    for year in minimal_year_list:
        tax_rate = abs(income_tax[year]) / income_before_tax[year]
        nopat = operating_profit[year] * (1 - tax_rate)
        interest_bearing_debt = short_term_debt[year] + long_term_debt[year]
        invested_capital = interest_bearing_debt + shareholder_equity[year]
        # invested_capital = total_assets[year]

        roic.append(nopat / invested_capital)

    # Calculate the ROIC averages
    rule1_dict['ROIC'] = {}
    rule1_dict['ROIC']['10-year'] = np.mean(roic[-10:])
    rule1_dict['ROIC']['5-year'] = np.mean(roic[-5:])
    rule1_dict['ROIC']['3-year'] = np.mean(roic[-3:])
    rule1_dict['ROIC']['1-year'] = np.mean(roic[-1:])

    # Calculate the Equity Growth Rate
    # BVPS: Book Value per Share = Book Value/Shares(Diluted)
    # Book Value = Shareholders' Equity

    # Input dictionaries
    book_value = shareholder_equity
    shares_diluted = df_is.loc[df_is['Category'] == "Shares (Diluted)"].to_dict('records')[0]

    # Process list
    bvps = list()

    # Calculations
    for year in minimal_year_list:
        bvps.append(book_value[year] / shares_diluted[year])

    # Calculate the equity growth numbers
    # Growth rate formula: Growth Rate = (Future Value/Current Value)^(1/Time(years)) - 1
    # Because growth rates require two different year values to be calculated,
    # the 9-year rate will be used in place of 10-year rate
    rule1_dict['Equity Growth Rate'] = {}
    rule1_dict['Equity Growth Rate']['9-year'] = (bvps[-1] / bvps[-10]) ** (1 / 9) - 1
    rule1_dict['Equity Growth Rate']['5-year'] = (bvps[-1] / bvps[-6]) ** (1 / 5) - 1
    rule1_dict['Equity Growth Rate']['3-year'] = (bvps[-1] / bvps[-4]) ** (1 / 3) - 1
    rule1_dict['Equity Growth Rate']['1-year'] = (bvps[-1] / bvps[-2]) ** (1 / 1) - 1

    # Calculate the EPS Growth Rate

    # Input list
    diluted_eps = df_is.loc[df_is['Category'] == "EPS (Diluted)"].values.flatten().tolist()[1:]

    # Calculate the EPS growth numbers
    rule1_dict['EPS Growth Rate'] = {}
    rule1_dict['EPS Growth Rate']['10-year'] = (diluted_eps[-1] / diluted_eps[-11]) ** (1 / 10) - 1
    rule1_dict['EPS Growth Rate']['5-year'] = (diluted_eps[-1] / diluted_eps[-6]) ** (1 / 5) - 1
    rule1_dict['EPS Growth Rate']['3-year'] = (diluted_eps[-1] / diluted_eps[-4]) ** (1 / 3) - 1
    rule1_dict['EPS Growth Rate']['1-year'] = (diluted_eps[-1] / diluted_eps[-2]) ** (1 / 1) - 1

    # Calculate the Sales Growth Rate
    # Sales = Revenue

    # Input list
    sales = df_is.loc[df_is['Category'] == 'Revenue'].values.flatten().tolist()[1:]

    # Calculate the Sales growth numbers
    rule1_dict['Sales Growth Rate'] = {}
    rule1_dict['Sales Growth Rate']['10-year'] = (sales[-1] / sales[-11]) ** (1 / 10) - 1
    rule1_dict['Sales Growth Rate']['5-year'] = (sales[-1] / sales[-6]) ** (1 / 5) - 1
    rule1_dict['Sales Growth Rate']['3-year'] = (sales[-1] / sales[-4]) ** (1 / 3) - 1
    rule1_dict['Sales Growth Rate']['1-year'] = (sales[-1] / sales[-2]) ** (1 / 1) - 1

    # Calculate Free Cash Flow Growth Rate
    # Free Cash Flow: FCF = OCF - PPE
    # OCF: Operating Cash Flow
    # PPE: Property, Plant & Equipment

    # Input dictionaries
    ocf = df_cf.loc[df_cf['Category'] == 'Cash From Operations'].to_dict('records')[0]
    ppe = df_cf.loc[df_cf['Category'] == 'Property, Plant, & Equipment'].to_dict('records')[0]

    # Process list
    fcf = list()

    # Calculations
    for year in year_list[1:]:
        fcf.append(ocf[year] - abs(ppe[year]))

    # Calculate the Free Cash Flow growth numbers
    rule1_dict['Free Cash Flow'] = {}
    rule1_dict['Free Cash Flow']['10-year'] = (fcf[-1] / fcf[-11]) ** (1 / 10) - 1
    rule1_dict['Free Cash Flow']['5-year'] = (fcf[-1] / fcf[-6]) ** (1 / 5) - 1
    rule1_dict['Free Cash Flow']['3-year'] = (fcf[-1] / fcf[-4]) ** (1 / 3) - 1
    rule1_dict['Free Cash Flow']['1-year'] = (fcf[-1] / fcf[-2]) ** (1 / 1) - 1

    # Calculate Operating Cash Flow Growth Rate
    # OCF: Operating Cash Flow

    # Process list
    ocf_list = df_cf.loc[df_cf['Category'] == 'Cash From Operations'].values.flatten().tolist()[1:]

    # Calculate the Free Cash Flow growth numbers
    rule1_dict['Operating Cash Flow'] = {}
    rule1_dict['Operating Cash Flow']['10-year'] = (ocf_list[-1] / ocf_list[-11]) ** (1 / 10) - 1
    rule1_dict['Operating Cash Flow']['5-year'] = (ocf_list[-1] / ocf_list[-6]) ** (1 / 5) - 1
    rule1_dict['Operating Cash Flow']['3-year'] = (ocf_list[-1] / ocf_list[-4]) ** (1 / 3) - 1
    rule1_dict['Operating Cash Flow']['1-year'] = (ocf_list[-1] / ocf_list[-2]) ** (1 / 1) - 1

    # Obtain the latest long-term debt and see if it can pay it back in at least 3 years with Free Cash Flow
    current_debt = long_term_debt['TTM']
    current_fcf = fcf[-1]
    debt_fcf_ratio = abs(current_debt / current_fcf)

    if debt_fcf_ratio <= 3:
        debt_payoff_possible = True
    else:
        debt_payoff_possible = False

    rule1_dict['Debt'] = {}
    rule1_dict['Debt']['Current Long-Term Debt'] = current_debt
    rule1_dict['Debt']['Debt Payoff Possible'] = debt_payoff_possible

    # Calculate the Margin of Safety Number
