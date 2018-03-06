import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import row
from bokeh.models.widgets import Dropdown
from bokeh.models import ColumnDataSource, CustomJS
import bokeh
import numpy as np

bokeh.settings.BOKEH_LOG_LEVEL = 'trace'

def fitData(x, y):
    fit = np.polyfit(x,y,1, cov=True)
    mat = fit[1]
    r2 = (mat[1][0]*mat[0][1])/(mat[0][0]*mat[1][1])
    return (fit[0][0], fit[0][1], r2)


# =========== End function definitions ===========

yearData = pd.read_csv("db2009.csv", header=0)

f = {'rush att': ['sum'], 'pass att': ['sum'], 'ptdiff': ['mean'], 'team': ['first']}

print yearData.index.size

drives = yearData.groupby('drive').agg(f)
drives.columns = ["_".join(x) for x in drives.columns.ravel() if x != "first"]  # Removes multi-index

downs = yearData.groupby(('team', 'down')).agg(f)
downs.columns = ["_".join(x) for x in downs.columns.ravel() if x != "first"]  # Removes multi-index

quarters = yearData.groupby('quarter').agg(f)
quarters.columns = ["_".join(x) for x in quarters.columns.ravel() if x != "first"]  # Removes multi-index

pointDiffs = yearData.groupby(('team', 'ptdiff')).agg(f)
pointDiffs.columns = ["_".join(x) for x in pointDiffs.columns.ravel() if x != "first"]  # Removes multi-index

#

drives = drives[(drives['pass att_sum'] + drives['rush att_sum']) > 2]
drives['fracPass'] = 100 * drives['pass att_sum'] / (drives['pass att_sum'] + drives['rush att_sum'])


# PLOTTING STUFF PLOTTING STUFF
# output to static HTML file
output_file("lines.html", title="line plot example")

# create a new plot with a title and axis labels
p = figure(title="simple line example", x_axis_label='Point Differential at Drive Start',
           y_axis_label='% Passes in Drive')


# THE DATA
original_source = ColumnDataSource(data=dict(x=drives['ptdiff_mean'],
                                             y=drives['fracPass'],
                                             label=drives['team_first']))

plotData = drives[drives['team_first'] == 'CLE']
# Set up the function that changes the team
source = ColumnDataSource(data=dict(x=plotData['ptdiff_mean'],
                                    y=plotData['fracPass'],
                                    label=plotData['team_first']))



# add a line renderer with legend and line thickness
p.circle(x='x', y='y', source=source, size=5, color="blue")

# fit the data
# (m, b, r2) = fitData(plotData['ptdiff_mean'], plotData['fracPass'])
# yfit = [b + m * min(plotData['ptdiff_mean']), b + m * max(plotData['ptdiff_mean'])]
# xfit = [min(plotData['ptdiff_mean']), max(plotData['ptdiff_mean'])]
# p.line(xfit, yfit, legend="%2.2f"%m + "*x+" + "%2.2f"%b)

# callback = CustomJS(args=dict(source=source, original_source=original_source),
#                     code="""
#     var data = source.data;
#     var f = cb_obj.value
#     console.log(f)
#     for (var key in original_source.data) {
#         data[key] = []
#         for (var i=0; i < original_source.data['team_first'].length; ++i) {
#             if (original_source.data['team_first'][i] === f){
#                 data[key].push(original_source.data[key][i]);
#             }
#         }
#     }
#     source.change.emit();
# """)
def callback(source = source, original_source = original_source, window = None):
    data = source.data
    original_data = original_source.data
    f = cb_obj.value
    x, y = data['x'], data['y']

    for i in range(len(original_data)):
        if(original_data['label'][i] == 'PIT'):
            x[i] = 1#original_data['x'][i]
            y[i] = 1#original_data['y'][i]
        else:
            x[i], y[i] = 0,0
    window.alert("ahem")
    source.trigger('change', data, data)

menu = [("Cleveland","CLE"), ("Pittsburgh","PIT")]
dropdown = Dropdown(label="BLAH", button_type="warning", menu=menu)
dropdown.js_on_change('value', CustomJS.from_py_func(callback))

# show the results
show(row(p,dropdown))

print "meh"