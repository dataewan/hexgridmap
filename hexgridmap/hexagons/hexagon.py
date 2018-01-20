"""
"""

class Hexagon(object):

    """Hexagon class.
    """

    def __init__(self, x, y, D, H, o_x, o_y):
        """x, y, w, h, o_x, o_y
        Args:
            x (int): x grid coordinate
            y (int): y grid coordinate
            D (float): width of a hexagon
            H (float): height of a hexagon
            o_x (float): grid origin x coordinate
            o_y (float): grid origin y coordinate
        """
        self.x = x
        self.y = y
        self.D = D
        self.H = H
        self.o_x = o_x
        self.o_y = o_y

        # the odd columns are offset up, precalculate this.
        self.oddcolumn = y % 2 == 1

    def to_geographic(self):
        """Returns the geographic coordinates of this point.

        Returns:
            (float, float): Geographic coordinates of this point.

        """
        # x coordinate. Start at the origin, each hex has 1.5 D contribution
        geo_x = self.o_x + self.x * self.D * 1.5
        # y coordinate. Start at the origin, each hex has 1 H contribution. If
        # we are on an odd column then shift it up by 0.5 H.
        adjustment = (self.H / 2) if self.oddrow else 0
        geo_y = self.o_y + self.y * self.H + adjustment
        return (geo_x, geo_y)

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
            return [
                (x + 0, y + 1),
                (x + 1, y + 1),
                (x + 1, y + 0),
                (x + 0, y - 1),
                (x - 1, y + 0),
                (x - 1, y + 1),
            ]
        else:
            return [
                (x + 0, y + 1),
                (x + 1, y + 0),
                (x + 1, y - 1),
                (x + 0, y - 1),
                (x - 1, y - 1),
                (x - 1, y + 0),
            ]
