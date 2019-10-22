#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot accumulator with either Matplotlib or plotly
"""

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm, colors, colorbar
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import seaborn as sns

import plotly.plotly as py
import plotly
import plotly.graph_objs as go

import os.path
import sys

u_pi = '\u03C0'
u_rho = '\u03C1'
u_theta = '\u03B8'

    
def ply(x, y, acc, fname_base='acc'):
    
    X, Y = np.meshgrid(x, y)
    
    data = [go.Surface(x=X, y=Y, z=acc, reversescale=True, colorscale='Blues',
                       showscale=False)]
    
    yticks = np.linspace(min(y), max(y), num=7)
    
    layout = go.Layout(
#        title='Hough Transform',
        scene=dict(
            xaxis=dict(
                title = u_rho
                ),
            yaxis=dict(
                title=u_theta,
                tickvals=yticks,
#                ticktext=list('{:.2f}'.format(n) for n in yticks),
                ticktext = ['0', u_pi+'/6', u_pi+'/3', u_pi+'/2',
                            '2'+u_pi+'/3', '5'+u_pi+'/6', u_pi]
                ),
            zaxis=dict(
                title='accumulator',
                ),
            camera=dict(
                center=dict(x=0, y=0, z=-0.25),
                eye=dict(x=1.25, y=1.25, z=0.5)
                ),
            ),
    )
    fig = go.Figure(data=data, layout=layout)
#    py.sign_in('keziah', 'LpFUWs0bg7RQCBvmdJvR')
#    py.image.save_as(fig, filename='db_scc.png')
    py.iplot(fig, filename='{}.html'.format(fname_base))
#    plotly.offline.plot(fig,
#        filename='{}.html'.format(fname_base),
#        image='png', image_width=1000, image_height=800)
    #py.plot(fig, filename='Hough Transform.html')



def mpl(x, y, acc, projection='3D', fname_base='acc'):
    
#    sns.set_style('whitegrid')
    
    fig = plt.figure(1)
    
    cmap = cm.Blues_r
    
    # do colormap stuff so because z values are in range (0,8), not (0,1) and if
    # all this isn't set, the colorbar will be in range (0,1), even though the
    # surface plot itself will be fine
#    norm = colors.Normalize(vmin=0, vmax=np.ceil(np.max(acc)))
    norm = colors.LogNorm(vmax=np.ceil(np.max(acc)))
    smap = cm.ScalarMappable(norm=norm, cmap=cmap)
    smap.set_array(acc)
    
    if projection == '2D':
        
        plt.imshow(acc, cmap=cmap, aspect=10)
        ax = plt.gca()
#        ax.grid()
        
#        r_max = 1500# acc.shape[1]//2
        x_max = 3600
#        
        xtx = np.linspace(0, x_max, 7)
        xtxlab = ['{:.0f}'.format(x-x_max/2) for x in xtx]
        ax.set_xticks(xtx)
        ax.set_xticklabels(xtxlab)
        
        ytx = np.linspace(0, acc.shape[0], num=7)
        ytxlab = ['0', u_pi+'/6', u_pi+'/3', u_pi+'/2', '2'+u_pi+'/3', 
                '5'+u_pi+'/6', u_pi]
#        
#        ylab = list('{:.2f}'.format(n) for n in np.linspace(min(y), max(y), 7))
#        ax.set_yticks(np.linspace(0, len(y), 7))
        ax.set_yticks(ytx)
        ax.set_yticklabels(ytxlab)
        
        ax.set_xlim(right=acc.shape[1])
        
        ylab_rot = 'horizontal'

    elif projection == '3D':
        
        ax = fig.gca(projection='3d')
    
        # make x and y values
        X, Y = np.meshgrid(x, y)
        
        # plot the surface
        ax.plot_surface(X, Y, acc, cmap=cmap)
        
        ax.view_init(elev=30, azim=45)
        
        ax.set_zlabel('accumulator')
        
        ylab_rot = None
        
    ax.set_xlabel(u_rho)
    ax.set_ylabel(u_theta, rotation=ylab_rot)
    
    # add a color bar which maps values to colors from the ScalarMappable object
    # created above
    fig.colorbar(smap, shrink=0.5, aspect=5)

#    plt.show()
    plt.savefig('../before_acc_2D.pdf', format='pdf')
    plt.close()



if __name__ == '__main__':
    
    fname = 'acc.csv'
    mode = 'ply'
    
#    fname = sys.argv[1]
#    mode = sys.argv[2]
#    
    _, name = os.path.split(fname)
    fname_base, _ = os.path.splitext(name)
    
    acc = np.loadtxt(fname, delimiter=',')
    
    r_max = acc.shape[1]#//2
    
#    acc = acc[:, :r_max]
    
    a0 = 0 #5*np.pi/6
    a1 = np.pi/2
    step = np.pi/180
#    y = np.arange(a0, a1+step, np.pi/180)
    y = np.arange(a0, a1, np.pi/180)
    x = np.arange(-r_max, 0, 1)
#    x = np.arange(r_max)
    
    print(acc.shape, len(x), len(y))

    if mode == 'mpl':
        mpl(x, y, acc, projection='3D', fname_base=None)
        
    elif mode == 'ply':
        ply(x, y, acc, fname_base)


###################
#### PYQTGRAPH ####
###################
    
#from pyqtgraph.Qt import QtCore, QtGui
##import pyqtgraph as pg
#import pyqtgraph.opengl as gl

#### Create a GL View widget to display data
#app = QtGui.QApplication([])
#w = gl.GLViewWidget()
#w.show()
#w.setWindowTitle('Hough Transform')
#w.setCameraPosition(distance=1000)
#
##z = pg.gaussianFilter(np.random.normal(size=(50,50)), (1,1))
#p1 = gl.GLSurfacePlotItem(z=acc, shader='shaded', color=(1, 1, 1, 1))
##p1.scale(16./49., 16./49., 1.0)
#p1.translate(-600, 0, 0)
#w.addItem(p1)
#
#
#if __name__ == '__main__':
#    import sys
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QtGui.QApplication.instance().exec_()
