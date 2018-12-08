import image_slicer
import os
import sys
from os.path import isfile, join
from PIL import Image, ImageStat, ImageDraw
from numpy import average, math

#The RBG to cice number range
RANGES = [42.5, 85.0, 127.5, 170.0, 212.5]
#Max allowed tiles, limited by image_slicer
MAXTILES = 9140

#Set dice colors default is white
if len(sys.argv) > 1:
    DICECOLOR = str(sys.argv[1])
else:
    DICECOLOR = "white"

#Get running directory
path = os.getcwd()
print(path)


#Create new text file for logging tile information
textFile = open("tile_data.txt", "w")

#Find all files in directory
files = [f for f in os.listdir(path) if isfile(join(path, f))]

#Find all png images in directory
images = []
for file in files:
    if ".png" in file:
        images.append(file)

##Make image grayscale, split the image into parts, get median rgb value of all parts
for fileName in images:
    print(fileName + ":")
    textFile.write(fileName + ":\n")

    # Open and convert to grayscale
    image = Image.open(fileName).convert('LA')
    width, height = image.size
    greyName = "grey-{}".format(fileName)
    image.save(greyName)


    #Split image into parts
    numberOfTiles = 0
    if height < width:
        numberOfTiles = height
        if numberOfTiles > MAXTILES:
            numberOfTiles = MAXTILES
        else:
            searchingForTileNumber = 1
            while searchingForTileNumber:
                newNumber = numberOfTiles + height
                if newNumber > MAXTILES:
                    searchingForTileNumber = 0
                else:
                    numberOfTiles = newNumber
    else:
        numberOfTiles = width
        if numberOfTiles > MAXTILES:
            numberOfTiles = MAXTILES
        else:
            searchingForTileNumber = 1
            while searchingForTileNumber:
                newNumber = numberOfTiles + width
                if newNumber > MAXTILES:
                    searchingForTileNumber = 0
                else:
                    numberOfTiles = newNumber


    tiles = image_slicer.slice(greyName, numberOfTiles, 0)


    #Count number of tiles that were used
    i = 0
    for tile in tiles:
        i += 1
    print("Tiles: {}".format(i))
    textFile.write("Tiles: {}\n".format(i))
    dim = int(math.sqrt(i))
    print("Dimensions: {} by {} tiles".format(dim, dim))
    textFile.write("Dimensions: {} by {} tiles\n".format(dim, dim))

    diceList = []
    #Find median RGB of tiles and assign a dice number based on RGB value
    for tile in tiles:
        image = tile.image
        median = ImageStat.Stat(image).median

        medianLength = 0
        medianList = []
        for index in median:
            medianList.append(index)
            medianLength = medianLength + 1
        if medianLength < 3:
            rgbColor = medianList[0]
            medianList.append(rgbColor)

        rgbAverage = average(medianList)

        dice = 1
        if (rgbAverage <= RANGES[0]):
            dice = 6
        elif (rgbAverage > RANGES[0] and rgbAverage <= RANGES[1]):
            dice = 5
        elif (rgbAverage > RANGES[1] and rgbAverage <= RANGES[2]):
            dice = 4
        elif (rgbAverage > RANGES[2] and rgbAverage <= RANGES[3]):
            dice = 3
        elif (rgbAverage > RANGES[3] and rgbAverage <= RANGES[4]):
            dice = 2

        diceList.append(dice)

        overlay = ImageDraw.Draw(tile.image)
        overlay.text((1, 1), str(dice))

    #Save new image
    newImage = image_slicer.join(tiles)
    newImage.save("dice_range-{}".format(fileName))




    #Resize all dice images based on tile size and store them in a list
    tile = tiles[0].image
    width, height = tile.size
    i = 1
    diceImages = []
    while i <= 6:
        diceImage = Image.open(path + "\\dices\{}\dice-{}.png".format(DICECOLOR ,i))
        resizedDice = diceImage.resize((width, height))
        diceImages.append(resizedDice)
        i += 1


    # Find median RGB of tiles and assign a dice image to the tile based on RGB value
    diceIndex = 0
    for tile in tiles:
        dice = diceList[diceIndex] - 1
        resizedDice = diceImages[dice]

        tile.image = resizedDice

        diceIndex += 1

    # Save new image
    newImage = image_slicer.join(tiles)
    newImage.save("dice-{}".format(fileName))


    #Remove the grayscale image
    os.remove(path + "\\" + greyName)

    print("\n")
    textFile.write("\n")

textFile.close()