"""Functions that perform operations on the polygon objects."""

from shapely.geometry import shape
import math
import itertools
from collections import defaultdict
from numpy import array
import tqdm


def findneighbours(polys, codeextractor):
    """Find the neighbours of each polygon in the dataset.

    :polys: fiona.collection.Collection of polygons
    :codeextractor: function applied to each element in polys. Extracts a
        unique code from that element
    :returns: defaultdict containing {code: [neighbours]}

    """
    output = defaultdict(list)

    # find all possible 2 permutations of different polygons
    for p1, p2 in tqdm.tqdm(itertools.permutations(polys, 2)):
        # are they neighbours?
        if shape(p1['geometry']).touches(shape(p2['geometry'])):
            # stick them on the defaultdict then!
            output[codeextractor(p1)].append(codeextractor(p2))

    return dict(output)


def anglebetween(p1, p2):
    """Find the angle between two points, relative to the cartesian
    coordinates, as if point 1 was pushing point 2.

    Args:
        p1 (tuple): x, y coordinates of point1
        p2 (tuple): x, y coordinates of point2

    Returns: (float) angle in degrees between the two points.

    """
    return math.atan2(
        p2[0] - p1[0],
        p2[1] - p1[1]
    ) * 180 / math.pi


def extractobjects(polys, codeextractor, objectextractor):
    """Extract the interesting information from the polygons.

    :polys: fiona.collection.Collection of polygons
    :codeextractor: function applied to each element in polys. Extracts a
        unique code from that element
    :objectextractor: function applied to each element in polys. Extracts
        dictionary of the useful parts of that object.
    :returns: {code: {interesting parts}}

    """
    output = {}
    for p in polys:
        output[codeextractor(p)] = objectextractor(p)

    return output


def findextent(polys):
    """Finds the maximum and minimum coordinates in the polygons.

    :polys: list of polygons
    :returns: object containing extents

    """
    bboxes = []
    for p in polys:
        s = shape(p['geometry'])
        bboxes.append(s.bounds)

    bboxes = array(bboxes)
    return {
        'min_x': min(bboxes.min(axis=0)[[0, 2]]),
        'min_y': min(bboxes.min(axis=0)[[1, 3]]),
        'max_x': max(bboxes.max(axis=0)[[0, 2]]),
        'max_y': max(bboxes.max(axis=0)[[1, 3]]),
    }
