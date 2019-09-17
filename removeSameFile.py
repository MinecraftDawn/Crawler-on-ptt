import os
from time import time

sTime = time()
dirPath = "images/"
directory = os.listdir(dirPath)
fileSet = set()

for index,fileName in enumerate(directory):
    if time() - sTime > 10:
        sTime = time()
        print(index, '/', len(directory))
    filePath = dirPath + fileName
    file = open(filePath, "rb")
    fileContent = file.read()
    file.close()
    
    fileHash = hash(fileContent)
    
    if fileHash in fileSet:
        print(filePath)
        os.remove(filePath)
    else:
        fileSet.add(fileHash)
        
        