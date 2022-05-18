import PIL.Image
from PIL import Image
import io


def hash_image(img: Image):

	# return imagehash.average_hash(img)

	img = img.resize((4, 4))
	# img = img.convert('1')

	img_hash = 0

	for y in range(4):
		for x in range(4):
			pixel = img.getpixel((x, y))
			for channel in pixel:
				img_hash <<= 1
				if channel > 127:
					img_hash += 1

	# img.save("bin.png")
	# print("{0:x}".format(img_hash))

	return img_hash
