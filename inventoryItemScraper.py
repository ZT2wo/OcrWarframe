import easyocr
import os
import image_slicer as slicer
import csv

class Item:
        def __init__(self, name, count, mean, max, min, mode):
            self.name = name
            self.count = count
            self.mean = mean
            self.max = max
            self.min = min
            self.mode = mode
        def __str__(self):
            return f'Item:{self.name :<40} Amount:{self.count :<8} Mean:{self.mean :<8} Max:{self.max :<8} Min:{self.min :<8} Mode:{self.mode :<8}'

def grossFixes(itemName):
    if 'Ivafa' in itemName:
        itemName = itemName.replace('Ivafa', 'Ivara')
    if itemName.endswith('Mag'):
        itemName = itemName[:-4]
        itemName = 'Mag ' + itemName
    return itemName

if __name__ == '__main__':

    #Define directories
    imgFullDir = 'OcrWarframe/inventory_screenshots'
    imgCutDir = 'OcrWarframe/cut_images'
    csvDir = 'OcrWarframe/inventory_data.csv'


    #Slice screenshot
    for filename in os.listdir(imgFullDir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img = os.path.join(imgFullDir, filename)
            tiles = slicer.slice(img, col=6, row=4, save=False)
            slicer.save_tiles(tiles,filename,"OcrWarframe/cut_images","png")

    reader = easyocr.Reader({'en'}, gpu=True) #Start reader

    items = []

    #Parse cut images
    for filename in os.listdir(imgCutDir):
        if filename.endswith(".png"):
            result = reader.readtext(os.path.join(imgCutDir, filename))

            itemData = []
            for text in result:
                itemData.append(text[1]) #Extract relevant data from result
            if len(itemData) != 0: #Check if image is empty
                itemName = ''

                try: #Parse item with count
                    itemCount = int(itemData[0]) #Check if a count exists

                    for idx, text in enumerate(itemData):
                        if idx != 0: #0th item already collected
                            itemName = itemName + text + " "
                        else:
                            pass
                    itemName = itemName[:-1] #Remove blank space at end
                    #Gross Fixes
                    itemName = grossFixes(itemName)

                    item = Item(itemName,itemCount,0,0,100000,0)
                    items.append(item)

                except ValueError: #Parse item without count
                    for text in itemData:
                        itemName = itemName + text + " "
                    itemName = itemName[:-1] #Remove blank space at end
                    #Gross Fixes
                    itemName = grossFixes(itemName)
                    
                    item = Item(itemName,1,0,0,100000,0) #Create item object
                    items.append(item) #Add to object list
            else:
                pass
        else:
            print('Not an png image')

        os.remove(os.path.join(imgCutDir, filename)) #File cleanup

    if os.path.exists(csvDir): #New file everytime
        os.remove(csvDir)
    else:
        pass

    with open(csvDir, 'w', encoding='UTF8', newline='')as f:
        writer = csv.writer(f) #Start writer
        header = ['Item Name', 'Amount', 'Mean', 'Max', 'Min', 'Mode']
        writer.writerow(header) #Write to file
        for item in items:
            data = [item.name, item.count, item.mean, item.max, item.min, item.mode] #Workaround since writerow() doesn't accept 2 args or objects
            writer.writerow(data)
        f.close

