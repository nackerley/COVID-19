#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 20:46:20 2020

@author: nick
"""
import os
from math import log
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import (
    MonthLocator, ConciseDateFormatter, date2num, num2date)
from io import StringIO
from difflib import get_close_matches

import pandas as pd

# %% constants
DATA_PATH = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
             'master/csse_covid_19_data/csse_covid_19_time_series')
CASES_CSV = 'time_series_covid19_confirmed_global.csv'
DEATHS_CSV = 'time_series_covid19_deaths_global.csv'
RECOVERED_CSV = 'time_series_covid19_recovered_global.csv'
POP_CSV = (
    'https://raw.githubusercontent.com/datasets/population/master/data/'
    'population.csv')
PROV_POP_CSV = (
    'https://www12.statcan.gc.ca/census-recensement/2016/'
    'dp-pd/hlt-fst/pd-pl/Tables/File.cfm?'
    'T=101&SR=1&RPP=25&PR=0&CMA=0&CSD=0&S=50&O=A&Lang=Eng&OFT=CSV')

PLOT_COUNTRIES = [
    ['China', 'South Korea', 'Italy', 'Iran', 'United States', 'Canada',
     'Taiwan', 'Singapore'],
    ['China', 'Italy', 'Spain', 'France', 'United Kingdom', 'Sweden', 'Canada',
     'Russia'],
    ['China', 'South Korea', 'Italy', 'Spain', 'United States', 'Canada',
     'Russia', 'Brazil'],
     ]

RENAME = {
    'US': 'United States',
    'Taiwan*': 'Taiwan',
    'Korea, South': 'South Korea'}
NON_STATES = ['Recovered']

EVENT_DF = pd.read_fwf(StringIO('''\
         country                         event        date arrow                                                                         source
           China                Wuhan lockdown  2020-01-23    up   https://en.wikipedia.org/wiki/2019-20_coronavirus_pandemic_in_mainland_China
     South Korea                super-spreader  2020-02-18    up          https://www.csis.org/analysis/timeline-south-koreas-response-covid-19
           Italy                super-spreader  2020-02-19    up               https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Italy
     South Korea            drive-thru testing  2020-02-23    up          https://www.csis.org/analysis/timeline-south-koreas-response-covid-19
     South Korea             social-distancing  2020-02-29    up          https://www.csis.org/analysis/timeline-south-koreas-response-covid-19
           Italy             Lombardy lockdown  2020-03-08  down               https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Italy
          Taiwan            no-travel advisory  2020-03-15    up              https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Taiwan
          France                      lockdown  2020-03-16    up              https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_France
         Germany    non-essential shops closed  2020-03-16  down             https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Germany
          Canada         ON state of emergency  2020-03-17  down             https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Ontario
         Ontario            state of emergency  2020-03-17  down             https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Ontario
British Columbia            state of emergency  2020-03-18  down    https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_British_Columbia
   United States               NY stay-at-home  2020-03-20    up            https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_New_York
          Russia               Moscow lockdown  2020-03-20  down              https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Russia
       Singapore    extended social distancing  2020-03-20  down           https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Singapore
          Quebec  non-essential business close  2020-03-23  down              https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Quebec
  United Kingdom                      lockdown  2020-03-24  down  https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_the_United_Kingdom
         Alberta  non-essential business close  2020-03-28  down             https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Alberta
'''))  # noqa
EVENT_DF['date'] = pd.to_datetime(EVENT_DF.date).dt.date

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
DPI = 96


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


def add_rates(ax, dates, rates=(0.1, 0.4), linestyles=('--', '-.', ':'),
              **kwargs):
    xlim = date2num([dates[0], dates[-1]])
    ylim = ax.get_ylim()
    for rate, linestyle in zip(rates, linestyles):
        label = '%.0f%%/day' % (100*rate)
        x = xlim[1] - log(ylim[1]/ylim[0], 1 + rate)
        y = ylim[1]/(1 + rate)**(xlim[1] - xlim[0])
        if x < xlim[0]:
            x = xlim[0]
        else:
            y = ylim[0]
        ax.semilogy(
            [item.date() for item in num2date([x, xlim[1]])], [y, ylim[1]],
            label=label, linestyle=linestyle, **kwargs)


# %% COVID-19 data
cases_df = pd.read_csv(os.path.join(DATA_PATH, CASES_CSV))
cases_df.columns = [maybe_date(item) for item in cases_df.columns]
dates = [item for item in cases_df.columns
         if isinstance(item, datetime.date)]
as_of = 'Johns Hopkins CSSE\nCOVID-19 data\nto %s' % dates[-1]
cases_df['Country/Region'] = cases_df['Country/Region'].replace(RENAME)
cases_df['Province/State'].fillna('', inplace=True)
cases_df = cases_df[~cases_df['Province/State'].isin(NON_STATES)]

aggregators = {item: aggregator(item) for item in cases_df.columns}
cases_country_df = cases_df.groupby('Country/Region').agg(
    aggregators).drop(columns='Country/Region')

cases_province_df = cases_df[cases_df['Country/Region'] == 'Canada'].copy()
cases_province_df.drop(columns=['Country/Region', 'Lat', 'Long'], inplace=True)
cases_province_df.set_index('Province/State', inplace=True)
cases_province_df.sort_values(dates[-1], inplace=True, ascending=False)

deaths_df = pd.read_csv(os.path.join(DATA_PATH, DEATHS_CSV))
deaths_df.columns = [maybe_date(item) for item in deaths_df.columns]
dates = [item for item in deaths_df.columns
         if isinstance(item, datetime.date)]
as_of = 'Johns Hopkins CSSE\nCOVID-19 data\nto %s' % dates[-1]
deaths_df['Country/Region'] = deaths_df['Country/Region'].replace(RENAME)
deaths_df['Province/State'].fillna('', inplace=True)
deaths_df = deaths_df[~deaths_df['Province/State'].isin(NON_STATES)]

aggregators = {item: aggregator(item) for item in deaths_df.columns}
deaths_country_df = deaths_df.groupby('Country/Region').agg(
    aggregators).drop(columns='Country/Region')

deaths_province_df = deaths_df[deaths_df['Country/Region'] == 'Canada'].copy()
deaths_province_df.drop(columns=['Country/Region', 'Lat', 'Long'],
                        inplace=True)
deaths_province_df.set_index('Province/State', inplace=True)
deaths_province_df.sort_values(dates[-1], inplace=True, ascending=False)


# %% auxiliary data
pop_df = pd.read_csv(POP_CSV)
pop_df['Value'] = pop_df['Value'].astype(int)
pop_df.sort_values('Year', inplace=True)
pop_df.drop_duplicates('Country Code', keep='last', inplace=True)
pop_df['Country Name'] = pop_df['Country Name'].replace(
    {'Korea, Rep.': 'South Korea',
     'Iran, Islamic Rep.': 'Iran',
     'Russian Federation': 'Russia'})
pop_df.set_index('Country Name', inplace=True)
pop_df.at['Taiwan', 'Value'] = 23.78e6
pop_df.at['Taiwan', 'Country Code'] = 'TW'

prov_pop_df = pd.read_csv(PROV_POP_CSV, skipfooter=12,
                          index_col='Geographic name')

# %% plot country data
for i, countries in enumerate(PLOT_COUNTRIES, start=1):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.annotate(as_of, (0.05, 0.95), xycoords='axes fraction', va='top')
    for country in countries:
        try:
            milion_people = pop_df.at[country, 'Value']/1e6
        except KeyError:
            print('Best matches for %s:' % country)
            print(get_close_matches(country, pop_df.index, cutoff=0.3))
            raise RuntimeError('No population data.')

        code = pop_df.at[country, 'Country Code']
        cases = cases_country_df.loc[country, dates[-1]]
        label = '%s: %dk/%dM' % (code, cases/1e3, milion_people)
        line = ax.semilogy(
            dates, cases_country_df.loc[country, dates]/milion_people,
            label=label)[0]

        for index, info in EVENT_DF[EVENT_DF.country == country].iterrows():
            if info.arrow == 'up':
                kwargs = dict(xytext=(0, 20), va='bottom')
            else:
                kwargs = dict(xytext=(0, -20), va='top')
            cases_pmp = cases_country_df.loc[country, info.date]/milion_people
            ax.annotate(
                info.event, (info.date, cases_pmp), textcoords='offset points',
                color=line.get_color(), fontsize=8, rotation=90, ha='center',
                fontweight='bold',
                arrowprops=dict(arrowstyle='-|>', color=line.get_color()),
                **kwargs)

        ax.semilogy(
            dates, deaths_country_df.loc[country, dates]/milion_people,
            color=line.get_color(), linestyle=':', alpha=0.5)[0]

    ax.semilogy(
        dates, deaths_country_df.loc[country, dates]/milion_people,
        color='black', linestyle=':', alpha=0.5, label='Deaths')[0]

    locator = MonthLocator(bymonthday=(1, 15))
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))

    add_rates(ax, dates, color='black', linewidth=1)

    ax.legend(title='Confirmed cases', loc='center left',
              bbox_to_anchor=(1, 0.5))
    ax.set_ylabel('Rate per million people')
    start_date = (pd.to_datetime(dates[0]) -
                  pd.to_timedelta(1, unit='day')).date()
    ax.set_xlim((start_date, dates[-1]))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    confirmed_png = 'CountriesConfirmed%d.png' % i
    fig.savefig(confirmed_png, dpi=DPI, bbox_inches='tight')

# %% plot country data
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.annotate(as_of, (0.05, 0.95), xycoords='axes fraction', va='top')

for province in cases_province_df.iloc[:8].index:
    milion_people = prov_pop_df.at[province, 'Population, 2016']/1e6
    code = SGC_CODES[prov_pop_df.at[province, 'Geographic code']]
    current = cases_province_df.loc[province, dates[-1]]
    label = '%s: %.1fk/%.1fM' % (code, current/1e3, milion_people)
    line = ax.semilogy(
        dates, cases_province_df.loc[province, dates]/milion_people,
        label=label)[0]

    for index, info in EVENT_DF[EVENT_DF.country == province].iterrows():
        if info.arrow == 'up':
            kwargs = dict(xytext=(0, 20), va='bottom')
        else:
            kwargs = dict(xytext=(0, -20), va='top')
        cases_pmp = cases_province_df.loc[province, info.date]/milion_people
        ax.annotate(
            info.event, (info.date, cases_pmp), textcoords='offset points',
            color=line.get_color(), fontsize=8, rotation=90, ha='center',
            arrowprops=dict(arrowstyle='-|>', color=line.get_color()),
            **kwargs)

    ax.semilogy(
        dates, deaths_province_df.loc[province, dates]/milion_people,
        color=line.get_color(), linestyle=':', alpha=0.5)[0]

ax.semilogy(
    dates, deaths_province_df.loc[province, dates]/milion_people,
    color='black', linestyle=':', alpha=0.5, label='Deaths')[0]

locator = MonthLocator(bymonthday=(1, 15))
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
start_date = (pd.to_datetime(info.date) -
              pd.to_timedelta(30, unit='day')).date()
add_rates(ax, [start_date, dates[-1]], linewidth=1, color='0.5')
ax.legend(title='Confirmed cases', loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_ylabel('Rate per million people')
ax.set_xlim((start_date, dates[-1]))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

confirmed_png = 'ProvincesConfirmed.png'
fig.savefig(confirmed_png, dpi=DPI, bbox_inches='tight')
