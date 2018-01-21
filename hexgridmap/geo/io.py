"""Function to load shapefile."""

import fiona
import geojson
from shapely.geometry import mapping


def loadshapefile(path):
    """Load the shapefile as python objects

    :path: path of the shapefile
    :returns: fiona.collection.Collection of polygons

    """
    return fiona.open(path)


def to_geojson(hexgrid, filename):
    """Write out the hexgrid assignment to geoJSON format.

    Args:
        hexgrid (Hexgrid): Hexgrid object that should have an assignment. So
            the `fit()` function should have been run.

    """
    def to_polygon(code):
        gridcoords = hexgrid.assignment[code]
        hexagon = hexgrid.grid[gridcoords]
        properties = hexgrid.objects[code]
        # drop the centroid, that was something that I calculated.
        properties.pop('centroid', None)
        # also stick the code on because I want that code.
        properties['code'] = code
        polygon = geojson.Polygon(
            mapping(hexagon.to_poly())['coordinates'],
            properties=properties
        )
        return polygon

    polygons = [
        to_polygon(code) for code in hexgrid.assignment.keys()
    ]
    collection = geojson.GeometryCollection(polygons)
    with open(filename, 'w') as f:
        geojson.dump(collection, f, sort_keys=True)
