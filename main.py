import json
import influxdb
import datetime
import threading
import websockets
import json
import asyncio


#json_body = '{"ADSC":"61662803981","VTIC":"2","DATE":"H211203164631","NGTF":"BASE","LDARF":"BASE","EAST":"5703343","EASF01":"5703343","EASD01":"5703343","URMS1":"235","PREF":"9","PCOUP":"9","SINSTS":"54","SMAXSN":"H21120307424701903","SMAXSN-1":"H21120219061203242","CCASN":"H21120316000000116","CCASN-1":"H21120315000000131","UMOY1":"H211203163000235","STGE":"DA0001","MSG1":"PASDEMESSAGE","PRM":"5110709083089","NTARF":"1"}'
semaphore = 0

dic = []






class InfluxDB:
    def __init__(self):
        self.d = ''


    def connection(self):
        self.client = influxdb.InfluxDBClient(host="192.168.1.180", port="8086")
        self.client.switch_database('teleinfo')


    def ajout_donnee(self):
        global semaphore
        global dic
        while 1:
            if semaphore == 1 and dic:
                semaphore = 0


    def affichage(self):
        print(self.client.get_list_database())
        resultat = self.client.query('SELECT * from "consommation"')
        #print(resultat)

    def create(self):
        self.client.create_database('teleinfo')






class Client:
    async def websocket(self):
        global dic
        async with websockets.connect("ws://XXX.XXX.XXX.XXX//ws/") as websocket:
            while True:
                json_ok = await websocket.recv()
                await asyncio.sleep(2)
                jl = json.loads(json_ok)
                for key in jl:
                    print(jl, jl[key])

                await self.set_semaphore()




    async def set_semaphore(self):
        global semaphore
        semaphore = 1



    def start(self):
        asyncio.run(self.websocket())


    def get_time(self):
        return datetime.datetime.now().isoformat('T')
















def multi():
    cli = Client()
    cli.start()


Thread = threading.Thread(target=multi, args=())
Thread.start()







