#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 00:28:42 2021

@author: em
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import datetime

def clean_K(string):
    return int(float(string[:-1])*1000)

def get_monday(year, month, day):
    
    date_=datetime.date(year, month, day)
    monday=date_+datetime.timedelta(days=-date_.weekday())

    return monday

def get_data(year, month, day):
    
    month_str=str(month)
    day_str=str(day)
    
    if month<10:
        month_str='0'+str(month)
    if day<10:
        day_str='0'+str(day)
    url='https://www.rollingstone.com/charts/albums/{}-{}-{}/'.format(str(year),month_str, day_str)
    page=requests.get(url)
    soup=BeautifulSoup(page.content, 'html.parser')
    
    top=soup.find(class_='l-section__charts c-chart__table--single c-chart__table--first')
    chart=soup.find_all('section', class_='l-section__charts c-chart__table--single')
    chart.append(top)
    
    monday=get_monday(year, month, day)
    
    url='https://www.rollingstone.com/wp-admin/admin-ajax.php?counter=15&chart=albums&results_per=185&chart_date={}%20{}%2C%20{}&is_eoy=0&eoy_year=0&action=rscharts_fetch_subchart'.format(monday.strftime('%B')[:3], str(monday.day), str(monday.year))
    further_req=requests.get(url)
    data=json.loads(further_req.content)
    data=data['data']
    
    soup=BeautifulSoup(data, 'html.parser')
    further_chart=soup.find_all('section',class_='l-section__charts c-chart__table--single')
    
    for album in further_chart:
        chart.append(album)
    
    with open('top200_{}-{}-{}.txt'.format(monday.strftime('%B')[:3], str(monday.day), str(monday.year)), 'w+') as file:
        for album in chart:
            file.write(str(album))
            file.write('@')
    
    return chart

def load_data(year, month, day):
    monday=get_monday(year, month, day)
    with open('top200_{}-{}-{}.txt'.format(monday.strftime('%B')[:3], str(monday.day), str(monday.year)), 'r+') as file:
        chart_str=file.read()
        chart=chart_str.split('@')
    chart=chart[:-1]
    
    return chart

class Entry:
    def __init__(self, album_html):
        soup=BeautifulSoup(album_html, 'html.parser')
    
        self.ranking=soup.find(class_='c-chart__table--rank').getText()
        self.ranking=int(self.ranking)
        
        self.album=soup.find(class_='c-chart__table--title')
        self.album=self.album.find('p').getText()
        
        self.artist=soup.find(class_='c-chart__table--caption').getText()
        
        self.album_units=soup.find(class_='c-chart__table--stat-base c-chart__table--album-units')
        self.album_units=self.album_units.find('span').getText()
        
        if 'K' in self.album_units:
            self.album_units=clean_K(self.album_units)
        
        
        self.album_sales=soup.find(class_='c-chart__table--stat-base c-chart__table--album-sales')
        self.album_sales=self.album_sales.find('span').getText()
        
        if 'K' in self.album_sales:
            self.album_sales=clean_K(self.album_sales)
        
        self.song_sales=soup.find(class_='c-chart__table--stat-base c-chart__table--song-sales')
        self.song_sales=self.song_sales.find('span').getText()
        
        if 'K' in self.song_sales: 
            self.song_sales=clean_K(self.song_sales)
        
        self.song_streams=soup.find(class_='c-chart__table--stat-base c-chart__table--song-streams')
        self.song_streams=self.song_streams.find('span').getText()
        
        if 'M' in self.song_streams:
            self.song_streams=clean_K(self.song_streams)*1000
        
        elif 'K' in self.song_streams:
            self.song_streams=clean_K(self.song_streams)
        
        self.peak_position=soup.find(class_='c-chart__table--stat-base c-chart__table--peak')
        self.peak_position=self.peak_position.find('span').getText()
        if self.peak_position:
            self.peak_position=int(self.peak_position)
        
        
        self.weeks_in_chart=soup.find(class_='c-chart__table--stat-base c-chart__table--weeks-present')
        self.weeks_in_chart=int(self.weeks_in_chart.find('span').getText())
    
        self.label=soup.find(class_='c-chart__table--label')
        self.label=self.label.find('span').getText()
        
    def add_to_df(self,path='rs_album_chart.csv'):
        
        if not os.path.exists(path):
            df=pd.DataFrame(columns=self.__dict__.keys())
        
        else:
            df=pd.read_csv(path, index_col=False)
        
        df= df.append(self.__dict__, ignore_index=True)
        df.to_csv(path, index=False)
            
        

    
def main(year, month, day, csv=True):
    monday=get_monday(year, month, day)
    
    
    if not os.path.exists('top200_{}-{}-{}.txt'.format(monday.strftime('%B')[:3], str(monday.day), str(monday.year))):
        chart=get_data(year, month, day)

    chart=load_data(year, month, day)

    entries=[Entry(i) for i in chart]
    
    if csv:
        for entry in entries:
            entry.add_to_df()
    
    return entries


year=int(input('Year: '))
month=int(input('Month: '))
day=int(input('Day: '))

x=main(year, month, day)