# 2019 Novel Coronavirus (COVID-19) Visualization

This work is built upon on the 2019 Novel Coronavirus dataset maintained by
the Johns Hopkins University Center for Systems Science and Engineering:
https://github.com/CSSEGISandData/COVID-19 

Their Visual Dashboard ([desktop](https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) or [mobile](http://www.arcgis.com/apps/opsdashboard/index.html#/85320e2ea5424dfaaa75ae62e5c06e61)) is great, but the plots it generates are not customizable. Logarithmic scaling of y-axes is important, of course, to show exponential growth at different rates as straight lines, but in order to compare the progress of the virus in countries of very different size, I find it useful to show the numbers per million people. I guess I'm wondering if all regions are heading toward the same percentage of confirmed cases, ultimately. Finally, I find it helpful to have the x-axes marked clearly as dates, for comparison of with actions we collectively take which might affect those rates.

The charts the Financial Times is producing are great: https://www.ft.com/coronavirus-latest. They certainly do a good job of comparing trajectories between countries, and it's great how they single out one country at a time for attention. Unfortunately the tactic of time-aligning the curves according to when the number of cases crosses a fixed threshold means they can't be plotted on a common calendar with significant dates marked. 

![countries with differing approaches](/visualization/CountriesConfirmedPerDay1.png)

![mostly europe](/visualization/CountriesConfirmedPerDay2.png)

![mostly South America](/visualization/CountriesConfirmedPerDay4.png)

![mostly Africa](/visualization/CountriesConfirmedPerDay5.png)

![Canadian provinces](/visualization/ProvincesConfirmedPerDay.png)

After most countries reached their peaks it became obvious that incremental case rates were more informative than cumulative case rates.

Sources for the significant dates marked on these plots are given in [/visualization/plots.py](/visualization/plots.py). 
Something like the Oxford University "stringency index" could be an improvement: https://www.bsg.ox.ac.uk/research/research-projects/oxford-covid-19-government-response-tracker. Almost anything is likely to be better than my ad hoc choice of key dates - of course governmental directives are not necessarily indicative of the breadth and depth of public participation.
