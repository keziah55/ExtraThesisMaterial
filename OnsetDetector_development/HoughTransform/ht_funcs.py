#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hough transform functions
"""

import numpy as np
import warnings

import matplotlib.pyplot as plt

def get_normal(m, c=0):
    """ From line of gradient `m`, return a perpendicular line which cuts the
        y-axis at `c`.
    """
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            mn = -1 / m
    except RuntimeWarning:
        mn = np.inf
    
    return mn

def get_intersection(m0, c0, m1, c1=0):
    """ Get point of intersection of two lines, y = m0 x + c0 and 
        y = m1 x + c1
    """
    
    if np.isinf(m0) or np.isinf(m1):
        pass

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
        theta += np.pi
        rho *= -1
  
    if mode == 'deg':
        theta *= (180/np.pi)
    
    return theta, rho


def theta_rho_to_m_c(theta, rho):
    """ Given theta and rho that define a straight line
        rho = x cos(theta) + y sin(theta)
        return the gradient and y-intercept of this line.
    """
    
    m = -1 / np.tan(theta)
    
    c = rho / np.sin(theta)
    
    return m, c


def m_c_to_theta_rho(m, c):
    """ Given a gradient `m` and y-intercept `c`, return the theta and rho
        values of the parametric equation of this line.
    """
    
    m_normal = get_normal(m)
    
    xi, yi = get_intersection(m, c, m_normal, 0)
    
    theta, rho = get_polar(0, 0, xi, yi)
    
    return theta, rho


def get_numerical_intersection(arrays, limit=None):
    """ Get intersection point of n arrays
        
        Analyse the spread of values at every sample and return the index
        where the spread is smallest and the spread at this point.
    
        Parameters
        ----------
        arrays : array-like
            array (or list) of arrays
        limit : float (optional)
            value with which to compare the minimum spread. If the spread 
            exceeds the limit, this function will return None, None
            
        Returns
        -------
        index where the spread of values is smallest, or None
        spread at index, or None
            
    """
    
    if type(arrays) is list:
        arrays = np.array(arrays)
        
    size = len(arrays[0])
    
    diff = np.zeros(size)
    
    for n in range(size):
        
        diff[n] = np.max(arrays[:,n]) - np.min(arrays[:,n])
        
    mn = np.min(diff)
    idx = np.where(diff==mn)[0][0]

    # if a limit had been given and the minimum spread of values exceeds
    # it, return None    
    if limit:
        if mn > limit:
            return None, None
    
    # if no limit or mn <= limit, return
    return idx, mn


def get_theta_rho(points):
    
    # angle increment
    inc = np.pi / 180
    # number of lines through original point to test
    num = int(np.pi / inc)
    
    all_rho = np.zeros((points.shape[0], num))
    all_theta = np.zeros((points.shape[0], num))
    
    for p in range(len(points)):
        
        print('{:.0f}%'.format(100*p/len(points)), end='\r')
    
        a0, b0 = points[p]
        
        # pick a point
        a1 = a0 + 1
        b1 = b0 + 0.5
        
        # distance between two points
        r = np.sqrt((a0-a1)**2 + (b0-b1)**2)
        
        # angle between this line and horizontal
        angle = np.arctan2((b1-b0), (a1-a0))
        
        if angle < 0:
            angle += 2*np.pi
    
        n = 0
        while n < num:
        
            # when n=0, new_a and new_b are a1 and b1
            new_a = a0 + r * np.cos(angle)
            new_b = b0 + r * np.sin(angle)
            
            m_line = (new_b - b0) / (new_a - a0)
            
            c0 = new_b - (m_line * new_a)
            
            m_normal = get_normal(m_line)
            
            xi, yi = get_intersection(m_line, c0, m_normal, 0)
            
            rho, theta = get_polar(0, 0, xi, yi)
            
            all_rho[p][n] = rho
            all_theta[p][n] = theta
            
            angle += inc
            n += 1
            
    return all_theta, all_rho
        



if __name__ == '__main__':

    m0 = 1.144
    c0 = -0.26
    
#    theta, rho = m_c_to_theta_rho(m0, c0)
    theta = 300 * (np.pi/180)
    rho = 30
    
    m1, c1 = theta_rho_to_m_c(theta, rho)
    
    x = np.linspace(0, 10)
    
#    y0 = m0 * x + c0
    y1 = m1 * x + c1
    
#    plt.plot(x, y0, color='green')
    plt.plot(x, y1, color='orange')
    
    plt.show()
    plt.close()
    
#    print('m0: {:.3f}, c0: {:.3f}\nm1: {:.3f}, c1: {:.3f}'
#          .format(m0, c0, m1, c1))
#    print('theta: {:.3f}, rho: {:.3f}'.format(theta, rho))


