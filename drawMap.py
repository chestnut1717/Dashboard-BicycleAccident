import pandas as pd
import folium
from folium import plugins

def get_data():
    df = pd.read_excel('dashboard_data/교통약자다발지점_사고지표_대시보드.xlsx')
    return df

def get_gwlist(df):
    return sorted(list(df['광역'].unique()))

def get_gclist(df, gw):
    return sorted(df[df['광역'] == gw]['기초'].unique()) + ['전체']

def select_road(df, gw, gc):
    if gc =='전체':
        tmp_df = df[(df['광역'] == gw)].reset_index(drop=True)
    else:
        tmp_df = df[(df['광역'] == gw) & (df['기초'] == gc)].reset_index(drop=True)
    
    return tmp_df[['지점명', '주요사고유형', '건수', '사망(명)', '중상(명)', '경상(명)', '부상(명)', '심각도(명)', '위도', '경도']]

class Map:
    def __init__(self, df, gc):
        self.df = df
        self.zoom_start = 10 if gc== '전체' else 13
    

    # popup화면 html
    @staticmethod
    def html_render(df, idx):
        loc_name   = df.loc[idx, ['지점명']][-1]
        death      = df.loc[idx, ['사망(명)']][-1]
        wound_high = df.loc[idx, ['중상(명)']][-1]
        wound_mdl  = df.loc[idx, ['경상(명)']][-1]
        wound_low  = df.loc[idx, ['부상(명)']][-1]
        acc_rsn    = df.loc[idx, ['주요사고유형']][-1]
        severity   = df.loc[idx, ['심각도(명)']][-1]
        sev_level  = ""
        
        death_color = ""
        wound_high_color = ""
        wound_mdl_color = ""
        wound_low_color = ""
        severity_color = ""
        
        # 색깔 지정
        if death < 1:
            death_color = "var(--color-black)"
        else:
            death_color = "var(--color-deep-red)"
            
        if wound_high < 1:
            wound_high_color = "var(--color-black)"
        elif wound_high < 3:
            wound_high_color = "var(--color-orange)"
        else:
            wound_high_color = "var(--color-deep-red)"           
            
        if wound_mdl < 3:
            wound_mdl_color = "var(--color-black)"
        elif wound_mdl < 4:
            wound_mdl_color = "var(--color-orange)"
        else:
            wound_mdl_color = "var(--color-deep-red)" 
        
        if wound_low < 3:
            wound_low_color = "var(--color-black)"
        elif wound_low < 4:
            wound_low_color = "var(--color-orange)"
        else:
            wound_low_color = "var(--color-deep-red)"  
        
        if severity <= 8 and death < 1:
            sev_level = "주의"
            severity_color = "var(--color-black)"
        elif severity <= 16:
            sev_level = "위험"
            severity_color = "var(--color-orange)"
        else:
            sev_level = "매우 위험"
            severity_color = "var(--color-deep-red)" 
            
        html="""
            <html>
              <head>
                <style>
                  :root {
                    /* Color*/
                    --color-black: #000000;
                    --color-orange: #FEB139;
                    --color-deep-red: #FF0000;

                  }

                  * {
                    box-sizing: border-box;
                  }
                  div.layout{
                    margin: auto;
                    width: 300px;
                    height: 300px;

                  }

                  table{
                    width: 100%;
                    height: 100%;
                    border-collapse: collapse;
                    background-color: #FFF6EA;
                    text-align: center;

                  }


                  tr.locName{
                    height: 40px;
                  }



                  tr.accRsn,.severity{
                    height: 40px;
                  }

                  td,th{
                    border: 3px solid white;
                  }
                  span{
                    font-weight: bold;
                  }

                  /* 색깔 */

                  span#death{
                    color: """ + death_color + """;
                  }

                  span#woundHigh{
                    color: """ + wound_high_color + """;
                  }

                  span#woundMdl{
                    color: """ + wound_mdl_color + """;
                  }
                  
                   span#woundLow{
                    color: """ + wound_low_color + """;
                  }

                  span#sev{
                    color: """ + severity_color + """;
                  }



                </style>
              </head>
              <body>
               <div class="layout">
                  <table>
                    <thead class="info">
                      <tr class="info locName"> 
                        <th colspan="2"><span id="loc">""" + loc_name + """</span></th>
                      </tr>
                    </thead>
                    <tbody class="info">

                      <tr class="info accCnt">
                        <td>사망 : <span id="death">""" + str(death) + """</span></td>
                        <td>중상 : <span id="woundHigh">""" + str(wound_high) + """</span></td>
                      </tr>
                      <tr class="info accCnt">
                        <td>부상 : <span id="woundMdl">""" + str(wound_mdl) + """</span></td>
                        <td>경상 : <span id="woundLow">""" + str(wound_low) + """</span></td>
                      </tr>
                      <tr class="info accRsn">
                        <td colspan="2">사고원인 : <span id="rsn">""" +  acc_rsn + """</span></td>
                      </tr>
                      <tr class="info severity">
                        <td colspan="2">위험도 : <span id="sev">""" + sev_level +"""</span></td>
                      </tr>
                     </tbody>
                  </table>

                  </div>


              </body>
            </html>
            """
     
        iframe = folium.branca.element.IFrame(html=html, width=320, height=320)
        popup = folium.Popup(iframe, max_width=500)

        return popup
    
    @staticmethod
    def set_severity_level(df, idx):
        death = df.loc[idx, ['사망(명)']][-1]
        severity = df.loc[idx, ['심각도(명)']][-1]
        if severity <= 8 and death < 1:
            sev_level = "주의"
            severity_color = "var(--color-black)"
        elif severity <= 16:
            sev_level = "위험"
            severity_color = "var(--color-orange)"
        else:
            sev_level = "매우 위험"
            severity_color = "var(--color-deep-red)" 
        
        return sev_level
    
    # 색깔 warning png file 가져오기
    @staticmethod
    def load_icon_img(color):
        try:
            url_file = f'icon/{color}.png'
            return url_file
        except:
            print('없는 색깔입니다.')
        
    # icon 색깔 설정
    @staticmethod
    def set_icon(df, idx):
        sev_level = Map.set_severity_level(df, idx)
        if sev_level =='주의':
            url_file = Map.load_icon_img('yellow')
        
        elif sev_level =='위험':
            url_file = Map.load_icon_img('red')
           
        else:
            url_file = Map.load_icon_img('black')
            
        icon = folium.features.CustomIcon(url_file, icon_size=(40,40))
        return icon, sev_level
    
    
    # 전체적인 지도 그리는 메소드
    def draw_map(self, width, height):
        
        m = folium.Map(
                        location = [self.df['위도'].mean(), self.df['경도'].mean()], 
                        min_zoom = 7,
                        zoom_start=self.zoom_start,
                        # scrollWheelZoom=False,
                        width=width, 
                        height=height
        )


        # 세부 Grouping 화면
        fg = folium.FeatureGroup()
        m.add_child(fg)

        g1 = plugins.FeatureGroupSubGroup(fg)
        m.add_child(g1)

        g2 = plugins.FeatureGroupSubGroup(fg)
        m.add_child(g2)

        g3 = plugins.FeatureGroupSubGroup(fg)
        m.add_child(g3)

        # 각각의 등급별 지점 개수 count
        w1, w2, w3 = 0, 0, 0

        for idx in range(len(self.df)):
            location = self.df.loc[idx, ['지점명']][-1]
            lat = self.df.loc[idx, ['위도']]
            lon = self.df.loc[idx, ['경도']]
            icon, group =  Map.set_icon(self.df, idx)
            marker = folium.Marker(
                          location = [lat, lon],
                          popup = Map.html_render(self.df, idx),
                          tooltip = location,
                          icon = icon
                          )

            marker.add_to(m)

            # 각 위험등급별로 subgroup
            if group == '주의':
              marker.add_to(g1)
              w1 += 1
            elif group == '위험':
              marker.add_to(g2)
              w2 += 1
            else:
              marker.add_to(g3)
              w3 += 1

        # group naming
        fg.layer_name = f'전체({w1+w2+w3})'
        g1.layer_name = f'주의({w1})'
        g2.layer_name = f'위험({w2})'
        g3.layer_name = f'매우 위험({w3})'
        


        folium.LayerControl(collapsed=False,).add_to(m)
        
  
        return m