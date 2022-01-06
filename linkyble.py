import bluepy.btle as btle  # Librairie bluetooth
import websockets
import asyncio  # Asynchrone Input/Ou
import threading
import time
msg=""

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

    async def socksend(self,websocket, path):  # Devient Asynchrone
        global msg
        while 1:

            await asyncio.sleep(1.5)
            msg2=msg
            print(msg2)
            print("message envoyé")
            await websocket.send(msg2)  # Attend la fin dun processus pour commencer

    def parsing(self, seg):
        global msg
        split = seg.splitlines()


        if len(split) >= 37 :
            for i, cle in enumerate(self.tab_cle):
                donne = split[i]
                taille = len(cle)
                if self.tab_rogne[i] != 0:
                    split[i] = donne[taille:self.tab_rogne[i]].strip().replace(" ", "").replace("\t", "").lstrip("0")
                else:
                    split[i] = donne[taille:].strip().replace(" ", "").replace("\t", "").lstrip("0")

            json = "{"

            for i, cle in enumerate(self.tab_cle):
                if split[i] != "":
                    json = json + '"' + self.tab_cle[i] + '"' + ":" + '"' + split[i] + '"' + ","

            json = json[:-1] + "}"
            self.json_to_send = json
            msg=json
            #print(self.json_to_send)

    def recup_data(self):
        self.flux = r.get_buffer()

        index = self.flux.find(chr(0x02))  # On attends le caractère de début de trame
        if (
                index != -1) and self.flag_debut_trame == 0:  # Si la méthode find à trouvé le caractère, alors on passe le flag à 0
            print("début trame detectée")
            self.flux = self.flux[index + 1:]  # On recupère les informations après le caractère de départ
            r.set_buffer(self.buffer)
            self.flag_debut_trame = 1  # Une fois le début de trame detecté, le flag passe à 1


        if self.flag_debut_trame == 1:  # Si un un début de tram à été détecté , avec un flag à 1
            index = self.flux.find(chr(0x03))  # On chercher le caractère de fin de trame
            if index != -1 and self.flag_debut_trame == 1:
                print("fin de trame detectée")

                flux2 = self.flux
                flux2 = flux2[index:]  # On garde

                if len(flux2) >= 1:
                    self.segment_to_parse = self.flux[:-1]


                else:
                    r.set_buffer(self.flux[:-1])

                self.flag_debut_trame = 0
                r.reset_buffer()
                self.parsing(self.segment_to_parse)


def multi():
    trait = Traitement()
    while True:  # Le processus est en multithread
        trait.recup_data()
        while p.waitForNotifications(0.1):  # Dès la reception de données
            pass


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


r = ReadDelegate()
t=Traitement()

start_server = websockets.serve(t.socksend, '127.0.0.1', 15555)  # Adresse IP et Port du WebSocket
print("Server started")  # Affiche un message quand le websocket à démarré

p = btle.Peripheral("FC:45:C3:BE:D6:5B")  # Adresse MAC du module BLE du Linky

s = p.getServiceByUUID("0000ffe0-0000-1000-8000-00805f9b34fb")  # UUID du module BLE
p.withDelegate(r)
c = s.getCharacteristics()[0]

Thread = threading.Thread(target=multi, args=())
Thread.start()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

p.disconnect()
