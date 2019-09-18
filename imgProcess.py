import os
from PIL import Image
from time import time

sTime = time()
dirPath = "images/"
directory = os.listdir(dirPath)

inValidPath = "invalidImages/"

for index, fileName in enumerate(directory):

    if time() - sTime > 10:
        sTime = time()
        print(index, '/', len(directory))

    filePath = dirPath + fileName

    try:
        img = Image.open(filePath)
    except OSError:
        movePath = inValidPath + fileName
        os.rename(filePath, movePath)
        print(fileName)
