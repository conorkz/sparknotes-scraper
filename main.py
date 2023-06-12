from bs4 import BeautifulSoup
import re
import requests
import paramiko
from datetime import datetime
import pytz
import time
dir = r'your_sftp_directory'
roi = 'no info on the website'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('server', username='', password='')
sftp = ssh.open_sftp()
def sftp_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except:
        return False
response = requests.get('https://www.sparknotes.com/lit/', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.content, "html.parser")
for g in soup.find(class_='hub-AZ-list').find_all(class_='hub-AZ-list__card hub-AZ-list__card--byTitle'):
    link = g.find(class_='hub-AZ-list__card__title__link hub-AZ-list__card__title__link--full-card-link no-link')['href']
    title = g.find(class_='hub-AZ-list__card__title__link hub-AZ-list__card__title__link--full-card-link no-link').text.strip()
    if g.find(class_='hub-AZ-list__card__secondary hub-AZ-list__card__secondary--link no-link'):
        author = g.find(class_='hub-AZ-list__card__secondary hub-AZ-list__card__secondary--link no-link').text.strip()
    elif g.find(class_='hub-AZ-list__card__secondary'):
        author = g.find(class_='hub-AZ-list__card__secondary').text.strip()
    else:
        author = roi
    respons = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    sorpa = BeautifulSoup(respons.content, "html.parser")
    time.sleep(5)
    print(link)
    berlin = datetime.now(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S %Z')
    bf = re.sub(r"[^\w\s]", "", title)
    file_name = f'{dir}/{bf}.txt'
    suffix = 1
    while sftp_exists(sftp, file_name):
        file_name = f'{dir}/{bf}({suffix}).txt'
        suffix += 1
    with sftp.open(file_name, "w") as file:
        if sorpa.find(class_='summary_sentence nnn'):
            desc = sorpa.find(class_='summary_sentence nnn').text.strip()
        else:
            desc = roi
        file.write(f"Link: {link}\n")
        file.write(f"Title: {title}\n")
        file.write(f"Author: {author}\n")
        file.write(f"Berlin time: {berlin}\n")
        file.write(f"Description: {desc}\n")
        if sorpa.select_one('#Summary'):
            for h in sorpa.find(class_='landing-page__umbrella__sections').find_all('a'):
                url = 'https://www.sparknotes.com' + h['href']
                respon = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                sorp = BeautifulSoup(respon.content, "html.parser")
                time.sleep(6)
                if sorp.find('div', class_='layout-wrapper-2018__column layout-wrapper-2018__column--main mainTextContent main-container'):
                    print(url)
                    file.write(f"Link of the section: {url}\n\n")
                    for j in sorp.find('div', class_='layout-wrapper-2018__column layout-wrapper-2018__column--main mainTextContent main-container').find_all(['p', 'h3']):
                        file.write(j.text.strip() + '\n\n')
                if sorp.find(class_='tag--interior-pagination interior-pagination-short__link'):
                    nurl= url + sorp.find(class_='tag--interior-pagination interior-pagination-short__link')['href']
                    respo = requests.get(nurl, headers={'User-Agent': 'Mozilla/5.0'})
                    sor = BeautifulSoup(respo.content, "html.parser")
                    time.sleep(6)
                    if sor.find('div', class_='layout-wrapper-2018__column layout-wrapper-2018__column--main mainTextContent main-container'):
                        print(nurl)
                        file.write(f"Link of the section: {nurl}\n")
                        for b in sor.find('div', class_='layout-wrapper-2018__column layout-wrapper-2018__column--main mainTextContent main-container').find_all(['p', 'h3']):
                            file.write(b.text.strip() + '\n\n')
        else:
            file.write("This book has no summary\n")
sftp.close()
ssh.close()