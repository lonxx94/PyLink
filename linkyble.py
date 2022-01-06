import bluepy.btle as btle  # Librairie bluetooth
import websockets
from websockets import WebSocketServerProtocol
import asyncio  # Asynchrone Input/Ou
import threading
import time
import logging

msg = ""
semaphore_ws = 0
logging.basicConfig(level=logging.INFO)

class Server:
    clients = set()
    logging.info(f'starting up ...')

    def __init__(self):
        logging.info(f'init happened ...')

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')
    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_client(self,client, message: str) -> None:
        global msg
        global semaphore_ws
        logging.info("sending...")
       
        try:            
            await client.send(msg)
        except:
            await self.unregister(client)

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
       
        while 1:
            await asyncio.sleep(0.5)
            await self.distribute()


    async def distribute(self) -> None:
        global msg
        global semaphore_ws
        while 1:
            await asyncio.sleep(0.1)
            msg2=msg
            if semaphore_ws == 1 :
                C = self.clients.copy()
               
                for client in C:
                    await self.send_to_client(client,msg)
                    logging.info(f'message envoyé à {client.remote_address[0]}')
               
                semaphore_ws = 0
                await asyncio.sleep(0.1)
           




class Traitement:
    def __init__(self):
        self.flag_debut_trame = 0
        self.buffer = ''
        self.json_to_send = ''
        self.tab_cle = ['ADSC', 'VTIC', 'DATE', 'NGTF', 'LDARF', 'EAST', 'EASF01', 'EASF02', 'EASF03', 'EASF04',
                        'EASF05',
                        'EASF06', 'EASF07', 'EASF08', 'EASF09', 'EASF10', 'EASD01', 'EASD02', 'EASD03', 'EASD04',
                        'IRMS1',
                        'URMS1', 'PREF', 'PCOUP', 'SINSTS', 'SMAXSN', 'SMAXSN-1', 'CCASN', 'CCASN-1', 'UMOY1', 'STGE',
                        'MSG1',
                        'PRM', 'RELAIS', 'NTARF', 'NJOURF', 'NJOURF+1']
        self.tab_rogne = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                          -1, -1, -1,
                          -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.flux = ''
        self.segment_to_parse = ''




    def parsing(self, seg):
        global msg
        global semaphore_ws

        split = seg.splitlines()
        # print(split)
        if len(split) >= 37:

            for i, cle in enumerate(self.tab_cle):
                donne = split[i]
                taille = len(cle)
                if self.tab_rogne[i] != 0:
                    split[i] = donne[taille:self.tab_rogne[i]].strip().lstrip("0").replace(" ", "")
                    # split[i]=split[i].replace(" ","")
                else:
                    split[i] = donne[taille:].strip().lstrip("0").replace(" ", "")
                    # split[i]=split[i].replace(" ","")

            json = "{"

            for i, cle in enumerate(self.tab_cle):
                if split[i] != '':
                    json = json + '"' + self.tab_cle[i] + '"' + ":" + '"' + split[i] + '"' + ","

            json = json[:-1] + "}"
            self.json_to_send = json.replace("\t", "")
            #print(self.json_to_send)
            msg = self.json_to_send
            semaphore_ws = 1

    def recup_data(self):
        self.flux = r.get_buffer()

        index = self.flux.find(chr(0x02))  # On attends le caractère de début de trame
        if (index != -1) and self.flag_debut_trame == 0:  # Si la méthode find à trouvé le caractère, alors on passe le flag à 0
            #print("début trame detectée")
            self.flux = self.flux[index + 2:]  # On recupère les informations après le caractère de départ
            r.set_buffer(self.flux)
            self.flag_debut_trame = 1  # Une fois le début de trame detecté, le flag passe à 1
        # else:
        # self.flux = ''  # Si l'on à rien, on vide le buffer

        if self.flag_debut_trame == 1:  # Si un un début de tram à été détecté , avec un flag à 1
            index = self.flux.find(chr(0x03))  # On chercher le caractère de fin de trame
            # print(self.flux)
            if index != -1 and self.flag_debut_trame == 1:
                #print("fin de trame detectée")

                flux2 = self.flux
                flux2 = flux2[index:]  # On garde

                if len(flux2) >= 1:
                    self.segment_to_parse = self.flux[:-1]
                    #print("J'affiche flux")

                else:
                    r.set_buffer(self.flux[:-1])
                    #print("on remet un bout")

                self.flag_debut_trame = 0
                r.reset_buffer()
                self.parsing(self.segment_to_parse)


def multi():
    trait = Traitement()
    while True:  # Le processus est en multithread
        trait.recup_data()
        try:          
            p.waitForNotifications(0.5)  # Dès la reception de données
        except:
           
            try_num=1
            success= False
            while (try_num and not success):
               
                try:
                    logging.info(f'trying to connect...wait')
                    p.connect("30:E2:83:8D:8C:4A")
                    logging.info(f'reconnected!...')
                    success= True
                except btle.BTLEException:
                    logging.info(f'retrying connection!...wait')
                    try_num+=1


class ReadDelegate(btle.DefaultDelegate):
    def __init__(self):
        self.buffer = ''

    def handleNotification(self, cHandle, data):  # Méthode appellée tout les paquets de 21 bits
        # data est le bytearray de 21 bytes que l'on reçoit du BT
        data_list = list(data)  # On transforme le bitearray en liste d'entiers  indexable et modifiable

        for i in range(len(data_list)):
            data_list[i] = data_list[i] & 0b01111111  # On utilise un ET logique pour supprimer le bit de parité

        data = bytearray(data_list)  # On convertit la liste en bytearray
        self.buffer = self.buffer + data.decode(
            "UTF-8")  # On concatène le message et le bitearray décodé en UTF-8

    def get_buffer(self):
        return self.buffer

    def reset_buffer(self):
        self.buffer = ''

    def set_buffer(self, value):
        self.buffer = value

s = Server()
r = ReadDelegate()
t = Traitement()

start_server = websockets.serve(s.ws_handler, '172.30.2.96', 15555)  # Adresse IP et Port du WebSocket
print("Server started")  # Affiche un message quand le websocket à démarré

p = btle.Peripheral()  # Adresse MAC du module BLE du Linky

try_num=1
success= False
while (try_num and not success):
   
    try:
        logging.info(f'trying to connect...')
        p.connect("30:E2:83:8D:8C:4A")
        logging.info(f'connected!...')
        success= True
    except btle.BTLEException:
        logging.info(f'retrying connection!...')
        try_num+=1


s = p.getServiceByUUID("0000ffe0-0000-1000-8000-00805f9b34fb")  # UUID du module BLE
p.withDelegate(r)
c = s.getCharacteristics()[0]

Thread = threading.Thread(target=multi, args=())
Thread.start()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

p.disconnect()
