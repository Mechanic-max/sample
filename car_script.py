from tkinter import N
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from shutil import which
import time
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
import csv
from selenium.webdriver.support.ui import Select
import re
import pandas as pd
import datetime
import requests
import json
import os
import mysql.connector

mydb = mysql.connector.connect(
  host = "node27015-env-3476383.it1.eur.aruba.jenv-aruba.cloud",
  user="root",
  password="KMLvnx37425",
  database="crawler",
)

mycursor = mydb.cursor()
class Cni():
    count = 0
    no_of_model = 0
    no_of_make = 0
    check_for_model = ""
    check_for_make = ""
    def start(self):
        options = Options()
        options.add_experimental_option("detach", True)
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument('--disable-gpu')

        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        

    def target_url(self):
        for i in range(0,1656,8):
            ul = f"https://www.quattroruote.it/tutte-le-auto/ricerca-more-desktop.html?area=ARCHIVE&itemStart={i}"
            self.driver.get(ul)
            time.sleep(5)
            try:
                self.driver.find_element_by_xpath("//button[contains(text(),'Accetta')]").click()
                time.sleep(5)
            except:
                None

            
            self.result_scrap()

        


    def result_scrap(self):
        html = self.driver.page_source
        resp = Selector(text=html)
        
        data = resp.xpath("//div[contains(@class,'c-postcar1 ')]//a[@class='c-postcar1__img-link']/@href").getall()
        for dat in data:
            results = str(dat)
            results = f"https://www.quattroruote.it{results}"
            with open("cni_links.csv",'a',newline='',encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([results])
            print(results)

            
    def sub_links(self):
        with open("cni_links.csv", 'r',encoding='utf-8') as input_file:
            reader = csv.reader(input_file,delimiter=",")
            for i in reader:
                link = str(i[0])
                self.driver.get(link)
                time.sleep(3)
                try:
                    self.driver.find_element_by_xpath("//button[contains(text(),'Accetta')]").click()
                    time.sleep(3)
                except:
                    None
                try:
                    button = self.driver.find_element_by_xpath("//button[@id='btnallestimenti']")
                    self.driver.execute_script("arguments[0].click();", button)
                except:
                    None
                time.sleep(5)
                html = self.driver.page_source
                resp = Selector(text=html)
                data_lancio = resp.xpath("normalize-space(//li[contains(text(),'Anno modello: ')]/strong/text())").extract_first()
                data_lancio= str(data_lancio)
                data_lancio1 = re.findall(r'^[^-]+', data_lancio)
                data_lancio1 = str(data_lancio1)
                data_lancio1 = data_lancio1.replace('[','')
                data_lancio1 = data_lancio1.replace(']','')
                data_lancio1 = data_lancio1.replace(',','')
                data_lancio1 = data_lancio1.replace('"','')
                data_lancio1 = data_lancio1.replace("'","")
                data_lancio1 = data_lancio1.strip()
                data_lancio = data_lancio.replace(data_lancio1,'')
                data_lancio = data_lancio.replace('-','')
                data_lancio = data_lancio.strip()
                data_lancio = f"01/01/{data_lancio}"
                data_lancio1 = f"01/01/{data_lancio1}"
                tipo_veicolo = 2
                make = resp.xpath("normalize-space(//h1[@id='page-main-title']/text()[1])").extract_first()
                model = resp.xpath("normalize-space(//h1[@id='page-main-title']/strong/text())").extract_first()
                self.save_data_in_make_table(make,tipo_veicolo)
                self.save_data_in_model_table(model,data_lancio,data_lancio1)
                data = resp.xpath("//table[@class='table table-striped margin-bottom-0 js-component-loaded']/tbody/tr/td[@class='arrow-archive']/a/@href").getall()
                for dat in data:
                    results = str(dat)
                    results = f"https://www.quattroruote.it{results}"
                    self.scrap(results)
                    

    def save_data_in_make_table(self,make,tipo_veicolo):
        if self.check_for_make == make:
            None
        else:
            mySql_insert_query = """INSERT INTO make_table (make,tipo_veicolo) 
                VALUES (%s , %s) """

            val = (make,tipo_veicolo)

            mycursor.execute(mySql_insert_query, val)
            mydb.commit()
            print(mycursor.rowcount, "record inserted in make table")
            self.no_of_make = self.no_of_make+1
            self.check_for_make = make


    def save_data_in_model_table(self,model,data_lancio,data_lancio1):
        if self.check_for_model == model:
            None
        else:
            mySql_insert_query = """INSERT INTO model_table (model,data_lancio,data_lancio1) 
                VALUES (%s , %s , %s) """

            val = (model,data_lancio,data_lancio1)

            mycursor.execute(mySql_insert_query, val)
            mydb.commit()
            print(mycursor.rowcount, "record inserted in model table")
            self.no_of_model = self.no_of_model+1
            self.check_for_model = model
        
    def scrap(self,link):
        
        try:
            self.driver.get(link)
        except:
            self.driver.close()
            self.start()
            self.driver.get(link)

        time.sleep(3)
        html = self.driver.page_source
        resp = Selector(text=html)
        
        

        equipment = resp.xpath("normalize-space(//h2[@id='page-subtitle']/text())").extract_first()
        posti =resp.xpath("normalize-space(//li[contains(text(),'Posti')]/strong/text())").extract_first()
        porte = resp.xpath("normalize-space(//li[contains(text(),'Porte')]/strong/text())").extract_first()

        serbatoio = resp.xpath("normalize-space(//li[contains(text(),'Serbatoio')]/strong/text())").extract_first()
        serbatoio = str(serbatoio)
        serbatoio = serbatoio.replace('L','')
        bagagliaio = resp.xpath("normalize-space(//li[contains(text(),'Bagagliaio')]/strong/text())").extract_first()
        bagagliaio = str(bagagliaio)
        bagagliaio = bagagliaio.replace('dm3','')
    
        altezza = resp.xpath("normalize-space(//li[contains(text(),'Altezza')]/strong/text())").extract_first()
        altezza = str(altezza)
        altezza = altezza.replace('cm','')
        altezza = altezza.strip()
        larghezza = resp.xpath("normalize-space(//li[contains(text(),'Larghezza')]/strong/text())").extract_first()
        larghezza = str(larghezza)
        larghezza = larghezza.replace('cm','')
        larghezza = larghezza.strip()
        lunghezza = resp.xpath("normalize-space(//li[contains(text(),'Lunghezza')]/strong/text())").extract_first()
        lunghezza = str(lunghezza)
        lunghezza = lunghezza.replace('cm','')
        lunghezza = lunghezza.strip()
        passo = resp.xpath("normalize-space(//li[contains(text(),'Passo')]/strong/text())").extract_first()
        passo = str(passo)
        passo = passo.replace('cm','')
        passo = passo.strip()


        massa = resp.xpath("normalize-space(//li[contains(text(),'Massa')]/strong/text())").extract_first()
        massa = str(massa)
        massa = massa.replace('kg','')
        massa = massa.strip()
        alimentazione = []
        alimentazione_all = resp.xpath("//span[@class='lh-fix icon-Icona_Economia']/parent::span/parent::li//text()").getall()
        for ali9 in alimentazione_all:
            ali9 = str(ali9)
            ali9 = ali9.strip()
            if ali9 == '' or ali9 == None:
                None
            else:
                alimentazione.append(ali9)
        
        alimentazione = str(alimentazione)
        alimentazione = alimentazione.replace('[','')
        alimentazione = alimentazione.replace(']','')
        alimentazione = alimentazione.replace('"','')
        alimentazione = alimentazione.replace("'","")
        alimentazione = alimentazione.replace(","," ")
        alimentazione = alimentazione.strip()

        
        cilindri = resp.xpath("normalize-space(//li[contains(text(),'Cilindri')]/strong/text())").extract_first()    
        cilindrata = resp.xpath("normalize-space(//li[contains(text(),'Cilindrata')]/strong/text())").extract_first()    
        

        
        omologazione_euro =resp.xpath("normalize-space(//li[contains(text(),'Omologazione')]/strong/text())").extract_first()
        omologazione_euro = str(omologazione_euro)
        omologazione_euro = omologazione_euro.replace('EURO','')
        omologazione_euro = omologazione_euro.strip()
        potenza = resp.xpath("normalize-space(//li[contains(text(),'Potenza')]/strong/text())").extract_first()
        potenza = str(potenza)
        cavalli = re.findall(r"\(.*?\)",potenza)
        cavalli = str(cavalli)
        cavalli = cavalli.replace('[','')
        cavalli = cavalli.replace(']','')
        cavalli = cavalli.replace('"','')
        cavalli = cavalli.replace("'","")
        cavalli = cavalli.replace(",","")
        cavalli = cavalli.replace("(","")
        cavalli = cavalli.replace(")","")
        cavalli = cavalli.replace("CV","")
        cavalli = cavalli.strip()
        
        potenza = potenza.replace(cavalli,'')
        potenza = potenza.replace('kW','')
        potenza = potenza.replace(' ( CV)','')
        potenza = potenza.strip()
        giri = resp.xpath("normalize-space(//li[contains(text(),'Potenza')]/text()[2])").extract_first()
        giri = str(giri)
        giri = giri.replace('a ','')
        giri = giri.replace('giri/min','')
        giri = giri.strip()
        
        coppia = resp.xpath("normalize-space(//li[contains(text(),'Coppia')]/strong/text())").extract_first()
        coppia = str(coppia)
        coppia = coppia.replace('Nm','')
        trazione = resp.xpath("normalize-space(//li[contains(text(),'Trazione')]/strong/text())").extract_first()
        cambio = resp.xpath("normalize-space(//li[contains(text(),'Cambio')]/strong/text())").extract_first()
        pneumatici_anteriori = resp.xpath("normalize-space(//h2[contains(text(),'Pneumatici anteriori')]/parent::div/following-sibling::div[1]/div/ul/li/strong/a/text())").extract_first()

        pneumatici_posteriori = resp.xpath("normalize-space(//h2[contains(text(),'Pneumatici posteriori')]/parent::div/following-sibling::div[1]/div/ul/li/strong/a/text())").extract_first()


        velocita_max = resp.xpath("normalize-space(//li[contains(text(),'Velocità max: ')]/strong/text())").extract_first()
        velocita_max = str(velocita_max)
        velocita_max = velocita_max.replace('km/h','')
        codice_allestimento = resp.xpath("normalize-space(//h2[contains(text(),'Codice identificativo')]/parent::div/following-sibling::div[1]/div/ul/li/strong/text())").extract_first()
        accelerazione_Kmh_0_100  = resp.xpath("normalize-space(//li[contains(text(),'Accelerazione 0-100 Km/h')]/strong/text())").extract_first()
        

        try:
            print()
            print("no_of_make",self.no_of_make)
            print("no_of_model",self.no_of_model)
            print("equipment:",equipment)
            print("posti:",posti)
            print("porte:",porte)
            print("serbatoio:",serbatoio)
            print("bagagliaio:",bagagliaio)
            print("altezza:",altezza)
            print("larghezza:",larghezza)
            print("lunghezza:",lunghezza)
            print("passo:",passo)
            print("massa:",massa)
            print("alimentazione:",alimentazione)
            print("cilindri:",cilindri)
            print("cilindrata:",cilindrata)
            print("omologazione_euro:",omologazione_euro)
            print("potenza:",potenza)
            print("cavalli:",cavalli)
            print("giri:",giri)
            print("coppia:",coppia)
            print("trazione:",trazione)
            print("cambio:",cambio)
            print("pneumatici_anteriori:",pneumatici_anteriori)
            print("pneumatici_posteriori:",pneumatici_posteriori)
            print("velocita_max:",velocita_max)
            print("codice_allestimento:",codice_allestimento)
            print("accelerazione_Kmh_0_100:",accelerazione_Kmh_0_100)
            print("url:",link)
            print()
        except:
            None
                
            
                # with open("Dataset_sample.csv",'a',newline='',encoding='utf-8') as file:
                #     writer = csv.writer(file)
                #     if self.count == 0:
                #         writer.writerow(['title','surname','f_name','reg_no','reg_date','first_reg_date','dob','order_engineer','first_order_engineer','university','sessions','main_activicty','disciplinary_measures','Formation','insurance','Personal_data_provided_by_the_member','suspended_from','suspended_at','province_of_birth','place_of_birth','sex','fiscal_code','vat_no','qualifying_title','year_of_qualifying','pec','email','cell_phone','website','serial_number','address','postal_code','province','location','phone','fax','link'])
                #     writer.writerow([title,surname,f_name,reg_no,reg_date,first_reg_date,dob,order_engineer,first_order_engineer,university,sessions,main_activicty,disciplinary_measures,Formation,insurance,Personal_data_provided_by_the_member,suspended_from,suspended_at,province_of_birth,place_of_birth,sex,fiscal_code,vat_no,qualifying_title,year_of_qualifying,pec,email,cell_phone,website,serial_number,address,postal_code,province,location,phone,fax,link])
        self.count = self.count + 1
        print("Data saved in CSV: ",self.count)         
            

        mySql_insert_query = """INSERT INTO dataset_rc_allestimenti_veicoli (make,model,equipment,codice_allestimento,cavalli,cilindrata,potenza,posti,porte,serbatoio,bagagliaio,altezza,larghezza,lunghezza,passo,massa,cilindri,coppia,trazione,cambio,alimentazione,omologazione_euro,giri,pneumatici_anteriori,pneumatici_posteriori,velocita_max,accelerazione_Kmh_0_100,url) 
        VALUES (%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s) """

        val = (self.no_of_make,self.no_of_model,equipment,codice_allestimento,cavalli,cilindrata,potenza,posti,porte,serbatoio,bagagliaio,altezza,larghezza,lunghezza,passo,massa,cilindri,coppia,trazione,cambio,alimentazione,omologazione_euro,giri,pneumatici_anteriori,pneumatici_posteriori,velocita_max,accelerazione_Kmh_0_100,link)

        mycursor.execute(mySql_insert_query, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")   

    def close(self):
        self.driver.close()
if __name__ == '__main__':
    scraper = Cni()
    scraper.start()
    # scraper.target_url()
    scraper.sub_links()
    # try:
    #     os.remove("cni_links.csv")
    # except:
    #     None

    scraper.close()