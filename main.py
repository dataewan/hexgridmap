"""Kick off an example project.

Usage:

    python main.py [[PATH OF SHAPEFILE]]
"""

from hexgridmap.geo import io, operations
from hexgridmap.hexagons import hexgrid
from shapely.geometry import shape
from joblib import Memory
import sys

if __name__ == "__main__":
    mem = Memory(cachedir="/tmp/joblib")
    polys = io.loadshapefile(sys.argv[1])

    def codefunction(x):
        return x['properties']['lau118cd']

    def objectextractor(x):
        centroid = shape(x['geometry']).centroid
        p = x['properties']
        return {
            'name': p['lau118nm'],
            'e': p['bng_e'],
            'n': p['bng_n'],
            'centroid': (centroid.x, centroid.y)
        }

    # this function takes a wee while, so cache the results
    fn = mem.cache(operations.findneighbours)
    neighbours = fn(polys, codefunction)

    objects = operations.extractobjects(polys, codefunction, objectextractor)
    extent = operations.findextent(polys)

    h = hexgrid.Hexgrid(objects, extent, neighbours, n_x=36,
                        padding={'max_x': 50e3})

    h.assigninitial()
    h.fit()

    # io.to_geojson(h, './example/hexes.json')
