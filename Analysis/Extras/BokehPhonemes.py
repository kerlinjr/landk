# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 09:15:48 2016

@author: jrkerlin
Bokeh Periodic table from the website
"""

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure, show, output_file
import pandas as pd

#df = pd.DataFrame.from_csv(os.path.normpath('C:\TCDTIMIT\Tables\Custom\TablesPhoneme.csv'))
df = pd.read_excel(os.path.normpath('C:\TCDTIMIT\Tables\Custom\TablesPhoneme.xlsx'),encoding='latin-1')
cmap = range(0,len(df))
source = ColumnDataSource(
    data=dict(
        xaxis=[str(x) for x in df['AdrianXCoord']],
        yaxis=[str(y) for y in df['AdrianYCoord']],
        cmu=[str(s) for s in df['CMU Phonemes']],
        type=[str(x) for x in cmap],
        sym=df['IPA symbol'],    
        type_color = ['#%02x%02x%02x' % (x*5,255-x*5,0) for x in cmap], #Must be hexadecimal
    )
)

p = figure(title="Phoneme Table", tools="resize,hover,save")
p.plot_width = 1200
p.toolbar_location = None
p.outline_line_color = None

p.rect("xaxis", "yaxis", 0.9, 0.9, source=source,
       fill_alpha=0.6, color="type_color")
      
#p.rect("xaxis", "yaxis", 0.9, 0.9, source=source,
#       fill_alpha=0.6)

text_props = {
    "source": source,
    "angle": 0,
    "color": "black",
    "text_align": "left",
    "text_baseline": "middle"
}

p.text(x="xaxis", y="yaxis", text="sym",
       text_font_style="bold", text_font_size="15pt", **text_props)


p.grid.grid_line_color = None

p.select_one(HoverTool).tooltips = [
    ("cmu", "@cmu"),

]

output_file("phoneme.html", title="phoneme example")

show(p)