import streamlit as st
from main import run
from notion import get_notion_db, OPTION_DB

if __name__ == '__main__':
    st.set_page_config('레버리지 코스트 애버리징', '🐱')

    try:
        unit = get_notion_db(OPTION_DB)[0].get('VALUE').get('number')
        num = st.number_input('투자단위', value=unit)

        with st.spinner('🏃 불러오는 중'):
            screener = run(num)
        
        st.write(f'🇺🇸 합계: **${screener.unit.sum()}** ({len(screener)}종목)')
        st.dataframe(screener.rename(columns={
            'unit': '투자단위($)',
            'price': '평단가($)',
            'loc': '1차기준($)',
            'lo': '2차기준($)',
        }), use_container_width=True)
    except Exception as e:
        st.error(e)