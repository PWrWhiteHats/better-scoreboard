#!/bin/python3
import random
import shutil
import os
import time
from bs4 import BeautifulSoup
import requests
import csv
import copy
from tabulate import tabulate
import emojis
from wcwidth import wcwidth, wcswidth
truncateWidth = 48
teamCutOff = 18
refreshRate = 10

def center_with_wide_chars(text, width, fillchar=' '):
    text_width = wcswidth(text)
    if text_width >= width:
        return text
    
    total_padding = width - text_width
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    return f"{fillchar * left_padding}{text}{fillchar * right_padding}"
def getScoreboard():
    url = "https://bts.wh.edu.pl/scoreboard"
    r = requests.get(url).content
    # print(r)
    data=[]
    b =BeautifulSoup(r, "html.parser")
    table = b.find("table", "table table-striped")
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        tab = [ele for ele in cols if ele]
        fin = [(tab[0].split("\n")[0].strip())[:truncateWidth], tab[1].strip()]
        data.append(fin)
    # print(data)
    # __import__('pprint').pprint(data)
    return data

def getOnSiteTeams():
    with open('teams.csv', newline='') as csvfile:

        reader = csv.reader(csvfile, delimiter=',')

        data =[]
        is_firts=False
        for row in reader:
            if is_firts:
                if row[1].strip():
                # print(row[1])
            # print(', '.join(row))
                    s = (row[1])[:truncateWidth]
                    data.append(s)
                    # print(s)
            is_firts = True
    return data
def run():
    onSiteTeams= getOnSiteTeams()
    # print(res)
    heders = ["PLACE","TEAM", "POINTS"]
    
    
    title = "ON SITE SCOREBOARD"
    old_res = []

    # print("Lorem ipsum dolor sit amet, qui minim labore\nadipisicing minim sint\n cillum sint consectetur cupidatat.".center(columns))
    # exit()
    timer = time.time()
    oldOut=""
    oldColumns=0
    columns=0
    while True:
        
        if time.time() - timer > refreshRate: 
            timer = time.time()
            allTeams = getScoreboard()
            # for i in range(len(allTeams)):
            #     
            #     print(allTeams[i][0], (allTeams[i][0].encode()), onSiteTeams[2], (onSiteTeams[2].encode()))  
                

            # rr = [team for team in ]
            res = [team for index, team in enumerate(allTeams) if (team[0])[:truncateWidth] in onSiteTeams]
            # print(res,"\n\n", old_res)
            # __import__('pprint').pprint(res)
            fin =  [team.insert(0,index+1) or team for index, team in enumerate(res)][:teamCutOff]

            if res == old_res:
                old_res = copy.deepcopy(res)
                continue
            tab = tabulate(fin, heders,tablefmt="rounded_grid")



            out = (chr(27) + "[2J")+"\n"+ title +"\n" + tab
            # print(out.encode())
            cout = "".join([ center_with_wide_chars(line, columns) for line in out.split("\n")])
            # print(out.center(columns))
            print(cout)
            old_res = copy.deepcopy(res)
            oldOut = out
            # print(tab)
        # time.sleep(10)
        # os.system("clear")
        else:
            columns = shutil.get_terminal_size().columns
            # print(columns)
            if columns != oldColumns:
                cout = "".join([ center_with_wide_chars(line, columns) for line in oldOut.split("\n")])
                print(cout)
            oldColumns = columns

        

        # print(res)
    return res


if __name__ == "__main__":
    # getScoreboard()

    # print(getOnSiteTeams())
    # print(getScoreboard())

    
    run()
    # print(run())
    pass
    
