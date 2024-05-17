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
        fin = [emojis.decode(tab[0].split("\n")[0].strip())[:32], tab[1].strip()]
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
                    s = emojis.decode(row[1])[:32]
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

    columns = shutil.get_terminal_size().columns
    # print("Lorem ipsum dolor sit amet, qui minim labore\nadipisicing minim sint\n cillum sint consectetur cupidatat.".center(columns))
    # exit()
    while True:

        allTeams = getScoreboard()
        # for i in range(len(allTeams)):
        #     
        #     print(allTeams[i][0], (allTeams[i][0].encode()), onSiteTeams[2], (onSiteTeams[2].encode()))  
            

        # rr = [team for team in ]
        res = [team for index, team in enumerate(allTeams) if emojis.decode(team[0])[:32] in onSiteTeams]
        # print(res,"\n\n", old_res)
        # __import__('pprint').pprint(res)
        fin =  [team.insert(0,index+1) or team for index, team in enumerate(res)][:10]

        if res == old_res:
            old_res = copy.deepcopy(res)
            continue
        tab = tabulate(fin, heders,tablefmt="rounded_grid")
        st = tab.split("\n")[0]



        out = (chr(27) + "[2J")+"\n"+ title +"\n" + tab
        # print(out.encode())
        cout = "".join([line.center(columns) for line in out.split("\n")])
        # print(out.center(columns))
        print(cout)
        old_res = copy.deepcopy(res)
        # print(tab)
        time.sleep(10)
        # os.system("clear")

        # print(res)
    return res


if __name__ == "__main__":
    # getScoreboard()

    # print(getOnSiteTeams())
    # print(getScoreboard())

    
    run()
    # print(run())
    pass
    
