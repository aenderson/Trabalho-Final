import time
tempo_inicial = time.time()
import sys

sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

from itertools import cycle
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
from functools import reduce
import multiprocessing

"""# Importando as Bibliotecas"""
import pandas as pd
import time
import numpy as np
from selenium.webdriver.common.by import By

"""# Configuração do Web-Driver"""
# Utilizando o WebDriver do Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json



# Instanciando o Objeto ChromeOptions
options = Options()
# Passando algumas opções para esse ChromeOptions
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-crash-reporter')
options.add_argument('--log-level=3')
options.add_experimental_option("detach", True)

wd_Chrome = webdriver.Chrome(options=options)


"""# Importando as Bibliotecas"""

import pandas as pd
import time
from tqdm import tqdm

# Dict com os dias da semana e as siglas
week = {
    "SU": "Sunday",
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thrusday",
    "FR": "Friday",
    "SA": "Saturday"
}

#Quantidade de jogos de cada time a serem analisados
partidas = 30

"""# Iniciando a Raspagem de Dados"""

# Com o WebDrive a gente consegue a pedir a página (URL)
wd_Chrome.get("https://www.flashscore.com/") 
time.sleep(2)

## Para jogos do dia seguinte / Comentar essa linha para os jogos agendados de hoje 
# wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow').click()
# time.sleep(2)

next_day = wd_Chrome.find_elements(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow')
for button in next_day:
    wd_Chrome.execute_script("arguments[0].click();", button)
time.sleep(2)

# Identificar o dia dos jogos
Date = wd_Chrome.find_element(By.CSS_SELECTOR, 'button#calendarMenu').text
print(f'Jogos do dia {Date[0:5]} {week[Date[6:]]}')

# Abrir os jogos fechados
display_matches = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__info')
for button in display_matches:
    wd_Chrome.execute_script("arguments[0].click();", button)

# Pegando o ID dos Jogos
id_jogos = []
## Para jogos agendados (próximos)
jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--scheduled')

## Para jogos ao vivo (live)
# jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--live')

for i in jogos:
    id_jogos.append(i.get_attribute("id"))

# Exemplo de ID de um jogo: 'g_1_Gb7buXVt'
id_jogos = [i[4:] for i in id_jogos]

jogo = {
    'ID': [], 'Date':[],'Time':[],'Country':[],'League':[],'Home':[],'Away':[],
    'golshtHome':[], 'totalHome':[], 
    'golshtAway':[], 'totalAway':[], 
    'pHome':[], 'pAway':[], 'pSum':[],
    'avgHome':[], 'sdHome':[], 'avgAway':[], 'sdAway':[], 
    'avgSum':[]
}

# Lista de países coletados
Countries = ["RUSSIA", "BELARUS", "UKRAINE"]

for x, link in enumerate(tqdm(id_jogos, total=len(id_jogos))):
    wd_Chrome.get(f'https://www.flashscore.com/match/{link}/#/match-summary/') # English

    # Checar se o país está na lista
    Country = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
    if Country in Countries:
        continue

    total, golsht = 0, 0
    golsHome, golsAway = 0, 0
    golshtAway, golshtHome = 0, 0
    golsArray = []
    mediaGolsHTHome, mediaGolsHTAway = 0, 0
    sdHome, sdAway = 0, 0
    totalHome, totalAway = 0, 0
    pHome, pAway = 0, 0
    # Pegando as Informacoes Básicas do Jogo
    try:
        Date = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
        Time = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
        Country = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
        League = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country')
        League = League.find_element(By.CSS_SELECTOR,'a').text
        Home = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__home')
        LinkHome = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName')
        LinkHome = LinkHome.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Home = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
        Away = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__away')
        LinkAway = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName')
        LinkAway = LinkAway.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Away = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName').text

        # Verificar se o nome do time tem (xxx) no final e remover
        if ")" in Home:
            pos = Home.find('(')
            Home = Home[:pos-1]
        if ")" in Away:
            pos = Away.find('(')
            Away = Away[:pos-1]
        
        total, golsht = 0, 0
        golsHome, golsAway = 0, 0
        golshtAway, golshtHome = 0, 0
        mediaGolsHTHome, mediaGolsHTAway = 0, 0
        golsArray = []
        sdHome, sdAway = 0, 0
        totalHome, totalAway = 0, 0
        pHome, pAway = 0, 0
        # Calcular a porcentagem de over 0,5 no HT de cada time
        links = [LinkHome, LinkAway]
        for index, sublink in enumerate(links):
            wd_Chrome.get(f'{sublink}results/') # English
            jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--static') #OR 'div.event__match--last'
            total, golsht = 0, 0
            gols = 0
            golsArray = []
            # print(f'{index}: {sublink}results/') # English
            for i in jogos:
                try:
                    golsHome = i.find_element(By.CSS_SELECTOR, 'div.event__part--home').text
                    golsHome = int(golsHome[1:2])
                    gols += golsHome
                    golsAway = i.find_element(By.CSS_SELECTOR, 'div.event__part--away').text
                    golsAway = int(golsAway[1:2])
                    gols += golsAway
                    # print(f'{golsHome}x{golsAway} ', end="")
                    total += 1
                    golsArray.append(golsHome+golsAway)
                    if((golsHome+golsAway) > 0):
                        golsht += 1
                    if(total>=partidas):
                        break
                except:
                    # print(f'?x? ', end="")
                    pass
            # print()
            if(index==0):
                pHome = golsht/total
                totalHome = total
                golshtHome = golsht
                mediaGolsHTHome = gols/total
                golsArray = np.array(golsArray)
                sdHome = golsArray.std() # Calcular o SD de golsArray
                # print(f'{Home} x {Away} --> {golsArray} --> {sdHome}')
                # print(f'pHome:{pHome*100:.2f} jogos:{totalHome} jogosComGolHT:{golshtHome} média:{mediaGolsHTHome:.2f} gols:{gols}')
            if(index==1):
                pAway = golsht/total
                totalAway = total
                golshtAway = golsht
                mediaGolsHTAway = gols/total
                golsArray = np.array(golsArray)
                sdAway = golsArray.std() # Calcular o SD de golsArray
                # print(f'pAway:{pAway*100:.2f} jogos:{totalAway} jogosComGolHT:{golshtAway} média:{mediaGolsHTAway:.2f} gols:{gols}')
            # print()       
    except Exception as error:
        print(f'\n{error}\nExcept: {Home} x {Away} - {link}')
        pass

    # print(Date,Time,Country,League,Home,Away,Odds_H,Odds_D,Odds_A) 
    # print(f'{Date}, {Time}, {Country}, {League}\n{Home} {pHome*100:.2f} x {pAway*100:.2f} {Away}\n') 

    # Colocar tudo dentro do df pra salvar no csv
    jogo['ID'].append(link)
    jogo['Date'].append(Date.replace(".", "/"))
    jogo['Time'].append(Time)
    jogo['Country'].append(Country.replace(";", "-"))
    jogo['League'].append(League.replace(";", "-"))
    jogo['Home'].append(Home.replace(";", "-"))
    jogo['Away'].append(Away.replace(";", "-"))
    jogo['golshtHome'].append(golshtHome)
    jogo['totalHome'].append(totalHome)
    jogo['golshtAway'].append(golshtAway)
    jogo['totalAway'].append(totalAway)
    jogo['pHome'].append(str(round(pHome, 4)).replace(".", ","))
    jogo['pAway'].append(str(round(pAway, 4)).replace(".", ","))
    jogo['pSum'].append(
        str(round((round(pHome, 4) + round(pAway, 4)), 4)).replace(".", ",")
        )
    jogo['avgHome'].append(str(round(mediaGolsHTHome, 4)).replace(".", ","))
    jogo['sdHome'].append(str(round(sdHome, 4)).replace(".", ","))
    jogo['avgAway'].append(str(round(mediaGolsHTAway, 4)).replace(".", ","))
    jogo['sdAway'].append(str(round(sdAway, 4)).replace(".", ","))
    jogo['avgSum'].append(
        str(round((round(mediaGolsHTHome, 4) + round(mediaGolsHTAway, 4)), 4)).replace(".", ",")
        )
    

# Para atualizar o CSV a cada 'n' interações.
# Colocar esse código abaixo dentro do loop acima (subir uma identação)
# Colocar uma condição para a cada 'n' interações do loop, realizar a escrita no arquivo
df = pd.DataFrame(jogo)

# Drop rows totalHome < 15 or totalAway < 15
filtered = df[ (df['totalHome'] < 15) | (df['totalAway'] < 15) ].index
df.drop(filtered , inplace=True)

df = df.sort_values(by=['pSum'], ascending=False)
df.reset_index(inplace=True, drop=True)
df.index = df.index.set_names(['Nº'])
df = df.rename(index=lambda x: x + 1)
filename = "lista_de_jogos/jogos_do_dia_"+Date.replace(".", "_")+"_last"+str(partidas)+"_SEQUENTIAL.csv"
df.to_csv(filename, sep=";")
tempo_final = time.time()

tempo_decorrido = tempo_final - tempo_inicial 

# Calcula horas, minutos e segundos
horas = int(tempo_decorrido // 3600)
minutos = int((tempo_decorrido % 3600) // 60)
segundos = int(tempo_decorrido % 60)

print(f'Programa gastou {horas} horas, {minutos} minutos e {segundos} segundos')