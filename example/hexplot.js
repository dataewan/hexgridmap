const LAHNDAHN = [
  'City of London',
  'Barking and Dagenham',
  'Barnet',
  'Bexley',
  'Brent ',
  'Bromley',
  'Camden',
  'Croydon',
  'Ealing',
  'Enfield',
  'Greenwich',
  'Hackney ',
  'Hammersmith and Fulham ',
  'Haringey',
  'Harrow',
  'Havering',
  'Hillingdon',
  'Hounslow',
  'Islington',
  'Kensington and Chelsea',
  'Kingston upon Thames',
  'Lambeth ',
  'Lewisham ',
  'Merton',
  'Newham ',
  'Redbridge',
  'Richmond upon Thames',
  'Southwark',
  'Sutton',
  'Tower Hamlets',
  'Waltham Forest',
  'Wandsworth',
  'Westminster',
]


const getdimensions = (bbox, width) => {
  /* calculate the correct dimensions in both real world and pixel coordinates
   * bbox: list containing the dimensions of the bounding box
   * width: desired width of the plot in pixels
   * returns: object containing the width and height of the svg object
   */
  const [x0, y0, x1, y1] = bbox
  const aspectratio = (y1 - y0) / (x1 - x0)
  const height = width * aspectratio
  return {
    width,
    height,
    x0, x1, y0, y1
  }
}

const createsvg = (holderselector, dimensions) => {
  /* create the svg object in the right place
   * holderselector: selector of the dom element that will contain the svg
   * dimensions: dimensions object
   */
  const holder = d3.select(holderselector)
  const svgelement = holder.append('svg')
    .attr('width', dimensions.width)
    .attr('height', dimensions.height)
    .style('background-color', '#eee')
  return svgelement
}


const createscales = (dimensions) => {
  /* calculate the linear scales used for transforming between real world and
   * pixel coordinates
   * dimensions: dimensions object
   * returns: scales object
   */
  const xscale = d3.scaleLinear()
    .domain([dimensions.x0, dimensions.x1])
    .range([0, dimensions.width])

  const yscale = d3.scaleLinear()
    .domain([dimensions.y0, dimensions.y1])
    .range([dimensions.height, 0])

  return {
    xscale, yscale
  }
}

const plothexes = (data, svgelement, scales) => {
  const { geometries } = data;
  const linefunction = d3.line()
    .x(d => scales.xscale(d[0]))
    .y(d => scales.yscale(d[1]))

  const scheme = d3.schemeCategory20b

  svgelement.selectAll('polygon')
    .data(geometries)
    .enter()
    .append('polygon')
    .attr('points', d => {
      const coords = d.coordinates
      return coords.map(g => [scales.xscale(g[0]), scales.yscale(g[1])].join(',')
      ).join(' ')
    })
    .attr('fill', (d, i) => {
      if (LAHNDAHN.indexOf(d.properties.name) != -1){
        return 'red'
      }
      return scheme[i % 20]
    })
    .attr('stroke-width', 0.5)
    .attr('stroke', 'white')
    .on('mouseover', d => console.log(d.properties.name))
}

d3.json('hexes.json', (error, data) =>{
  window.d3 = d3
  window.data = data
  const bbox = data.bbox
  const dimensions = getdimensions(bbox, width=400)
  const svgelement = createsvg('#plotholder', dimensions)
  const scales = createscales(dimensions)
  const hexes = plothexes(data, svgelement, scales)
})
