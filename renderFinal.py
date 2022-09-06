import pandas as pd

csvMarketDir = 'OcrWarframe\market_data.csv'

with open(csvMarketDir, 'r', encoding='UTF8')as f:
    pdread = pd.read_csv(f)
    pd.set_option('display.max_rows', pdread.shape[0]+1)
    pdread = pdread.sort_values('Mean', ascending=False)
    print(pdread)
    f.close