#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo of polar coordinates of straight line
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.patches import Arc

def get_intersection(m0, c0, m1, c1=0):
    """ Get point of intersection of two lines, y = m0 x + c0 and 
        y = m1 x + c1
    """
    
    xi = (c0 - c1) / (m1 - m0)
    
    yi = m1 * xi + c1
    
    return xi, yi


def get_polar(x0, y0, x1, y1, mode='rad'):  
    
    if mode not in ('rad', 'deg'):
        raise ValueError("'mode' should be 'rad' or 'deg'")
    
    delta_x = x1 - x0
    delta_y = y1 - y0
    
    rho = np.sqrt(delta_y**2 + delta_x**2)
    theta = np.arctan2(delta_y, delta_x)
    
    if theta < 0:
        theta *= -1
        rho *= -1
        
    if mode == 'deg':
        theta *= (180/np.pi)
    
    return theta, rho


def get_theta_rho(m, c, plot=False):
    
    # origin
    xo = 0
    yo = 0
    
    m1 = -1 / m
    c1 = yo
    
    # intersection
    xi, yi = get_intersection(m, c, m1, c1)
    
    # get parametric equation parameters
    theta, rho = get_polar(xo, yo, xi, yi, 'rad')
    
    if plot:
        plot_all(m, c, m1, c1, xi, yi)
    
    return theta, rho


def plot_all(m0, c0, m1, c1, xi, yi):
    
    sns.set_style('whitegrid')
    
    plt.figure(figsize=(5,2.5))
    ax = plt.gca()
    
    plt.scatter(0,0, color='red')
    
    plt.scatter(xi, yi, color='purple')
    
    x0 = np.linspace(0, 3)
    y0 = m0*x0 + c0
    plt.plot(x0, y0, color='steelblue')
    
    x1 = np.linspace(0, xi)
    y1 = m1*x1 + c1
    
    plt.plot(x1, y1, color='red', linestyle='--')
    
    theta = np.arctan(-1/m0)
    deg = theta * 180/np.pi
    arc = Arc((0,0), width=1, height=1, angle=0, theta1=deg, theta2=0, 
              color='orange', linestyle='--')
    plt.text(0.22, -0.22, '\u03B8', color='orange', size=14)
    ax.add_patch(arc)
    
    plt.text(0.08, -0.68, '\u03C1', color='red', size=14)
    
    plt.grid(True)
    #plt.legend()
    plt.xlabel('x')
    plt.ylabel('y', rotation='horizontal')
    
    ytx = [-1, -0.5, 0, 0.5]
    plt.yticks(ytx)
    
#    border = 0.25
#    
#    plt.xlim(-1-border, 1+border)
#    plt.ylim(0-border,2+border)
    
    plt.show()
    plt.close()


if __name__ == '__main__':
    
    m0 = 0.5
    c0 = -1
    
    theta, rho = get_theta_rho(m0, c0, True)
    
    print('Line 1: theta: {:.3f}, rho: {:.3f}'.format(theta, rho))
    
    m1 = -1/np.tan(theta)
    c1 = rho/np.sin(theta)
    
    print('This gives: m={}, c={}'.format(m1,c1))
    
    
    
