
# Fantasy MapTiler

A python tool to create a leaflet style map from multiple image sources.

© 2020 Johannes Novotny and released under the MIT License. See LICENSE.md.

## Example

Click to go to live version 

[![A simple example map](demo.png "Click for a demo")](https://jonovotny.github.io/map.html)
 
## Features

* Images can be placed and scaled independently, e.g. to place detail maps into a overall world map
* Automatically generated Leaflet layers, allowing users to toggle the visibility of individual map images
* Customizable zoom options for each layer, e.g. to only show detail maps at zoom levels at which they are legible
* (optional) Preliminary image filter support to create an 'underground' effect using a drop shadow
* (optional) A measuring tool with user-controllable size scale to allow accurate distance measurements
* (optional) Ability to parse marker information from a remote html source, e.g. to create city labels and quest markers

## Requirements

* [Python 3](https://www.python.org/download/releases/3.0/) (developed with 3.7.4)
* Additional Python modules: [numpy](https://numpy.org/), [PIL](https://pillow.readthedocs.io/en/stable/), [scipy](https://www.scipy.org/)

## Instructions

To create the example project run the following command on Commandline or PowerShell:

```
python maptiler.py -c example.json
```

Check the Json configuration file ([example.json](https://github.com/jonovotny/fantasy_maptiler/blob/master/example.json)) for customization options.

## Configuration

```
{
	"map_name": "Isla del Craneo",		| The name of the map, used in the title of the generated webpage
	"map_levels_min": 1,				| The minimum zoom level available on the generated leaflet map (default 0)
	"map_levels_max": 4,				| The maximum zoom level available on the generated leaflet map (default 4)
										| Due to some implementation limitations it is recommended to stay below map_max_levels 6. 
	
	"tile_size": 512,					| Size of tiles images are cut into in pixels (default 512). It is recommended to choose either 512 or 256.
	"default_lat": -256,				| 	
	"default_lng": 256,					| 
	"default_zoom": 1,					| default_lat, _lng and _zoom define the map view used when the map is loaded

	"distance_tool_enabled": true,		| Adds the measurement to the map (button with ruler symbol, top left)
	"distance_tile_size": 100,			| Size of the top level tile (i.e. tile_size) in map units
	"distance_settings": {				| Internal settings of the Leaflet.LinearMeasurement.js plugin
		"color": "#b51d21",				| Color of the measuring line and tooltip
		"unitSystem": "imperial",		| The unit system defining UNIT and SUB_UNIT. Options are "metric" [km/m], "imperial" [mi/ft] or "custom".
		"unitSystem_custom": {			| If "custom" was chosen as unitSystem, these options allow setting unit conversion between main and minor unit and unit names
			"UNIT_CONV": 1,				| Keep this setting at 1 (conversion between internal scale and map scale should be defined in "distance_tile_size")
			"SUB_UNIT_CONV": 1980,
			"UNIT": "furlong",
			"SUB_UNIT": "hand"
		}
	},
	
	"marker_tool_enabled": true,		| Adds the link generation tool to the map (button with marker symbol, top left)
										| Clicking on the map drops a marker on the map. The tooltip attached to the map encodes it's location and zoom level 
										| based on the "marker_string_format"
										| This can be used to generate links that zoom in on specific map locations.
	"marker_string_format": "&lt;li&gt;&lt;a href=&quot;https://jonovotny.github.io/map.html?lat={0}&amp;lng={1}&amp;level={2}&quot;&gt;&lt;/a&gt;&lt;/li&gt;",
										| An example format string. To generate links html characters need to be escaped (e.g. use &lt; instead of <)
										| Within the string {0} is replaced by the markers latitude, {1} byt the markers longitude and {2} by the current map zoom level.

	"source_path": "sourcemaps",		| The directory containing source map images relative to the python script execution directory
	"output_path": "example",			| The output directory relative to the python script execution directory
										| This directory will be overwritten whenever a new map is generated.
	
	"layers": [							| This list defines all layers that are available in the generated map (button with layer symbol, top left)
		{								| Layers are defined by the following attributes:
			"name": "Isla del Craneo",	| The "name" is used as the entry name in the layer dropdown menu
			"type": "base",				| "base" layers should fill the entire map area, only one base layer can be shown at a time.
			"defaultVisible": true,		| The default visibility state of a layer when the map is loaded
			"maps": [					| This list defines the image sources used to build this layer. It is possible to combine multiple images into one layer.
				"Isla del Craneo"		| Entries of this list must exist in the "sourcemaps" settings below.
			]
		},
		{
			"name": "Port Dental",
			"type": "overlay",			| "overlay" layers usually cover a smaller area of the entire map and can be toggled on and off
			"defaultVisible": true,
			"maps": [
				"Port Dental",			| An example of combining multiple detail maps into a single layer. 
				"Lone Tree Island"		| Images are combined into a composite image in the order they appear on this list.
			],
			"minlevel": 2				| The minimum zoom level for this layer, it will not be visible while zoomed out further (zoom level 0 and 1 in this example)
										| This can be used to hide the map if it is not legible while zoomed out.
		},
		{
			"name": "Nasal Cavities",
			"type": "overlay",
			"defaultVisible": false,
			"maps": [
				"Nasal Cavities"
			],
			"minlevel": 2
		},
		{
			"name": "Quests",
			"type": "overlay",
			"defaultVisible": true,		| Layers without map images can be used to toggle the visibility of text labels and markers (quest symbols in this example)
			"minlevel": 0
		}
	],
	"sourcemaps": {						| This list defines where source images should be placed within the world map.
		"Isla del Craneo": {			| The name of each entry has to the one used in the "maps" lists of layer entries above.
			"path": "exemplaria.png",	| The name of the source image file within the previously defined "source_path" directory.
			"origin": [					| Origin and scale at which the image should place within the map.
				0,						| X location of the bottom left corner of the image within the "inputlevel" in pixels. The coordinate origin is bottom left.
				0						| Y location of the bottom left corner of the image within the "inputlevel" in pixels.
			],
			"scale": 1.0,				| Image scale
			"inputlevel": 0				| The level at which the image is inserted in the image pyramid. The image size at a given level is (2^level)*tile_size.
										| E.g. a world map with a resolution of 2048*2048 pixels should be inserted at level 2 (2^2*512) in this example, to avoid a loss of quality.
		},
		"Port Dental": {
			"path": "portdental.png",
			"origin": [
				218,
				232
			],
			"scale": 0.1555,
			"inputlevel": 0				| Defining origin and scale of detail layers on the same level as the world map makes it easier to get the placement right.
		},
		"Lone Tree Island": {
			"path": "lonetree.png",
			"origin": [
				278,
				334
			],
			"scale": 0.04,
			"inputlevel": 0
		},
		"Nasal Cavities": {
			"path": "nasalcavity.png",
			"origin": [
				218,
				232
			],
			"scale": 0.1555,
			"inputlevel": 0,
			"filters": [				| Filters are applied to the image before tiling happens. Currently one a cutout filter is available, 
										| but it is possible to add custom filters to maptiler.py. Filters are applied to the image before scaling and
										| in the order they appear in the following list.
										| The dictionary of options will be passed to the filter implementation as arguments. 
				{						 
					"type": "cutout",	| The cutout filter grows a border around all features of the image that are different from the provided background image.
										| It also has an option to create a drop shadow effect to indicate that the cutout lies below the surrounding areas. 
					"bgpath": "nasalcavitybg.png",
										| The background map used to find features of interest in the source image. 
					"expand": 50,		| The extent of the border created around identified features in pixel
					"pixel_threshold": 20,
										| The threshold defining when a pixel is considered different from the background (to avoid problems with image compression artifacts)
					"shadow_offset": [	| The shadow offset in pixels. (use [0,0] for no shadow)
						10,
						-10
					],
					"shadow_blur": 5	| The Gaussian blur applied to the shadow in pixels.
				}
			]
		}
	},
	"labelsources": [					| TODO
		{
			"id": "SourceA",
			"type": "html",
			"url": "https://jonovotny.github.io/labelexample.html",
			"txtTokens": ["\">", "</a"],
			"ignoreTokens": ["<del>", "\\*\\*"],
			"latToken": "lat=",
			"lngToken": "lng=",
			"levelToken": "level=",
			"layerToken": "layer=",
			"groupTokens": ["<h2>","</h2>"],
			"groups": {
				"Worldmap Labels": {
					"labelType": "text",
					"labelStyle": "label-city"
				},
				"Port Dental Labels": {
					"labelType": "text",
					"labelStyle": "label-city",
					"minlevel": 2
				},
				"Port Dental Minor Labels": {
					"labelType": "text",
					"labelStyle": "label-city",
					"labelLayer": "Port Dental",
					"minlevel": 3
				},
				"Nasal Cavities Labels": {
					"labelType": "text",
					"labelStyle": "label-city",
					"labelLayer": "Nasal Cavities",
					"minlevel": 3
				},
				"Quests": {
					"labelType": "icon",
					"labelStyle": "questIcon",
					"labelLayer": "Quests"
				},
				"Water Labels": {
					"labelType": "text",
					"labelStyle": "label-water",
					"labelLayer": "Isla del Craneo",
					"minlevel": 0
				}
			},
			"defaultStyle": {
				"labelType": "text",
				"labelStyle": "label-region",
				"minlevel": 0,
				"labelLayer": "Isla del Craneo"
			}
		}
	]
}
```