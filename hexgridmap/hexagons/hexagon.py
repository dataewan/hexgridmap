"""Geometric operations based on a hexagonal shape.
"""
import math
import numpy as np
from shapely.geometry.polygon import LinearRing


class Hexagon(object):

    """Hexagon class.
    """

    def __init__(self, x, y, D, H, o_x, o_y, max_x, max_y):
        """x, y, w, h, o_x, o_y
        Args:
            x (int): x grid coordinate
            y (int): y grid coordinate
            D (float): width of a hexagon
            H (float): height of a hexagon
            o_x (float): grid origin x coordinate
            o_y (float): grid origin y coordinate
            max_x (int): grid maximum x coordinate
            max_y (int): grid maximum y coordinate
        """
        self.x = x
        self.y = y
        self.D = D
        self.H = H
        self.o_x = o_x
        self.o_y = o_y
        self.max_x = max_x
        self.max_y = max_y

        # the odd columns are offset up, precalculate this.
        self.oddcolumn = x % 2 == 1

    def __str__(self):
        return (
            """
            x:\t{x}
            y:\t{y}
            D:\t{D}
            H:\t{H}
            o_x:\t{o_x}
            o_y:\t{o_y}
            geo:\t{geo}
            oddcolumn:\t{oddcolumn}
            """.format(
                x=self.x,
                y=self.y,
                D=self.D,
                H=self.H,
                o_x=self.o_x,
                o_y=self.o_y,
                geo=self.to_geographic(),
                oddcolumn=self.oddcolumn
            )
        )

    def to_geographic(self):
        """Returns the geographic coordinates of this point.

        Returns:
            (float, float): Geographic coordinates of this point.

        """
        # x coordinate. Start at the origin, each hex has 1.5 D contribution
        geo_x = self.o_x + self.x * self.D * 1.5
        # y coordinate. Start at the origin, each hex has 1 H contribution. If
        # we are on an odd column then shift it up by 0.5 H.
        adjustment = (self.H / 2) if self.oddcolumn else 0
        geo_y = self.o_y + self.y * self.H + adjustment
        return (geo_x, geo_y)

    def to_poly(self):
        """Convert to a polygon.

        Returns:
            (shapely.geometry.polygon.LinearRing): Outline of the hexagon.

        """
        centre = self.to_geographic()

        # the corners of a hexagon are at 60 degree increments. Start halfway
        # through an increment because we have flat topped ones
        DEG_TO_RAD = math.pi / 180
        angles = [
            30 * DEG_TO_RAD,
            90 * DEG_TO_RAD,
            150 * DEG_TO_RAD,
            210 * DEG_TO_RAD,
            270 * DEG_TO_RAD,
            330 * DEG_TO_RAD
        ]

        return LinearRing(
            [
                (
                    centre[0] + self.D * math.sin(t),
                    centre[1] + self.D * math.cos(t)
                )
                for t in angles
            ]
        )

    def find_neighbours(self):
        """
        Find the immediate neighbours of this hexagon. Easiest to do through a
        lookup table.

        Returns:
            (list): List containing the grid coordinates of this point's
                neighbours as tuples of grid coordinates.
        """
        x = self.x
        y = self.y
        if self.oddcolumn:
            neighbours = [
                (x + 0, y + 1),
                (x + 1, y + 1),
                (x + 1, y + 0),
                (x + 0, y - 1),
                (x - 1, y + 0),
                (x - 1, y + 1),
            ]
        else:
            neighbours = [
                (x + 0, y + 1),
                (x + 1, y + 0),
                (x + 1, y - 1),
                (x + 0, y - 1),
                (x - 1, y - 1),
                (x - 1, y + 0),
            ]

        # need to trim the neighbours so they don't go outside the grid
        def checkneighbour(hexagon):
            return hexagon[0] >= 0 and \
                hexagon[0] < self.max_x and \
                hexagon[1] >= 0 and \
                hexagon[1] < self.max_y

        return list(filter(checkneighbour, neighbours))

    def find_neighbour_in_direction(self, angle, sd=10):
        """Find the neighbour if you take the centre of this point and draw a
        line at an angle from it

        Args:
            angle (float): angle in degrees

        Returns: (tuple): grid ref of neighbour

        """
        if self.oddcolumn:
            angles = [
                [30, (0, 1)],
                [90, (1, 1)],
                [150, (1, 0)],
                [210, (0, -1)],
                [270, (-1, 0)],
                [330, (-1, 1)],
                [361, (0, 1)],
            ]
        else:
            angles = [
                [30, (0, 1)],
                [90, (1, 0)],
                [150, (1, -1)],
                [210, (0, -1)],
                [270, (-1, -1)],
                [330, (-1, 0)],
                [361, (0, 1)],
            ]

        d = np.random.normal(0, sd)

        for a in angles:
            if (angle + d) <= a[0]:
                return (self.x + a[1][0], self.y + a[1][1])


    def distance_to_point(self, point):
        """Return the distance to a given point.

        Args:
            point (tuple): geometric coordinates of point

        Returns: 
            (float): euclidean distance from centre of this hex to the point

        """
        centre = self.to_geographic()
        return np.sqrt(
            (point[0] - centre[0])**2 + 
            (point[1] - centre[1])**2 
        )
