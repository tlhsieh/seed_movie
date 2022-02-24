import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.io import output_notebook, show
output_notebook()

import warnings
warnings.filterwarnings("ignore", message="ColumnDataSource's columns must be of the same length")

def movie(da, y=None, x=None, xarray=False, sizefac=1, fontsize=12, vmin=None, vmax=None):
    """Generates inline animation within Jupyter Notebook
    
    Args:
        da (np.array or xr.DataArray): A 3d array (e.g. t, y, x), where t is the axis being scanned through
        y, x (1d array): y and x axes, not required if da is an xr.DataArray
        xarray (bool): Specifies whether da is an xr.DataArray
        sizefac (float): Factor to scale the size of output image
    
    """
    
    # retrieve axes from xr.DataArray
    if xarray:
        d = da.values
        y = da[da.dims[1]].values
        x = da[da.dims[2]].values
    else:
        d = da
        
    if vmin == None:
        vmin = np.min(d)
    if vmax == None:
        vmax = np.max(d)

    # collect data to feed to JS
    data = {'i': [d[0]], 'x': x, 'y': y}
    for i in range(len(d)):
        data[str(i)] = [d[i]]

    source = ColumnDataSource(data=data)
    source_ori = ColumnDataSource(data=data)
    
    color_mapper = LinearColorMapper(palette='Viridis256', low=vmin, high=vmax)
    
    plot = figure(x_range=(np.min(x), np.max(x)), y_range=(np.min(y), np.max(y)), plot_width=int(len(x)*sizefac), plot_height=int(len(y)*sizefac*0.8))
    plot.image(image='i', x='x', y='y', dw=np.max(x)-np.min(x), dh=np.max(y)-np.min(y), source=source, color_mapper=color_mapper)
    plot.add_layout(ColorBar(color_mapper=color_mapper, location=(0,0)), 'right')
    
    # change font size
    fontsize_string = str(fontsize)+'pt'
    plot.xaxis.major_label_text_font_size = fontsize_string
    plot.xaxis.axis_label_text_font_size = fontsize_string
    plot.yaxis.major_label_text_font_size = fontsize_string
    plot.yaxis.axis_label_text_font_size = fontsize_string

    # set axis label
    if xarray:
        plot.xaxis.axis_label = da.dims[2]
        plot.yaxis.axis_label = da.dims[1]
        
    slider = Slider(start=0, end=len(d)-1, value=0, step=1, title='index')

    codes = """
        var idx = slider.value;
        var data = source.data;
        var data_ori = source_ori.data;

        data['x'] = []
        data['y'] = []
        data['i'] = []

        data['x'] = data_ori['x'].slice();
        data['y'] = data_ori['y'].slice();
        data['i'] = data_ori[String(idx)].slice();

        source.change.emit();
    """
    update_plot = CustomJS(args=dict(source=source, source_ori=source_ori, slider=slider), code=codes)
    slider.js_on_change('value', update_plot)

    show(column(slider, plot))