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
    compare_link = []
    def start(self):
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')

        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36')
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        
    def read_from_csv(self):
        with open("main_links_for_cni.csv", 'r') as input_file:
            reader = csv.reader(input_file,delimiter=",")
            for ri in reader:
                riw = str(ri[0])
                self.compare_link.append(riw)

    def target_url(self,url):
        self.driver.get(url)
        time.sleep(5)
        self.pro_select()


    def result_scrap(self):
        html = self.driver.page_source
        resp = Selector(text=html)
        
        data = resp.xpath("//a[contains(text(),'Dettaglio')]/@href").getall()
        for dat in data:
            results = str(dat)
            results = f"https://www.cni.it{results}"
            if results in self.compare_link:
                    None
            else:
                with open("cni_links.csv",'a',newline='',encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([results])
                print(results)

                
    def next_page(self):
        while True:
            self.result_scrap()
            html = self.driver.page_source
            resp = Selector(text=html)
            next_btn_check = resp.xpath("//li[@class='next']").get()
            print(next_btn_check)
            if next_btn_check != None or next_btn_check != '' or next_btn_check != "":
                try:
                    button = self.driver.find_element_by_xpath("//a[contains(text(),'Successivo')]")
                    self.driver.execute_script("arguments[0].click();", button)
                except:
                    None
                time.sleep(5)
            else:
                break
            

    def pro_select(self):
        # try:
        self.driver.find_element_by_xpath("//option[contains(text(),'Seleziona')]").click()
        time.sleep(3)
        self.driver.find_element_by_xpath("//button[@id='ricercaAnagraficaCercaButton']").click()
        time.sleep(8)
        self.next_page()
        # except:
        #     self.pro_select()


    def scrap(self):
        with open("cni_links.csv", 'r',encoding='utf-8') as input_file:
            reader = csv.reader(input_file,delimiter=",")
            for i in reader:
                link = str(i[0])
                with open("main_links_for_cni.csv",'a',newline='',encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([link])
                    print("Link saved",link)
                try:
                    self.driver.get(link)
                except:
                    self.driver.close()
                    self.start()
                    self.driver.get(link)

                time.sleep(3)
                html = self.driver.page_source
                resp = Selector(text=html)
                
                title = resp.xpath("normalize-space(//td[contains(text(),'titolo:')]/following-sibling::td/text())").extract_first()
                
                surname = resp.xpath("normalize-space((//td[contains(text(),'cognome:')])[1]/following-sibling::td/text())").extract_first()

                f_name = resp.xpath("normalize-space((//td[contains(text(),'nome:')])[1]/following-sibling::td/text())").extract_first()
                sex =resp.xpath("normalize-space((//td[contains(text(),'sesso:')])[1]/following-sibling::td/text())").extract_first()
                dob = resp.xpath("normalize-space((//td[contains(text(),'il:')])[1]/following-sibling::td/text())").extract_first()

                province_of_birth = resp.xpath("normalize-space((//td[contains(text(),'nato a:')])[1]/following-sibling::td/text())").extract_first()
                fiscal_code = resp.xpath("normalize-space((//td[contains(text(),'codice fiscale:')])[1]/following-sibling::td/text())").extract_first()
                address = resp.xpath("normalize-space((//td[contains(text(),'residenza/domicilio professionale:')])[1]/following-sibling::td/text())").extract_first()
                order_engineer = resp.xpath("normalize-space((//td[contains(text(),'ordine ingegneri:')])[1]/following-sibling::td/text())").extract_first()
                first_order_engineer = resp.xpath("normalize-space((//td[contains(text(),'prima iscrizione Ordine di:')])[1]/following-sibling::td/text())").extract_first()
                reg_no = resp.xpath("normalize-space((//td[contains(text(),'numero iscrizione:')])[1]/following-sibling::td/text())").extract_first()

                reg_date = resp.xpath("normalize-space((//td[contains(text(),'in data:')])[1]/following-sibling::td/text())").extract_first()
                first_reg_date = resp.xpath("normalize-space((//td[contains(text(),'prima iscrizione Ordine di:')])[1]/parent::tr/following-sibling::tr[1]/td[last()]/text())").extract_first()

                
                qualifying_title = resp.xpath("normalize-space((//td[contains(text(),'settore')])[1]/following-sibling::td/text())").extract_first()    
                university = resp.xpath("normalize-space((//td[contains(text(),'università:')])[1]/following-sibling::td/text())").extract_first()    
                

                
                sessions =resp.xpath("normalize-space((//td[contains(text(),'sessione:')])[1]/following-sibling::td/text())").extract_first()
                year_of_qualifying = resp.xpath("normalize-space((//td[contains(text(),'esame di stato:')])[1]/following-sibling::td/text())").extract_first()
                
                pec = resp.xpath("normalize-space((//td[contains(text(),'PEC:')])[1]/following-sibling::td/text())").extract_first()
                main_activicty = resp.xpath("normalize-space((//td[contains(text(),'attività prevalente:')])[1]/following-sibling::td/text())").extract_first()
                disciplinary_measures = resp.xpath("normalize-space((//td[contains(text(),'Provvedimenti disciplinari:')])[1]/following-sibling::td/text())").extract_first()
                Formation = resp.xpath("normalize-space((//td[contains(text(),'Formazione:')])[1]/following-sibling::td/text())").extract_first()

                insurance = resp.xpath("normalize-space((//td[contains(text(),'assicurazione:')])[1]/following-sibling::td/text())").extract_first()

                try:
                    Personal_data_provided_by_the_member = resp.xpath("//td[contains(text(),'Dati personali forniti dall'iscritto:')]/following-sibling::td/text()").extract_first()
                except:
                    Personal_data_provided_by_the_member = ''
                suspended_from = resp.xpath("normalize-space((//td[contains(text(),'sospeso dal:')])[1]/following-sibling::td/text())").extract_first()
                suspended_at  = resp.xpath("normalize-space((//td[contains(text(),'sospeso al:')])[1]/following-sibling::td/text())").extract_first()
                
                place_of_birth = ''
                vat_no = ''
                email= ''
                cell_phone = ''
                website= ''
                serial_number= ''
                postal_code= ''
                province= ''
                location= ''
                phone= ''
                fax= ''

                print()
                print("title:",title)
                print("surname:",surname)
                print("f_name:",f_name)
                print("reg_no:",reg_no)
                print("reg_date:",reg_date)
                print("first_reg_date:",first_reg_date)
                print("dob:",dob)
                print("order_engineer:",order_engineer)
                print("first_order_engineer:",first_order_engineer)
                print("university:",university)
                print("sessions:",sessions)
                print("main_activicty:",main_activicty)
                print("disciplinary_measures:",disciplinary_measures)
                print("Formation:",Formation)
                print("insurance:",insurance)
                print("Personal_data_provided_by_the_member:",Personal_data_provided_by_the_member)
                print("suspended_from:",suspended_from)
                print("suspended_at:",suspended_at)
                print("province_of_birth:",province_of_birth)
                print("place_of_birth:",place_of_birth)
                print("sex:",sex)
                print("fiscal_code:",fiscal_code)
                print("vat_no:",vat_no)
                print("qualifying_title:",qualifying_title)
                print("year_of_qualifying:",year_of_qualifying)
                print("pec:",pec)
                print("email:",email)
                print("cell_phone:",cell_phone)
                print("website:",website)
                print("serial_number:",serial_number)
                print("address:",address)
                print("postal_code:",postal_code)
                print("province:",province)
                print("location:",location)
                print("phone:",phone)
                print("fax:",fax)
                print("url:",link)
                print()
                
            
                # with open("Dataset_sample.csv",'a',newline='',encoding='utf-8') as file:
                #     writer = csv.writer(file)
                #     if self.count == 0:
                #         writer.writerow(['title','surname','f_name','reg_no','reg_date','first_reg_date','dob','order_engineer','first_order_engineer','university','sessions','main_activicty','disciplinary_measures','Formation','insurance','Personal_data_provided_by_the_member','suspended_from','suspended_at','province_of_birth','place_of_birth','sex','fiscal_code','vat_no','qualifying_title','year_of_qualifying','pec','email','cell_phone','website','serial_number','address','postal_code','province','location','phone','fax','link'])
                #     writer.writerow([title,surname,f_name,reg_no,reg_date,first_reg_date,dob,order_engineer,first_order_engineer,university,sessions,main_activicty,disciplinary_measures,Formation,insurance,Personal_data_provided_by_the_member,suspended_from,suspended_at,province_of_birth,place_of_birth,sex,fiscal_code,vat_no,qualifying_title,year_of_qualifying,pec,email,cell_phone,website,serial_number,address,postal_code,province,location,phone,fax,link])
                self.count = self.count + 1
                print("Data saved in CSV: ",self.count)         
                    

                mySql_insert_query = """INSERT INTO Data (title,surname,f_name,reg_no,reg_date,first_reg_date,dob,order_engineer,first_order_engineer,university,sessions,main_activicty,disciplinary_measures,Formation,insurance,Personal_data_provided_by_the_member,suspended_from,suspended_at,province_of_birth,place_of_birth,sex,fiscal_code,vat_no,qualifying_title,year_of_qualifying,pec,email,cell_phone,website,serial_number,address,postal_code,province,location,phone,fax,url) 
                VALUES (%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s, %s, %s, %s ,%s, %s, %s,%s,%s) """

                val = (title,surname,f_name,reg_no,reg_date,first_reg_date,dob,order_engineer,first_order_engineer,university,sessions,main_activicty,disciplinary_measures,Formation,insurance,Personal_data_provided_by_the_member,suspended_from,suspended_at,province_of_birth,place_of_birth,sex,fiscal_code,vat_no,qualifying_title,year_of_qualifying,pec,email,cell_phone,website,serial_number,address,postal_code,province,location,phone,fax,link)

                mycursor.execute(mySql_insert_query, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")   

if __name__ == '__main__':
    url = "https://www.cni.it/albo-unico"
    scraper = Cni()
    scraper.read_from_csv()
    scraper.start()
    scraper.target_url(url)
    scraper.scrap()
    try:
        os.remove("cni_links.csv")
    except:
        None
