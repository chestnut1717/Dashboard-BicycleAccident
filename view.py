import streamlit as st
import drawMap
from streamlit_folium import folium_static

def show_page():
  # Streampli page

  st.set_page_config(page_title="전국 자전거 사고다발구간 조회", page_icon="🚲", layout="wide")

  df = drawMap.get_data()

  # layout
  st.sidebar.title('지역 선택')

  # 광역 / 기초
  gw_list = drawMap.get_gwlist(df)
  gw= st.sidebar.selectbox('광역', gw_list)

  gc_list = drawMap.get_gclist(df, gw)
  gc= st.sidebar.selectbox('기초(시/군/구)', gc_list)
      
  final_df = drawMap.select_road(df, gw, gc)

  # 지도 size
  size_list = ["800x600", "1200x720", "1920x1080"]
  size = st.sidebar.selectbox('지도의 크기를 선택하세요', size_list)
  width, height = [int(num) for num in size.split('x')]


  m = drawMap.Map(final_df, gc)
  map = m.draw_map(width=width, height=height)

  st.title('🚴우리 동네 자전거 사고다발구간 조회 시스템')
  folium_static(map, width=width, height=height)

if __name__ == "__main__":
    show_page()