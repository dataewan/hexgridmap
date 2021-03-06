"""
"""

import numpy as np
import random
from scipy.spatial import KDTree
import itertools
from . import hexagon
from ..geo import operations


class Hexgrid(object):

    """Hexgrid object describes a hexagonal grid that encompasses a geographic
    area.
    """

    def __init__(self, objects, extent, neighbours, n_x=None, n_y=None,
                 padding=None):
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
            padding (dict): dictionary containing any padding that I want to
                apply to the grid.

        """
        self.objects = objects
        self.extent = extent
        self.neighbours = neighbours
        self.n_x = n_x
        self.n_y = n_y
        self.padding = padding

        # check that either x or y number of hexes is set.
        if n_x is None and n_y is None:
            raise ValueError("Specify number of hexagons in x or y axis")

        if n_x is not None and n_y is not None:
            raise ValueError("Only one value for number of hexagons required.")

        if n_x is not None and n_x % 2 != 0:
            raise ValueError("n_x needs to be even number.")

        if self.padding is not None:
            self.applypadding()

        self.calculategriddimensions()
        self.creategrid()

    def applypadding(self):
        """Apply an adjustment to the grid to make it a nicer fit.
        """
        for component in ['min_x', 'max_x', 'min_y', 'max_y']:
            if component in self.padding:
                self.extent[component] += self.padding[component]

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

    def creategrid(self):
        """Form the grid object.
        """
        self.grid = {}
        for x in range(self.n_x):
            for y in range(self.n_y):
                self.grid[(x, y)] = hexagon.Hexagon(x, y, self.D, self.H,
                                                    self.extent['min_x'],
                                                    self.extent['min_y'],
                                                    self.n_x,
                                                    self.n_y)
        self.extent['max_x'] += self.D

    def fit(self):
        """Assign the geographic objects to the grid, optimise their placement.

            First start by giving all objects an initial position close to
        their correct point.
            Then check for overlaps and points that should be neighbouring that
        aren't. Move things around as needed.
        """
        self.assigninitial()

        overlaps = self.findoverlaps()

        def getoverlapped(x):
            """
            Find grid references that have multiple assigments.
            """
            return len([
                i for i in overlaps.values()
                if i > 1
            ])


        while getoverlapped(overlaps) > 0:
            print(getoverlapped(overlaps))
            gridref_tofix = self.findmostoverlapped(overlaps)
            fix = self.fixoverlap(gridref_tofix)
            if fix is not None:
                self.applychain(fix)
                overlaps = self.findoverlaps()
            else:
                print(
                    'Failed to find a fix for this one {}'.format(
                        gridref_tofix
                    )
                )

    def assigninitial(self):
        """Find an initial point for all the geographic objects.

        For each centroid, find the nearest neighbour in the hexgrid
        coordinates.
        """
        hexcentres = np.array([
            h.to_geographic() for h in self.grid.values()
        ])
        gridcoords = list(self.grid.keys())

        kdt = KDTree(hexcentres)

        self.assignment = {}
        for code, geoobject in self.objects.items():
            # assign the code to the grid coordinate closest to the centroid
            self.assignment[code] = gridcoords[
                kdt.query(geoobject['centroid'])[1]
            ]

    def findoverlaps(self):
        """Find any points on the grid that have multiple hexes assigned.

        Returns:
            (dict): {gridreference: number of assignments}
        """
        assignments = list(self.assignment.values())
        assignments.sort()
        overlaps = {
            k: sum([1 for _ in g])
            for k, g in itertools.groupby(assignments)
        }
        return overlaps

    def findmostoverlapped(self, overlap):
        """Find a gridreference from the overlaps to fix.

        Pick the most overlapped grid reference, a random one from the set if
        multiple have the same number of overlaps.

        Args:
            overlap (dict): {gridreference: numberofassignments}

        Returns: (tuple): gridreference to fix

        """
        mostoverlapped = [
            k for k, v in overlap.items()
            if v == max(overlap.values())
        ]
        return random.choice(mostoverlapped)

    def fixoverlap(self, gridref):
        """Find a reassignment for a code at hex gridref.

        Args:
            gridref (tuple): grid coordinates of hex containing multiple
                assignments.
        """
        def findswap(code, previousgridref, nextgridref, swaps, alreadymoved):
            """Which chain of swaps should we do?

            Recursive function. Calculates all the chains that move one code
            from a hex to a neighbouring hex.

            Args:
                code (str): code that we're trying to swap
                previousgridref (tuple): x and y coordinates of the gridref to
                    swap from.
                nextgridref (tuple): x and y coordinates of the gridref to
                    check if we can move to
                swaps (list): list of movements performed
                alreadymoved (list): list containing the codes that have
                    already moved in this chain
            """
            # add the code to the list of codes that have already been moved
            alreadymoved.append(code)
            # is the place we're trying to swap to empty?
            isempty = nextgridref not in self.assignment.values()

            # update the list of codes to swap with moving this code to the
            # nextgridref
            newswaps = list(swaps) + [(code, nextgridref)]

            if isempty:
                # we're done, and can return the end of the chain.
                return newswaps
            else:
                codestomove = [
                    k for k, v in self.assignment.items()
                    if v == nextgridref
                    and k not in alreadymoved
                ]
                pusherobject = self.objects[code]

                angles = [
                    {
                        'code': c,
                        'angle': operations.anglebetween(pusherobject['centroid'], self.objects[c]['centroid'])
                    }
                    for c in codestomove
                ]

                # HERE IS WHERE I AM
                # i need to start moving these codes out from this hex
                # start moving the furthest one first? or doesn't that matter?
                # pop them all out and then get the next one in the chain to do that as well.
                hexagon = self.grid[nextgridref]
                chains = []
                for a in angles:
                    chains.extend(
                        findswap(
                            a['code'],
                            nextgridref,
                            hexagon.find_neighbour_in_direction(a['angle']),
                            newswaps,
                            alreadymoved
                        )
                    )

                return chains

        # initiate the recursion
        # find the outermost point in this hex
        gridref_hex = self.grid[gridref]
        objects_in_hex = [k for k, v in self.assignment.items()
                          if v == gridref]

        distances = [
            (code, gridref_hex.distance_to_point(self.objects[code]['centroid']))
            for code in objects_in_hex
        ]
        startcode = max(distances, key=lambda x: x[1])[0]

        # Which angle should I move it in?
        angle_to_move = operations.anglebetween(gridref_hex.to_geographic(), self.objects[startcode]['centroid'])

        # Which hex is that?
        grid_to_move_to = gridref_hex.find_neighbour_in_direction(angle_to_move)
        swaps = []
        alreadymoved = []
        chains = findswap(
                startcode,
                gridref,
                grid_to_move_to,
                swaps,
                alreadymoved
            )
        return chains

    def applychain(self, chain):
        """Perform the swaps described in chain.

        Args:
            chain (list): list of swaps from above

        """
        for swap in chain:
            self.assignment[swap[0]] = swap[1]
