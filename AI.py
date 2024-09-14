
from PIL import ImageEnhance , Image
from matplotlib import pyplot

im = Image.open("ペットボトル.jpg")
fig, ax = pyplot.subplots()
im_enhanced = ImageEnhance.Brightness(im).enhance(2.0)


