# PyLink
Deux scripts python.

LinkyBLE :
- Se connecte au module BLE du Linky ( La librairie bluepy nécessite Linux pour fonctionner)
- Installer libglib2.0-dev pour que bluepy fonctionne
- Nécessite l'adresse MAC du module BLE pour s'y connecter.
- Effectue le parsing des données.
- Le compteur doit être impérativement en mode "STANDARD"


InfluxDB :
- Récupère les données du WebSocket
- Inscrit les données dans une BDD InfluxDB
- Nécessite la librairie InfluxDB


Un schéma de la carte éléctronique conçue sous KiCad sera bientôt disponible avec la liste des composants nécessaires. 
