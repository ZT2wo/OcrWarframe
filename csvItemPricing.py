import csv
import inventoryItemScraper
import requests
import time
import re
from scipy import stats

csvInvDir = 'OcrWarframe\inventory_data.csv'
csvMarketDir = 'OcrWarframe\market_data.csv'
apiUrl = 'https://api.warframe.market/v1/'

items = []
itemsFinal = []

with open(csvInvDir, 'r') as csvfile: #Extract item info
    reader = csv.reader(csvfile)
    for item in reader:
        itemData = inventoryItemScraper.Item(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7])
        items.append(itemData)
    csvfile.close

items.pop(0)

for item in items:
    if item.name.endswith(' '):
        item.name = item.name[:-1]
    itemUrlValid = item.name.replace("'", "").replace(" ", "_").replace("-", "_").lower()
    
    validFilter = '(chassis|neuroptics|systems|carapace|cerebrum)_blueprint'
    if re.search(validFilter, itemUrlValid):
        pattern = re.compile('[a-z]{1,}._[a-z]{1,}._(chassis|neuroptics|systems|carapace|cerebrum)')
        # [a-z]{1,}_[a-z]{1,}_(chassis|neuroptics|systems|carapace|cerebrum)
        itemUrlValid = re.search(pattern, itemUrlValid).group()

    if item.type == 'Prime':
        itemInfo = requests.get(apiUrl + 'items/' + itemUrlValid).json()
        for info in itemInfo['payload']['item']['items_in_set']:
            if info['url_name'] == itemUrlValid:
                item.ducat = info['ducats']
    orders = requests.get(apiUrl + 'items/' + itemUrlValid + '/orders').json() #Retrieve item order data

    relevantOrders = []

    try:
        for order in orders['payload']['orders']: #Get only the orders we care about
            if order['user']['status'] == 'ingame' and order['order_type'] == 'sell':
                relevantOrders.append(order)
        platSum = 0
        platList = []

        #Gather stat data
        for order in relevantOrders: 
            platSum += order['platinum']
            if order['platinum'] > int(item.max):
                item.max = order['platinum']
            if order['platinum'] < int(item.min):
                item.min = order['platinum']
            platList.append(order['platinum'])

        
        item.mean = round(platSum / len(relevantOrders))
        item.mode = int(stats.mode(platList)[0])
        itemsFinal.append(item)

        print(item)
    except KeyError:
        print('Error Parsing Data...  Probably OCR Misread (Check the csv for this line: %s)' % itemUrlValid)
    time.sleep(0.68)

with open(csvMarketDir, 'w', encoding='UTF8', newline='')as f:
    writer = csv.writer(f) #Start writer
    header = ['Item Name', 'Amount', 'Mean', 'Max', 'Min', 'Mode', 'Ducat', 'Type']
    writer.writerow(header) #Write to file
    for item in itemsFinal:
        data = [item.name, item.count, item.mean, item.max, item.min, item.mode, item.ducat, item.type] #Workaround since writerow() doesn't accept 2 args or objects
        writer.writerow(data)
    f.close

