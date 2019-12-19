from Huffman import HuffmanCoding
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
#input file path
# path = r"../Test/imaaaa.bmp"
def compress(path,fun):
    h = HuffmanCoding()
    h.compress(path,fun)
def decompress(path,fun):
    h=HuffmanCoding()
    h.decompress(path,fun)


