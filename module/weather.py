# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:19:37 2021

날씨 긁어와서 알려주는 
"""

import requests
from pandas import DataFrame as df
from bs4 import BeautifulSoup as bs
import pandas as pd
import folium
import webbrowser
from folium.features import DivIcon
import matplotlib.pyplot as plt
import platform
from matplotlib import font_manager, rc
import math

# 지역 날씨 크롤링
def for_one_clawer(keyword):
    keywordSplit=keyword.split()
    html = requests.get('https://search.naver.com/search.naver?query='+keywordSplit[0]+'날씨')
    soup=bs(html.text,'html.parser')

    try :
        data1=soup.find('div',class_='temperature_text').find('strong').text
        data2=soup.find('p',class_='summary').text
        data3=soup.find('dl',class_='summary_list').find('dt',class_='term').text
        data4=soup.find('dl',class_='summary_list').find('dd',class_='desc').text
        data_region=soup.find('h2',class_='title').text
        dust=soup.find('li',class_='item_today').text

        cloth = '<br />&nbsp기온이 영상이네요. 너무 두꺼운 옷은 더워요!'
        if '-' in data1 :
            cloth = '<br />&nbsp기온이 영하네요. 따뜻하게 중무장 하고 외출 하세요!'

        rain = '<br />&nbsp강수확률이 없어요. 편하게 나가세요!'
        if '0%' != data4 :
            rain = '<br />&nbsp강수확률이 있어요. 우산 챙기세요!'
        return ('<b>'+data_region+' 날씨</b>&nbsp<br />&nbsp'+data1+',&nbsp'+data2.split()[3]+',&nbsp'+data3+'&nbsp'+data4+',&nbsp'+dust+
                cloth + rain)
    except :
        return '지역을 다시 입력 하세요' 


# 날씨 크롤링
def for_all_clawer(keyword):
    
     # Plot 한글 지원
    plt.rcParams['axes.unicode_minus'] = False
    if platform.system() == 'Darwin':
        rc('font', family='AppleGothic')
    elif platform.system() == 'Windows':
        path = "c:/Windows/Fonts/malgun.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        rc('font', family=font_name)
    elif platform.system() == 'Linux':
        path = "/usr/share/fonts/NanumGothic.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        plt.rc('font', family=font_name)
    else:
        print('Unknown system... sorry~~~~')
    # Plot 한글지원 END


    html = requests.get('https://search.naver.com/search.naver?query='+'전국 날씨').text
    weather_data=bs(html,'lxml').find('div',class_='map _map_normal').findAll('span')
    weather_list_before=[title.get_text() for title in weather_data]

    weather_list=[weather_list_before[(i*3):((i*3)+3)] for i in range(12)]
    
    columns_list = ['지역','날씨','기온']
    weather_df=df(weather_list,columns=columns_list)
    weather_df.set_index('지역',inplace=True)

    # 위도 경도 획득
    position=pd.read_excel('./data/naver_data.xlsx')
    position.set_index('지역',inplace=True)
    
    # 날씨 + 위도 경도
    naver_weather_df = pd.merge(weather_df,position, how='left', right_index=True,left_index=True)
    

    # if '전국' in keyword:
    maps = folium.Map(location=[35.59517902558, 128.0103345404], zoom_start=6,tiles='cartodbpositron') 

    for n in naver_weather_df.index :

        num=30+len(naver_weather_df['날씨'][n])*5
        # if '전국' in keyword :
        folium.Marker(
            [naver_weather_df['lat'][n],naver_weather_df['lng'][n]],
            radius=10,
            color='#3186cc',
            fill_color='#3186cc',
            fill=True,
            icon=DivIcon(
                html=
                    '<div style="font-size: 1pt; border-radius:10px; border:1px solid;  background-color: #fffffdd9; width:'+str(num)+'px ;text-align:center;">'+
                    '<center><b>'+n+'</b><br/>'+naver_weather_df['날씨'][n]+'<br>'+naver_weather_df['기온'][n]+'°C<br/>'+
                    '</div>'
            )

            #tooltip=('<b>'+n+' 날씨<b> : '+naver_weather_df['날씨'][n]+' 상태.<br />'+
            #'<b>현재 기온</b> : '+naver_weather_df['기온'][n])+'℃'
            ).add_to(maps)
        # elif n in keyword :
        #     res = ('# 날씨 정보 입니다. #<br>'+ n +' : '+naver_weather_df['날씨'][n]+' 상태, '+
        #     '현재 온도 : '+naver_weather_df['기온'][n]+'℃<br />')

    # if type(maps) == folium.Map :
    return maps._repr_html_()

        
def past_weather(keyword):
    try :
        keywordSplit=keyword.split()
        html = requests.get('https://search.naver.com/search.naver?query='+keywordSplit[0]+" "+keywordSplit[1]+" "+keywordSplit[2]+' 날씨').text
        soup=bs(html,'lxml')
        before_data_area=soup.find('tbody').findAll('dt')
        before_data_weather=soup.find('tbody').findAll('p',class_='dsc')
        before_data_dgree=soup.find('tbody').findAll('p',class_='temp')
        before_data_area_text=[title.get_text().strip() for title in before_data_area]
        before_data_weather_text=[title.get_text().strip() for title in before_data_weather]
        before_data_dgree_text=[title.get_text().strip() for title in before_data_dgree]

        df_area=pd.DataFrame(before_data_area_text,columns=['지역'])
        df_weather=pd.DataFrame(before_data_weather_text,columns=['날씨'])
        df_dgree=pd.DataFrame(before_data_dgree_text,columns=['기온'])

        before_test= pd.merge(df_area,df_weather,left_index=True,right_index=True)
        before_test2=pd.merge(before_test,df_dgree,left_index=True,right_index=True)
        before_test2.set_index('지역',inplace=True)

        columns_list=['지역','lat','lng']
        naver_excel=pd.read_excel('./data/naver_data.xlsx')

        naver=pd.DataFrame(naver_excel,columns=columns_list)
        naver_weather = pd.merge(before_test2,naver,left_on='지역',right_on='지역')
        naver_weather.set_index('지역',inplace=True)
        naver_weather_df=naver_weather
    except:
        return '년, 월, 일을 다시 확인해 주세요'

    maps = folium.Map(location=[35.59517902558, 128.0103345404], zoom_start=6,tiles='cartodbpositron') 

    for n in naver_weather_df.index :

        weather = naver_weather_df['날씨'][n].split('/')
        temp = naver_weather_df['기온'][n].split('/')
        num=30+len(weather[0])*5
        # if '전국' in keyword :
        folium.Marker(
            [naver_weather_df['lat'][n],naver_weather_df['lng'][n]],
            radius=10,
            color='#3186cc',
            fill_color='#3186cc',
            fill=True,
            icon=DivIcon(
                html=
                    '<div style="font-size: 1pt; border-radius:10px; border:1px solid;  background-color: #fffffdd9; width:'+str(num)+'px ;text-align:center;">'+
                    '<center><b>'+n+'</b><br/>'+weather[0]+'<br>'+temp[0]+'°C<br/>'+
                    '</div>'
            )).add_to(maps)
    return maps._repr_html_()

# 전국 미세먼지 크롤링
def all_dust(keyword):

     # Plot 한글 지원
    plt.rcParams['axes.unicode_minus'] = False
    if platform.system() == 'Darwin':
        rc('font', family='AppleGothic')
    elif platform.system() == 'Windows':
        path = "c:/Windows/Fonts/malgun.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        rc('font', family=font_name)
    elif platform.system() == 'Linux':
        path = "/usr/share/fonts/NanumGothic.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        plt.rc('font', family=font_name)
    else:
        print('Unknown system... sorry~~~~')
    # Plot 한글지원 END


    url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=미세먼지"
    html_dust = requests.get(url).text
    soup_dust = bs(html_dust, 'lxml')
    
    dust_condition = soup_dust.select('div.detail_box tbody tr')
    
    dust_condition_text = [title.get_text() for title in dust_condition[:18]]    
    dust_condition_table = [line.split() for line in dust_condition_text]
    
    columns_list = ['지역','현재','오전예보','오후예보']
    dust_condition_pd= pd.DataFrame(dust_condition_table[1:], columns=['지역']+[words for words in dust_condition_table[0][1:]])
    dust_condition_pd.set_index('지역',inplace=True)
    
    # 위도 경도 획득
    position=pd.read_excel('./data/naver_data.xlsx')
    position.set_index('지역',inplace=True)
    
    # 미세먼지 + 위도 경도
    dust_condition_last = pd.merge(dust_condition_pd,position, how='left', right_index=True,left_index=True)
    

    # 지도 생성 + 답변 생성
    res = '# 미세먼지 정보 입니다. #<br>'
    maps = ''

    #지도에 마크 표시
    maps = folium.Map(location=[35.59517902558, 128.0103345404], tiles='cartodbpositron',zoom_start=7)


    for n in dust_condition_last.index:
        num=40
        maxLen = max(len(dust_condition_last['오전예보'][n]),len(dust_condition_last['오후예보'][n]))
        num=num+maxLen*10
        folium.Marker(
            [dust_condition_last['lat'][n],dust_condition_last['lng'][n]],
            radius=10,
            color='#3186cc',
            fill_color='#3186cc',
            fill=True,
            icon=DivIcon(
            html=('<div style="font-size: 1pt; border:1px solid; border-radius : 10px; background-color: #fffffdd9; width:'+str(num)+'px ;">'+
                '<div style="text-align:center"><b>'+str(n)+'</b></div>'+
                '<b>오전</b> : '+dust_condition_last['오전예보'][n]+'<br/>'+
                '<b>오후</b> : '+dust_condition_last['오후예보'][n]+
                '</div>'),)).add_to(maps)
        res = res + n + ' 미세먼지 : 오전 - '+dust_condition_last['오전예보'][n]+ ' / 오후 - '+dust_condition_last['오후예보'][n]+'.<br />'
    return maps._repr_html_()


# 전국 아닌 미세먼지 크롤링
def dust_last(keyword):

    # Plot 한글 지원
    plt.rcParams['axes.unicode_minus'] = False
    if platform.system() == 'Darwin':
        rc('font', family='AppleGothic')
    elif platform.system() == 'Windows':
        path = "c:/Windows/Fonts/malgun.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        rc('font', family=font_name)
    elif platform.system() == 'Linux':
        path = "/usr/share/fonts/NanumGothic.ttf"
        font_name = font_manager.FontProperties(fname=path).get_name()
        plt.rc('font', family=font_name)
    else:
        print('Unknown system... sorry~~~~')

    keyword_split = keyword.split()
    url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query="+keyword_split[0]+'미세먼지'
    # Plot 한글지원 END

    try:
        html_dust = requests.get(url).text
        soup_dust = bs(html_dust, 'lxml')
        
        dust_city = soup_dust.select('span.cityname')
        dust_value = soup_dust.select('span.value em')
        
        dust_city_table = [title.get_text() for title in dust_city]
        dust_city_table_pd = pd.DataFrame(dust_city_table)
        dust_value_table = [title.get_text() for title in dust_value]
        dust_value_table_pd = pd.DataFrame(dust_value_table)
        
        merge_dust = pd.concat([dust_city_table_pd,dust_value_table_pd],axis=1)
        
        merge_dust.columns = ['위치','미세먼지']
    except:
        return '지역을 다시 확인해 주세요'
    
    
     
    '''
    #구글 map으로 위도경도 따오기
    gmaps_key = "AIzaSyC-ezB2J00Td105d4jqtdi2-JmZKuZ-5lY"
    gmaps = googlemaps.Client(key=gmaps_key)
    tasty_name = []
    for num in range(len(merge_dust)):
        if merge_dust['위치'][num]=='광주':
            merge_dust['위치'][num]='경기도 광주'
        if merge_dust['위치'][num]=='구리':
            merge_dust['위치'][num]='경기도 구리'
        tasty_name.append(merge_dust['위치'][num])
    tasty_addreess = []
    tasty_lat = []
    tasty_lng = []
    i = 0;
    for name in tasty_name:
        tmp = gmaps.geocode(name, language='ko')
        tasty_addreess.append(tmp[0].get("formatted_address"))
        
        tmp_loc = tmp[0].get("geometry")
        tasty_lat.append(tmp_loc['location']['lat'])
        tasty_lng.append(tmp_loc['location']['lng'])
        i= i+1
        print(i,"번째 주소 가져오기 수행중")
    merge_dust['lat'] = tasty_lat
    merge_dust['lng'] = tasty_lng
    # gmap에서 위도 경도 가져오기 END
    
    #경도위도 엑셀 파일 읽기
    xlsx3 = pd.read_excel('./dust_city.xlsx')
    
    #합치기
    merge_dust_last = pd.merge(merge_dust,xlsx3)
    
    
    maps=''
    for n in merge_dust_last.index:
        if((merge_dust_last['위치'][n] in keyword) and (type(maps)!=folium.folium.Map)):
            maps = folium.Map(location=[merge_dust_last['lat'][n], merge_dust_last['lng'][n]], tiles='cartodbpositron', zoom_start=9)
        if(merge_dust_last['위치'][n] in keyword):
            folium.Marker(
                [merge_dust_last['lat'][n],merge_dust_last['lng'][n]],
                radius=10,
                color='#3186cc',
                fill_color='#3186cc',
                fill=True,
                tooltip=merge_dust_last['위치'][n]).add_to(maps)
        
    ''' 
    
    dust_list=[]
    res=''
    res2=''
    for i in merge_dust.index:
          if int(merge_dust.loc[i][1]) <= 30:
              dust_list.append('좋음')
          elif 30 < int(merge_dust.loc[i][1]) <= 80:
              dust_list.append('보통')
          elif 80 < int(merge_dust.loc[i][1]) <= 150:
              dust_list.append('나쁨')
          elif int(merge_dust.loc[i][1]) > 150:
              dust_list.append('매우나쁨')
        
    merge_dust['수준']=dust_list

    #출력 ex) 현재 순천 미세먼지는 좋음[14] 입니다.
    res2 = "<b>"+keyword_split[0] +" 미세먼지 검색 결과 입니다.</b>"
    
    j = 0
    for i in merge_dust.index:
        if merge_dust.loc[i][0] in keyword_split[0]:
            res = '현재 '+keyword_split[0]+' 미세먼지는 '+merge_dust.loc[i][2]+'['+merge_dust.loc[i][1]+'] 입니다.'
        else:
            if j == 3  :
                res2 = res2+"|"
            j=j+1
            res2 = res2+'</br>&nbsp'+merge_dust.loc[i][0]+' 미세먼지는 '+merge_dust.loc[i][2]+'['+merge_dust.loc[i][1]+'] 입니다.'

    if(res==''):
        return res2
    return res















