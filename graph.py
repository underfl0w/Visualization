import os
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
init_notebook_mode()

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

clear = lambda: os.system('reset')

terror = pd.read_csv('/home/jurjen/PycharmProjects/graphing/globalterrorismdb_0718dist.csv', encoding='ISO-8859-1',
                          usecols=['eventid', 'iyear', 'imonth', 'iday', 'country_txt', 'targtype1_txt', 'region_txt', 'weapsubtype1_txt', 'nkill', 'nwound', 'provstate', 'longitude','latitude','attacktype1_txt', 'gname' ])

terror = terror.rename(columns={
                                'attacktype1_txt':'aanvaltype','eventid':'id', 'iyear':'year',
                                'imonth':'month', 'iday':'day', 'country_txt':'land', 'region_txt':'regio',
                                'targtype1_txt':'doel', 'weapsubtype1_txt':'weapon', 'nkill':'doden',
                                'nwound':'gewonden', 'gname':'organisatie'})

terror['doden'] = terror['doden'].fillna(0).astype(int)
terror['gewonden'] = terror['gewonden'].fillna(0).astype(int)
terror['regio'] = terror['regio'].fillna('non').astype(str)



terror_EU = terror.loc[:][(terror.regio == 'Western Europe') | (terror.regio == 'Eastern Europe')]# & (terror.land != 'Russia')]
terror_EU['day'][terror_EU.day == 0] = 1
terror_EU['month'][terror_EU.month == 0] = 1
terror_EU['datum'] = pd.to_datetime(terror_EU[['day', 'month', 'year']])
terror_EU = terror_EU[['id', 'datum', 'year','regio', 'latitude', 'longitude', 'doel', 'weapon', 'gewonden', 'doden', 'organisatie']]
terror_EU = terror_EU.sort_values(['doden', 'gewonden'], ascending = False)
terror_EU = terror_EU.drop_duplicates(['datum', 'latitude', 'longitude', 'doden'])

terror_NL = terror.loc[:][(terror.land == 'Netherlands')]
terror_NL['day'][terror_NL.day == 0] = 1
terror_NL['month'][terror_NL.month == 0] = 1
terror_NL['datum'] = pd.to_datetime(terror_NL[['day', 'month', 'year']])
terror_NL = terror_NL[['id', 'datum', 'year','regio', 'latitude', 'longitude', 'doel', 'weapon', 'gewonden', 'doden']]
terror_NL = terror_NL.sort_values(['doden', 'gewonden'], ascending = False)
terror_NL = terror_NL.drop_duplicates(['datum', 'latitude', 'longitude', 'doden'])


terror_EU['text']= terror_EU['datum'].dt.strftime('%B %-d, %Y') + '<b>' +\
terror_EU['doden'].astype(str) + ' Doden, ' +\
terror_EU['gewonden'].astype(str) + ' Gewonden'


terror_NL['text']= terror_NL['datum'].dt.strftime('%B %-d, %Y') + '<b>' +\
terror_NL['doden'].astype(str) + ' Doden, ' +\
terror_NL['gewonden'].astype(str) + ' Gewonden'

doden = dict(
           type = 'scattergeo',
           locationmode = 'ISO-3',
           lon = terror_EU[terror_EU.doden > 0]['longitude'],
           lat = terror_EU[terror_EU.doden > 0]['latitude'],
           text = terror_EU[terror_EU.doden > 0]['text'],
           mode = 'markers',
           name = 'Doden ',
           hoverinfo = 'text+name',
           marker = dict(
               size = terror_EU[terror_EU.doden > 0]['doden'] ** 0.255 * 8,
               opacity = 0.95,
               color = 'rgb(240, 140, 45)')
           )

gewonden = dict(
         type = 'scattergeo',
         locationmode = 'ISO-3',
         lon = terror_EU[terror_EU.doden == 0]['longitude'],
         lat = terror_EU[terror_EU.doden == 0]['latitude'],
         text = terror_EU[terror_EU.doden == 0]['text'],
         mode = 'markers',
         name = 'Gewonden',
         hoverinfo = 'text+name',
         marker = dict(
             size = (terror_EU[terror_EU.doden == 0]['gewonden'] + 1) ** 0.245 * 8,
             opacity = 0.85,
             color = 'rgb(20, 150, 187)')
         )

layout = dict(
         title = 'Terroristische aanvallen in de EU  (1970-2017)',
         autosize = True,
	 showlegend = True,
         legend = dict(
             x = 0.85, y = 0.4
         ),
         geo = dict(
             scope = 'europe',
             showland = True,
             landcolor = 'rgb(250, 250, 250)',
             subunitwidth = 1,
             subunitcolor = 'rgb(217, 217, 217)',
             countrywidth = 1,
             countrycolor = 'rgb(217, 217, 217)',
             showlakes = True,
             lakecolor = 'rgb(255, 255, 255)')
         )

data = [doden, gewonden]

figure = dict(data = data, layout = layout)
plot(figure, show_link=True, link_text='Export to plot.ly', validate=True, output_type='file', include_plotlyjs=True, filename='temp-plot-map.html', auto_open=True, image=None, image_filename='plot_image', image_width=1280, image_height=900)

terror_peryears = np.asarray(terror_EU.groupby('year').year.count())
clear()

terror_years = np.arange(1970, 2018)
terror_years = np.delete(terror_years, [23])

trace = [go.Bar(
         x = terror_years,
         y = terror_peryears,
         )]

layout = go.Layout(
                    title = 'Terrorist aanvallen per jaar in de EU (1970 - 2017) *No data from 1993',
                    xaxis = dict(
                        rangeslider = dict(thickness = 0.05),
                        showline = True,
                        showgrid = True
                    ),
                    yaxis = dict(
                        showline = True,
                        showgrid = True)
                    )

figure = dict(data = trace, layout = layout)
plot(figure, show_link=True, link_text='Export to plot.ly', validate=True, output_type='file', include_plotlyjs=True, filename='temp-plot.html', auto_open=True, image=None, image_filename='plot_image_chart', image_width=1280, image_height=900)

data = terror_EU.groupby("doel").id.count().sort_values(ascending=False)[:10]
data = data.reset_index()
data.columns = ["Doel", "Number of attacks"]
sns_plot = sns.barplot(data=data, x=data.columns[1], y=data.columns[0]);
plt.show()
