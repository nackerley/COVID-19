#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 20:46:20 2020

@author: nick
"""
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from difflib import get_close_matches

# %% constants
DATA_PATH = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
             'master/csse_covid_19_data/csse_covid_19_time_series')
CONFIRMED_CSV = 'time_series_covid19_confirmed_global.csv'
DEATHS_CSV = 'time_series_covid19_deaths_global.csv'
RECOVERED_CSV = 'time_series_covid19_recovered_global.csv'
POP_CSV = (
    'https://raw.githubusercontent.com/datasets/population/master/data/'
    'population.csv')
PROV_POP_CSV = (
    'https://www12.statcan.gc.ca/census-recensement/2016/'
    'dp-pd/hlt-fst/pd-pl/Tables/File.cfm?'
    'T=101&SR=1&RPP=25&PR=0&CMA=0&CSD=0&S=50&O=A&Lang=Eng&OFT=CSV')

RENAME_COUNTRIES = {'US': 'United States',
                    'Taiwan*': 'Taiwan',
                    'Korea, South': 'South Korea'}
COUNTRIES = [
    'Canada', 'United States', 'China', 'Iran', 'Italy', 'South Korea',
    'Taiwan', 'Singapore']
NON_STATES = ['Recovered']
LOCKDOWN_DATES = {
    'China': datetime.date(2020, 1, 23),
    'Italy': datetime.date(2020, 3, 7),
    'Taiwan': datetime.date(2020, 3, 14),
    'Singapore': datetime.date(2020, 3, 15),
    'Canada': datetime.date(2020, 3, 16),
    'United States': datetime.date(2020, 3, 19),
    'South Korea': datetime.date(2020, 3, 20),
    }

SGC_CODES = {
    10: 'NL',
    11: 'PE',
    12: 'NS',
    13: 'NB',
    24: 'QC',
    35: 'ON',
    46: 'MB',
    47: 'SK',
    48: 'AB',
    59: 'BC',
    60: 'YT',
    61: 'NT',
    62: 'NU',
    }


# %% definitions
def maybe_date(item):
    try:
        return pd.to_datetime(item).date()
    except (ValueError, AttributeError):
        return item


def aggregator(item):
    if isinstance(item, datetime.date):
        return 'sum'
    elif item in ['Lat', 'Long']:
        return 'mean'
    elif item in ['Province/State']:
        return lambda x: ','.join(x)
    else:
        return 'first'


# %% COVID-19 data
confirmed_df = pd.read_csv(os.path.join(DATA_PATH, CONFIRMED_CSV))
confirmed_df.columns = [maybe_date(item) for item in confirmed_df.columns]
dates = [item for item in confirmed_df.columns
         if isinstance(item, datetime.date)]
confirmed_df['Country/Region'] = confirmed_df['Country/Region'].replace(
    RENAME_COUNTRIES)
confirmed_df['Province/State'].fillna('', inplace=True)
confirmed_df = confirmed_df[~confirmed_df['Province/State'].isin(NON_STATES)]

aggregators = {item: aggregator(item) for item in confirmed_df.columns}
countries_df = confirmed_df.groupby('Country/Region').agg(
    aggregators).drop(columns='Country/Region')
countries_df = countries_df.loc[COUNTRIES]

provinces_df = confirmed_df[confirmed_df['Country/Region'] == 'Canada'].copy()
provinces_df.drop(columns=['Country/Region', 'Lat', 'Long'], inplace=True)
provinces_df.set_index('Province/State', inplace=True)
provinces_df.sort_values(dates[-1], inplace=True, ascending=False)

# %% auxiliary data
pop_df = pd.read_csv(POP_CSV)
pop_df['Value'] = pop_df['Value'].astype(int)
pop_df.sort_values('Year', inplace=True)
pop_df.drop_duplicates('Country Code', keep='last', inplace=True)
pop_df['Country Name'] = pop_df['Country Name'].replace(
    {'Korea, Rep.': 'South Korea',
     'Iran, Islamic Rep.': 'Iran'})
pop_df.set_index('Country Name', inplace=True)
pop_df.at['Taiwan', 'Value'] = 23.78e6
pop_df.at['Taiwan', 'Country Code'] = 'TW'

prov_pop_df = pd.read_csv(PROV_POP_CSV, skipfooter=12,
                          index_col='Geographic name')

# %% plot country data
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.axvline(LOCKDOWN_DATES['China'], ls='--', color='k', label='lockdown')
for country in COUNTRIES:
    milion_people = pop_df.at[country, 'Value']/1e6
    code = pop_df.at[country, 'Country Code']
    label = '%s: pop. %.0fM' % (code, milion_people)
    line = ax.semilogy(dates, countries_df.loc[country, dates]/milion_people,
                       label=label)[0]

    try:
        ax.axvline(LOCKDOWN_DATES[country], ls='--', color=line.get_color())
    except KeyError:
        pass

    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.set_ylabel('Confirmed cases per million people')

confirmed_png = 'CountriesConfirmed%s.png' % str(datetime.datetime.now().date())
fig.savefig(confirmed_png, dpi=96, bbox_inches='tight')

# %% plot country data
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.axvline(LOCKDOWN_DATES['Canada'], ls='--', color='k', label='lockdown')
for province in provinces_df.iloc[:8].index:
    milion_people = prov_pop_df.at[province, 'Population, 2016']/1e6
    code = SGC_CODES[prov_pop_df.at[province, 'Geographic code']]
    current = provinces_df.loc[province, dates[-1]]
    label = '%s: %d cases, %.1fM people' % (code, current, milion_people)
    ax.semilogy(dates, provinces_df.loc[province, dates]/milion_people,
                label=label)
    locator = AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.set_ylabel('Confirmed cases per million people')
    ax.set_xlim(((pd.to_datetime(LOCKDOWN_DATES['Canada']) -
                  pd.to_timedelta(30, unit='day')).date(), ax.get_xlim()[1]))

confirmed_png = 'ProvincesConfirmed%s.png' % str(datetime.datetime.now().date())
fig.savefig(confirmed_png, dpi=96, bbox_inches='tight')
