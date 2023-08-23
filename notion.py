import os
import requests
import pandas as pd

TICKER_DB = 'a5772abe9c524e2692833bb417396e32'
OPTION_DB = '0325e29b468a499a9b8880eca7f3893e'

def get_notion_db(db_id):
    secret_key = os.getenv('NTN_SK')
    if not (db_id or secret_key):
        print('환경 변수 오류')
        raise Exception('Please set Notion Secret Key')
    URL = f'https://api.notion.com/v1/databases/{db_id}/query'
    res = requests.post(URL, headers={
        'Authorization' : f'Bearer {secret_key}',
        'Notion-Version' : '2022-06-28'
    })
    if res.status_code != 200:
        raise Exception(f'{res.status_code}/{res.json().get("code")}/{res.json().get("message")}')
    return [el['properties'] for el in res.json().get('results')]

if __name__ == '__main__':
    # print(get_notion_db(OPTION_DB))
    # print(get_notion_db(OPTION_DB)[0].get('VALUE').get('number'))
    # print(get_notion_db(TICKER_DB))
    # print([el.get('TICKER').get('title')[0].get('plain_text') for el in get_notion_db(TICKER_DB)])
    # data = get_notion_db(TICKER_DB)
    # ticker_col = [el.get('TICKER').get('title')[0].get('plain_text') for el in data]
    # # print(ticker_col)
    # price_col = [el.get('평단가').get('number') or 0 for el in data]
    # # print(price_col)
    # df = pd.DataFrame({'TICKER': ticker_col, 'AVG': price_col})
    # print(df)
    pass