"""Kick off an example project"""

from hexgridmap.geo import io, operations
from shapely.geometry import shape

if __name__ == "__main__":
    polys = io.loadshapefile(
        "/Users/ewannicolson/dev/papabaiden-vizforgood/data/geo/Local_Administrative_Units_Level_1_January_2018_Ultra_Generalised_Clipped_Boundaries_in_United_Kingdom.shp"
    )

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

    # neighbours = operations.findneighbours(polys, codefunction)
    objects = operations.extractobjects(polys, codefunction, objectextractor)
    extent = operations.findextent(polys)
