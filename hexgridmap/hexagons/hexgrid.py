"""
"""

import numpy as np

class Hexgrid(object):

    """Hexgrid object describes a hexagonal grid that encompasses a geographic
    area.
    """

    def __init__(self, objects, extent, neighbours, n_x=None, n_y=None):
        """
        Args:
            objects (dict): extracted geographic objects. Key is the code of
                the objects.
            extent (dict): Description of the bounding box of the objects. Max
                and min x and y coordinates.
            neighbours (dict): The neighbours of each object:
                {code: list of neighbourcodes}
            n_x (int): number of hexagons needed in the x axis.
                Have to set this _or_ n_y.
                If set this needs to be an even number.
            n_y (int): number of hexagons needed in the y axis.
                Have to set this _or_ n_x.

        """
        self.objects = objects
        self.extent = extent
        self.neighbours = neighbours
        self.n_x = n_x
        self.n_y = n_y

        # check that either x or y number of hexes is set.
        if n_x is None and n_y is None:
            raise ValueError("Specify number of hexagons in x or y axis")

        if n_x is not None and n_y is not None:
            raise ValueError("Only one value for number of hexagons required.")

        if n_x is not None and n_x % 2 != 0:
            raise ValueError("n_x needs to be even number.")

    def calculategriddimensions(self):
        """Calculate the size of grid needed.

        There are two cases, either we're making a grid with the x axis
        specified, or we're creating one with the y axis specified. Both
        logical branches are calculated in this function.

        We want the whole rectangular area to be covered by hexagons. We also
        want the hexagons to be regular hexagons. The way to achieve this is to
        make enough hexagons to cover the specified axis, and then make
        enough hexagons to at least cover the other axis.

        When covering an axis, we want hexagons to be centred on either end of
        the axis. That means that we'll have hexagons covering areas outside
        the bounding box, but that's okay.

        The grid uses an odd-q vertical layout, as described here:
            https://www.redblobgames.com/grids/hexagons/

        Difference is that I'll start in the bottom left corner to match the
        geographic cartesian coordinates.
        """
        xextent = self.extent['max_x'] - self.extent['min_x']
        yextent = self.extent['max_y'] - self.extent['min_y']
        if self.n_x is not None:
            # we need to find out how many hexagons cover the x-axis.

            # D is the length of one edge of the hexagon, or the distance from
            # the centre to any corner.
            # If we have a hex centred on either end of the axis then we get
            # D/2 contribution from each of them. We also get 3/2.D
            # contribution from each hex in the middle.
            self.D = (
                xextent /
                # N-2 lots of 3/2, plus 2 lots of 1/2 from the end ones.
                (3 / 2 * (self.n_x - 2)) + 1
            )

            # Calculate the height. From pythagoras it is √3.D
            self.H = np.sqrt(3) * self.D

            # Now the number of hexes to cover the y axis.
            # We get 1/2 H from the one at the top. How many more are required
            # to cover the rest of the axis?
            self.n_y = int(
                # can't have fractional hexes, and want to make sure we cover
                # the extent. Round up.
                np.ceil(
                    # already got 1/2 H from the first one, how many more do we
                    # need?
                    (yextent - (self.H / 2)) /
                    self.H
                ) + 1
                # remember that we've already counted that one from the top,
                # that's why add one.
            )

        if self.n_y is None:
            # we need to find out how many hexagons cover the y-axis.

            # H is the height of one hexagon. Since the start and end hexagons
            # have their centres at the ends of the axis, it means that they
            # only contribute H/2 each.
            self.H = (
                yextent / (self.n_y - 1)
            )

            # Calculate D. From pythagoras we know that it is H/√3
            self.D = self.H / (np.sqrt(3))

            # Now the number of hexes to cover the x axis.
            # We have 1/2 D from the first one, and then 3/2 D from each
            # subsequent one.
            self.n_x = int(
                # can't have fractional hexes, and want to make sure we cover
                # the extent. Round up.
                np.ceil(
                    # Already got D/2 from the first one. How many more do we
                    # need?
                    (xextent - (self.D / 2)) /
                    (self.D * 3 / 2)
                ) + 1
                # remember that we've already counted that one from the first,
                # that's why add one.
            )

            # I want to stipulate that n_x is even. If it isn't, then add one.
            # TODO: Check if I need to do this or can I work with odd numbers
            # of x hexes.
            if self.n_x % 2 == 1:
                self.n_x += 1
