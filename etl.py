import json
import requests
import unicodedata
import pandas as pd
import re
import logging
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message, MessageBase
from spade.template import Template



#SOME PRE-CONFIGURATION
##########################################################################################################################################################################
f = open('credentials.json',)
data = json.load(f)
AUTH_DATA = ("ab7ac04688174782a8269c5adc7bde6c", "Gnt7Tqgb4fUctqOMKXWjJg9YPGKKPP+PDgd6r/B0tdsjPEqbmp")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        datefmt='%d/%m/%y %H:%M:%S', level=logging.INFO)
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }

MAX_REQUESTS = "EXTRACT-ERROR: You have reached the maximum number of requests, probably your ip is temporarily blocked on this domain:"
###########################################################################################################################################################################

class ExtractAgent(Agent):
    def get_michaelpage(url):
        print('')
        logging.info("STARTING MICHAELPAGE EXTRACTION...")
        data_dic = {'sector': [], 'n_jobs': [], 'link': []}
        try:
            page = requests.get(url, headers=HEADERS)
            logging.info('Making request to: {}'.format(url))
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise SystemExit(e)

        try:
            html_soup = BeautifulSoup(page.content, 'html.parser')
            logging.info('Request completed, parsing html tree...')
            panel = html_soup.find('div', {'id': 'browse-sector'})
            logging.info('Extracting SECTORS...')

            for li in panel.find_all('li'):
                link = li.find('a')['href']
                sector = li.find('a').text

                try:
                    page_inner = requests.get(url+link, headers=HEADERS)
                    logging.info('Making request to: {}'.format(url+link))
                except requests.exceptions.RequestException as e:
                    logging.error(e)
                    raise SystemExit(e)

                html_soup_inner = BeautifulSoup(page_inner.content, 'html.parser')
                n_offers = html_soup_inner.find(
                    'span', {'class': 'total-search no-of-jobs'}).text
                logging.info('Extracting OFFERS...')
                sector = unicodedata.normalize("NFKD", sector).encode("ascii", "ignore").decode("ascii")
                data_dic['sector'].append(sector)
                data_dic['n_jobs'].append(int(n_offers))
                data_dic['link'].append('https://www.michaelpage.es')

        except AttributeError as error:
            logging.error(error)
        logging.info('Extracting at {} completed.'.format(url))
        return data_dic
    
    def get_infoempleo(url):
        print('')
        logging.info("STARTING INFOEMPLEO EXTRACTION...")
        data_dic = {'sector': [], 'n_jobs': [], 'link': []}
        try:
            page = requests.get(url, headers=HEADERS)
            logging.info('Making request to: {}'.format(url))
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise SystemExit(e)

        try:
            html_soup = BeautifulSoup(page.content, 'html.parser')
            logging.info('Request completed, parsing html tree...')
            panel = html_soup.find("ul", {"class": "image-pills mt60"})
            logging.info('Extracting SECTORS...')

            for li in panel.find_all('li'):
                sector = li.find('a').text.lower().replace('trabajo en', "").replace(
                    ',', "").lstrip().replace(' ', '-').replace('i+d', 'id')
                sector = unicodedata.normalize("NFKD", sector).encode(
                    "ascii", "ignore").decode("ascii")
                url_inner = (
                    'https://www.infoempleo.com/trabajo/area-de-empresa_'+sector)
                url_inner = url_inner.strip()

                try:
                    logging.info('Extracting OFFERS...')
                    page_inner = requests.get(url_inner, headers=HEADERS)
                    logging.info('Making request to: {}'.format(url_inner))
                except requests.exceptions.RequestException as e:  
                    logging.error(e)
                    raise SystemExit(e)

                html_soup_inner = BeautifulSoup(page_inner.content, 'html.parser')
                logging.info('Request completed, parsing html tree...')
                cadena = html_soup_inner.find(
                    'p', {'class': 'small width-read l12-hide'}).text
                cadena = re.findall(r'\d+', cadena)[0]
                n_offers = cadena
                sector = sector.replace('-', ' ').strip()
                sector = unicodedata.normalize("NFKD", sector).encode("ascii", "ignore").decode("ascii")
                data_dic['sector'].append(sector)
                data_dic['n_jobs'].append(int(n_offers))
                data_dic['link'].append('https://www.infoempleo.com')

        except AttributeError as error:
            logging.error(error)

        logging.info('Extracting at {} completed.'.format(url))
        return data_dic
    
    def get_indeed(url):
        print('')
        data_dic = {'sector': [], 'n_jobs': [], 'link': []}
        logging.info("STARTING INDEED EXTRACTION...")
        try:
            page = requests.get(url, headers=HEADERS)
            logging.info('Making request to: {}'.format(url))
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise SystemExit(e)

        try:
            html_soup = BeautifulSoup(page.content, 'html.parser')
            logging.info('Request completed, parsing html tree.')
            panel = html_soup.find(
                "ul", {"role": "presentation", "id": "categories"})
            logging.info('Extracting SECTORS...')

            for li in panel.find_all('li'):
                sector = li.find('a').text
                url_inner = 'https://es.indeed.com/'+'ofertas-de-'+sector

                try:
                    page_inner = requests.get(url_inner, headers=HEADERS)
                    logging.info('Making request to: {}'.format(url_inner))
                except requests.exceptions.RequestException as e:
                    raise SystemExit(e)

                html_soup_inner = BeautifulSoup(page_inner.content, 'html.parser')
                cadena = html_soup_inner.find(
                    'div', {'id': 'searchCountPages'}).text
                logging.info('Extracting OFFERS...')
                cadena = cadena.replace('Página 1 de', '').replace(
                    'empleos', '').lstrip().rstrip()
                n_offers = cadena.replace('.', '').lstrip().rstrip()
                sector = unicodedata.normalize("NFKD", sector).encode("ascii", "ignore").decode("ascii")
                data_dic['sector'].append(sector)
                data_dic['n_jobs'].append(int(n_offers))
                data_dic['link'].append('https://es.indeed.com')

        except Exception as error:
            logging.error(error)
            print(MAX_REQUESTS, url)

        logging.info('Extracting at {} completed.'.format(url))
        return data_dic

    def get_infojobs(url):
        print('')
        data_dic = {'sector': [], 'n_jobs': [], 'link': []}
        logging.info("STARTING INFO-JOBS EXTRACTION...")
        
        try:
            response = requests.get(url, auth=AUTH_DATA, headers=HEADERS)
            logging.info('Making request to: {}'.format(url))
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise SystemExit(e)
        
        categorias = json.loads(response.content)
        logging.info('Request completed, parsing API content...')
        logging.info('Extracting SECTORS...')
        for categoria in categorias:
            names = categoria['value']
            sector = categoria['value']
            if sector != '(Seleccionar)':
                names = names.lower()
                names =  unicodedata.normalize("NFKD", names).encode("ascii","ignore").decode("ascii")
                names = names.replace(',','').replace(' de ',' ').replace(' e ',' ').replace('i+d','id').replace('ventas al','venta').replace('clientes','cliente')
                sector = sector.lower().replace('y','').replace(',','').replace(' de ',' ').replace(' e ',' ').replace('i+d','id').replace('ventas al','venta').replace('clientes','cliente').replace(' ','-').replace('--','-')
                sector =  unicodedata.normalize("NFKD", sector).encode("ascii","ignore").decode("ascii")

                url_inner = 'https://api.infojobs.net/api/7/offer?category='+sector
                try:
                    response =  requests.get(url_inner, auth=AUTH_DATA)
                    
                    logging.info('Making request to: {}'.format(url))
                except requests.exceptions.RequestException as e:
                    logging.error(e)
                    raise SystemExit(e)
                n_offers = json.loads(response.content)

                logging.info('Extracting OFFERS...')
                n_offers = n_offers['totalResults']
                data_dic['sector'].append(names)
                data_dic['n_jobs'].append(int(n_offers))
                data_dic['link'].append('https://www.infojobs.net/')
                
        logging.info('Extracting at {} completed.'.format(url))
        return data_dic

    
    
    class SendExtract(OneShotBehaviour):
        async def run(self):
            michelpage_dic = ExtractAgent.get_michaelpage('https://www.michaelpage.es/')
            df_michaelpage = pd.DataFrame.from_dict(michelpage_dic)
            df_michaelpage = df_michaelpage.to_json()
            send1 = Message(to=data['spade_intro']['username'])
            send1.set_metadata("performative", "inform")     
            send1.body = df_michaelpage                       
            await self.send(send1)

            infoempleo_dic = ExtractAgent.get_infoempleo('https://www.infoempleo.com/trabajo-categorias/')
            df_infoempleo = pd.DataFrame.from_dict(infoempleo_dic)
            df_infoempleo = df_infoempleo.to_json()
            send2 = Message(to=data['spade_intro']['username'])
            send2.set_metadata("performative", "inform")     
            send2.body = df_infoempleo                       
            await self.send(send2)
            
            indeed_dic = ExtractAgent.get_indeed('https://es.indeed.com/browsejobs')
            df_indeed = pd.DataFrame.from_dict(indeed_dic)
            df_indeed = df_indeed.to_json()
            send3 = Message(to=data['spade_intro']['username'])
            send3.set_metadata("performative", "inform")     
            send3.body = df_indeed                        
            await self.send(send3)
            
            infojobs_dic = ExtractAgent.get_infojobs('https://api.infojobs.net/api/1/dictionary/category')
            df_infojobs = pd.DataFrame.from_dict(infojobs_dic)
            df_infojobs = df_infojobs.to_json()
            send4 = Message(to=data['spade_intro']['username'])
            send4.set_metadata("performative", "inform")     
            send4.body = df_infojobs                        
            await self.send(send4)
            
            await self.agent.stop()
            logging.info("EXTRACTOR AGENT FINISH")
            
            

    async def setup(self):
        logging.info("EXTRACTOR AGENT:"+str(self.jid)+ "READY")
        send_extract = self.SendExtract()
        self.add_behaviour(send_extract)

class TransformAgent(Agent):
    def load_pre(df):    
        try:
            client = MongoClient('localhost')
        except Exception:
            logging.error('Error in Db connection')      
        db = client['ETL-empleos']

        logging.info('Creating Collection...')       
        col = db['data_raw'] 

        logging.info('Inserting data...')   
        col.insert_many(df.to_dict('records'))  

        client.close()
        logging.info("DATA RAW INSERTED IN DB")
    def clean_data(df):
        logging.info('Cleaning data...')
        df['sector']= df['sector'].str.lower()
        
        occurrences = 0
        for sector in df['sector']:
            occurrences = df['link'].groupby(df['sector']).get_group(sector).count()
            if occurrences < 2:
                index_del = df[ df['sector'] == sector ].index
                logging.info('Deleting sectors with < 2 ocurrences in webs')
                df.drop(index_del , inplace=True)
            if len(sector) > 20:
                index_del = df[ df['sector'] == sector ].index
                logging.info('Deleting sectors with > 20 characters')
                df.drop(index_del , inplace=True)
                
        logging.info('Remaking df...')
        df = df.sort_values(by=['sector'])
        df= df.reset_index(drop=True)

        return df
    
    class ReciveExtract(OneShotBehaviour):
        async def run(self):
            rcv1 = await self.receive(timeout=100)
            rcv2 = await self.receive(timeout=100)
            rcv3 = await self.receive(timeout=100)
            rcv4 = await self.receive(timeout=100)
            

            rcv1_json = json.loads(rcv1.body)
            rcv2_json = json.loads(rcv2.body)
            rcv3_json = json.loads(rcv3.body)
            rcv4_json = json.loads(rcv4.body)
            

            df1 = pd.DataFrame.from_dict(rcv1_json)
            df2 = pd.DataFrame.from_dict(rcv2_json)
            df3 = pd.DataFrame.from_dict(rcv3_json)
            df4 = pd.DataFrame.from_dict(rcv4_json)
            
            df_pre = pd.concat([df1, df2, df3, df4], axis=0)
            df_pre = df_pre.reset_index(drop=True)
            TransformAgent.load_pre(df_pre)
            df_pre = TransformAgent.clean_data(df_pre)
            df_pre = df_pre.to_json()
            if rcv4:
                logging.info("TRANSFORMER: PREPROCCESED TABLE RECEIVED")
            else:
                logging.info("Did not received any message after 10 seconds")
            await self.agent.stop()
            table_to_transform = Message(to=data['mi_cuenta']['username'])
            table_to_transform.set_metadata("performative", "inform")     
            table_to_transform.body = df_pre                    
            await self.send(table_to_transform)
            await self.agent.stop()
            logging.info("TRANSFORMER AGENT FINISH")
            
    async def setup(self):
        logging.info("TRANSFORMER AGENT"+str(self.jid)+ "READY")
        recive_extract = self.ReciveExtract()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(recive_extract, template)
        
class LoadAgent(Agent):
    def load(df):
        try:
            client = MongoClient('localhost')
        except Exception:
            logging.error('Error in Db connection')      
        db = client['ETL-empleos']

        logging.info('Creating Collection...')       
        col = db['jobs_search'] 

        logging.info('Inserting data...')   
        col.insert_many(df.to_dict('records'))  

        client.close()
        logging.info("DATA PROCCESED INSERTED IN DB")

    class ReciveLoad(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=250)
            df_load = pd.read_json(msg.body)
            if msg:
                logging.info("LOADER: JOBS SEARCH FINISHED")
                print(df_load)
                LoadAgent.load(df_load)
                
                df_load.to_csv('jobs_search.csv' )
                await self.agent.stop()
                print("LOADER AGENT FINISH")
                
            else:
                print("Did not received any message after 250 seconds")
            await self.agent.stop()
            print("LOADER AGENT FINISH")
    
    async def setup(self):
        print("LOADER AGENT:"+str(self.jid)+ "READY")
        recive_load = self.ReciveLoad()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(recive_load, template)


def main():
    print("Creating agents ... ")
    transformagent = TransformAgent(data['spade_intro']['username'], 
                            data['spade_intro']['password'])
    future = transformagent.start()
    future.result()
    extractagent = ExtractAgent(data['spade_intro_2']['username'], 
                            data['spade_intro_2']['password'])
    extractagent.start()
    
    loadagent = LoadAgent(data['mi_cuenta']['username'], 
                            data['mi_cuenta']['password'])
    future2 = loadagent.start()
    future2.result()
    
    
    
    while loadagent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            extractagent.stop()
            transformagent.stop()
            loadagent.stop()
            
            break
    print("Agents finalizados")

if __name__ == "__main__":
    main()



