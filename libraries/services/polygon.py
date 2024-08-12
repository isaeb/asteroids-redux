"""
Module providing polygon functions
"""

import math


def polarToCartesian(angle, radius):
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)
    
def cartesianToPolar(x, y):
    a = math.atan2(y, x)
    r = math.sqrt(x ** 2 + y ** 2)
    return (a, r)

def polygonCentroid(vertices, polar=False):
    n = len(vertices)
    A = 0.0
    Cx = 0.0
    Cy = 0.0

    for i in range(n):
        if polar:
            x_i, y_i = polarToCartesian(vertices[i][0], vertices[i][1])
            x_next, y_next = polarToCartesian(vertices[(i + 1) % n][0], vertices[(i + 1) % n][1])
        else:
            x_i, y_i = vertices[i]
            x_next, y_next = vertices[(i + 1) % n]
        
        # Calculate the signed area A
        A += x_i * y_next - x_next * y_i
        
        # Calculate the centroid coordinates
        Cx += (x_i + x_next) * (x_i * y_next - x_next * y_i)
        Cy += (y_i + y_next) * (x_i * y_next - x_next * y_i)
    
    A *= 0.5  # Calculate the signed area A
    Cx /= (6 * A)  # Calculate Cx
    Cy /= (6 * A)  # Calculate Cy
    
    return (Cx, Cy)

def projectPolygon(axis, polygon):
    min_proj = float('inf')
    max_proj = float('-inf')
    for vertex in polygon:
        projection = vertex[0] * axis[0] + vertex[1] * axis[1]
        if projection < min_proj:
            min_proj = projection
        if projection > max_proj:
            max_proj = projection
    return min_proj, max_proj

def colliding(polygon1, polygon2):
    # Get all the axes to test
    axes = []
    for i in range(len(polygon1)):
        edge = (polygon1[i][0] - polygon1[i-1][0], polygon1[i][1] - polygon1[i-1][1])
        axes.append((-edge[1], edge[0]))
    for i in range(len(polygon2)):
        edge = (polygon2[i][0] - polygon2[i-1][0], polygon2[i][1] - polygon2[i-1][1])
        axes.append((-edge[1], edge[0]))

    # Test all axes
    for axis in axes:
        min1, max1 = projectPolygon(axis, polygon1)
        min2, max2 = projectPolygon(axis, polygon2)
        if max1 < min2 or max2 < min1:
            return False
    return True
