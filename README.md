# hexgridmap
Create equal area hexagon grids from shapefiles.

## Why use this?

[Choropleth maps](https://en.wikipedia.org/wiki/Choropleth_map) are maps, where regions are coloured to represent some variable. For example, showing election results colouring constituencies by the political party that won them.

A pretty major problem with this is that larger areas cover a larger area of the map, so they look more important. As an example, in the UK Labour party traditionally win more city centre constituencies which are smaller in geographic area, while Conservative party tends to win in the larger but more sparsely populated rural seats. That means that [traditional choropleths](https://bl.ocks.org/animateddata/32e61728c63448fa24965c406f8a7755) give the false impression that the Conservative party are more popular than they actually are.

To get around this maps like [this](http://www.telegraph.co.uk/news/general-election-2015/11584325/full-results-map-uk-2015.html) display each constituency as a hexagon. Each hexagon has the same area, so it removes the bias described above. These are known as hexagon grid maps.

Careful positioning of the hexagons is required to make sure that it retains some of the geographic information. As far as I can tell, this is done manually. Is there any way to do this algorithmically? That's what I'm playing about with here.


# Hexagons

I never realised that hexagons were so interesting.

https://www.redblobgames.com/grids/hexagons/

I'm going to use the _odd-q vertical layout_.

This means that this is how you calculate neighbours:

```
var oddq_directions = [
   [ Hex(+1,  0), Hex(+1, -1), Hex( 0, -1),
     Hex(-1, -1), Hex(-1,  0), Hex( 0, +1) ],
   [ Hex(+1, +1), Hex(+1,  0), Hex( 0, -1),
     Hex(-1,  0), Hex(-1, +1), Hex( 0, +1) ]
]

function oddq_offset_neighbor(hex, direction):
    var parity = hex.col & 1
    var dir = oddq_directions[parity][direction]
    return Hex(hex.col + dir.col, hex.row + dir.row)
```

and this is how you convert back to pixel coordinates

```
function oddq_offset_to_pixel(hex):
    x = size * 3/2 * hex.col
    y = size * sqrt(3) * (hex.row + 0.5 * (hex.col&1))
    return Point(x, y)
```
