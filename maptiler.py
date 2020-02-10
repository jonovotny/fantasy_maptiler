import sys, getopt, os, json, numpy, shutil
from math import sqrt, ceil, floor, pow
from PIL import Image, ImageChops, ImageOps, ImageFilter
from scipy import ndimage

def split(img, path, size):
	imgwidth, imgheight = img.size
	tilesx = ceil(imgwidth/size)
	tilesy = ceil(imgwidth/size)
	for i in range(0,tilesx):
		xpath = os.path.join(path, "%s" % (i))
		print("[", end = "")
		try:
			os.mkdir(xpath)
		except OSError:
			print ("Creation of the column directory %s failed" % xpath)
		for j in range(0,tilesy):
			tile = (i*size, j*size, (i+1)*size,(j+1)*size)
			oim = img.crop(tile)
			if oim.getbbox():
				oim.save(os.path.join(xpath, "%s.png" % j))
				print("o", end = "")
			else:
				print("x", end = "")
		print("]")

# Filter Implementations (Method names need to exactly match the filter type in the config file)			
def cutout(imgsrc, options):
	imgwidth, imgheight = imgsrc.size
	imgbg = Image.open(os.path.join(options["source_path"], options["bgpath"]))
	imgdif = ImageChops.difference(imgsrc, imgbg)
	imgdif = imgdif.convert('L').point(lambda x: 0 if x<options["pixel_threshold"] else 1, '1')
	np_im = numpy.array(imgdif)
	ksize = ceil(options["expand"]/2)
	if ((ksize % 2) == 0):
		y,x = numpy.ogrid[-ksize:ksize+1, -ksize:ksize+1]
	else:
		y,x = numpy.ogrid[-ksize:ksize, -ksize:ksize]
	mask = x*x + y*y <= (options["expand"]/2)*(options["expand"]/2)
	np_im = ndimage.binary_dilation(np_im, structure=mask).astype(np_im.dtype)
	imgmask = Image.fromarray(np_im).convert('L')
	imgshadow = imgmask.filter(ImageFilter.GaussianBlur(floor(options["shadow_blur"]/2)))
	imgmask = imgmask.filter(ImageFilter.GaussianBlur(2))
	imgshadow = imgshadow.transform(imgshadow.size, Image.AFFINE, (1, 0, options["shadow_offset"][0], 0, 1, options["shadow_offset"][1]))
	imgout = ImageChops.multiply(imgsrc, imgshadow.convert('RGBA'))
	imgout.putalpha(imgmask)
	return imgout

def main(argv):
	configfile = ""
	try:
		opts, args = getopt.getopt(argv,"hc:",["config="])
	except getopt.GetoptError:
		print ('Usage: maptiler.py -c <configfile, e.g. samplemap.json>')
		sys.exit()
		
	for opt, arg in opts:
		if opt == "-h":
			print ("Usage: maptiler.py -c <configfile, e.g. samplemap.json>")
			sys.exit()
		elif opt in ("-c", "--configfile"):
			configfile = arg
			
	if configfile == "":
		print ("Please provide a configuration json file, e.g. maptiler.py -c example.json")
		sys.exit()
		
		#Default values
		tilepath = 'tiles'
		tilesize = 512
		levels_min = 0
		levels_max = 4
	
	with open(configfile) as json_file:
		data = json.load(json_file)
		if "output_path" in data:
			tilepath = data["output_path"]
		if "source_path" in data:
			sourcepath = data["source_path"]
		if "tile_size" in data:
			tilesize = data["tile_size"]
		if "map_levels_min" in data:
			levels_min = data["map_levels_min"]
		if "map_levels_max" in data:
			levels_max = data["map_levels_max"]
		
		# Clear existing map
		
		if (os.path.isdir(tilepath)):
			try:
				shutil.rmtree(tilepath)
			except OSError as e:
				print("Could not delete %s : %s \n" % (dir_path, e.strerror))

		# Generate tiles
		layers = data['layers']
		
		for layer in layers:
			if (not("maps" in layer)):
				#Not a tile layer
				continue
				
			layerpath = os.path.join(tilepath, layer["name"])
			try:
				os.makedirs(layerpath)
			except OSError as e:
				print ("Could not create %s : %s \n" % layerpath, e)	
				
			#set up composite image, in case multiple maps are joined on the same layer
			compimg = Image.new('RGBA',(tilesize, tilesize), color=(0,0,0,0))
			compzoom = 1
			
			#Apply filters to individual maps and place them into the composite image
			for source in layer["maps"]:
				if source in data["sourcemaps"]:
					sourcemap = data["sourcemaps"][source]
					sourceimg = Image.open(os.path.join(sourcepath, sourcemap['path']))
					w,h = sourceimg.size
					origin = sourcemap['origin']
					scale = sourcemap['scale']
					inputlevel = sourcemap['inputlevel']
					sourcezoom = pow(2,inputlevel) * (1/scale)
					factor = 1
					origin_factor = 1
					if sourcezoom > compzoom:
						compzoom = sourcezoom
						scale = 1
						compimg = compimg.resize((floor(tilesize*compzoom), floor(tilesize*compzoom)), Image.ANTIALIAS)
					else:
						factor = compzoom/sourcezoom
					origin_factor = compzoom/pow(2,inputlevel)
					if ('filters' in sourcemap):
						for filter in sourcemap["filters"]:
							if not("source_path" in filter):
								filter["source_path"] = sourcepath
							sourceimg = globals().get(filter["type"])(sourceimg, filter)
					
					if (scale != 1 or factor !=1):
						sourceimg = sourceimg.resize((floor(w*factor), floor(h*factor)), Image.ANTIALIAS)
					compimg.paste(sourceimg,(floor(origin[0]*origin_factor), floor(origin[1]*origin_factor)))		

			#Split composite image into leaflet map tiles
			print ("Processing Layer \"%s\": " % layer["name"])
			print ("<-N-")
			for l in range (levels_min,levels_max):
				if (("minlevel" in layer and layer['minlevel'] > l) or ("maxlevel" in layer and layer['maxlevel'] < l)):
					continue
				print("Level %d: " % l)
				levelpath = os.path.join(layerpath, "%s" % (l))
				try:
					os.mkdir(levelpath)
				except OSError as e:
					print ("Could not create %s : %s \n" % layerpath, e)	
				if pow(2,l) != compzoom:
					split(compimg.resize((floor(tilesize*(pow(2,l))), floor(tilesize*(pow(2,l)))), Image.ANTIALIAS), levelpath, tilesize)
				else:
					split(compimg, levelpath, tilesize)
			print ("")
			
		# Generate html file
		print ("Creating map.html\n")
		template = open("template.html", "r")
		contents = template.readlines()
		template.close()
		replaceIdx = contents.index("<insert config json>\n");
		contents.remove("<insert config json>\n");

		contents.insert(replaceIdx, json.dumps(data, indent="\t", separators=(',', ': ')) + ";")
		mappath = os.path.join(tilepath, "map.html")
		maphtml = open(mappath, "w")
		maphtml.writelines(contents)
		maphtml.close()
		
		# Copy resources (CSS, JavaScript, Images)
		print ("Copying resource directory\n")
		shutil.copytree("resources", os.path.join(tilepath, "resources"))
		

if __name__ == "__main__":
	main(sys.argv[1:])

