"""Function to load shapefile."""

import fiona


def loadshapefile(path):
    """Load the shapefile as python objects

    :path: path of the shapefile
    :returns: fiona.collection.Collection of polygons

    """
    return fiona.open(path)
