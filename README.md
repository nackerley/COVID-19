# 2019 Novel Coronavirus (COVID-19) Visualization

This work is built upon on the 2019 Novel Coronavirus dataset maintained by
the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE):
https://github.com/CSSEGISandData/COVID-19 

Their Visual Dashboard ([desktop](https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) or [mobile](http://www.arcgis.com/apps/opsdashboard/index.html#/85320e2ea5424dfaaa75ae62e5c06e61)) is great, but the plots it generates are not customizable. Logarithmic scaling of y-axes is important, of course, to show exponential growth at different rates as straight lines, but in order to compare the progress of the virus in countries of very different size, I find it useful to show the numbers per million people. Finally, I find it helpful to have the x-axes marked clearly as dates, for comparison of with actions we collectively take which might affect those rates. 

![countries with differing approaches](/visualization/CountriesConfirmed1.png)

![mostly european countries](/visualization/CountriesConfirmed2.png)

![provinces](/visualization/ProvincesConfirmed.png)

Sources for the significant dates marked on these plots are given in [/visualization/plots.py](plots.py). 
Errors in the choice of these dates are all mine.
