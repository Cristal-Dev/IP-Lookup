#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module simple pour afficher les informations d'une adresse IP
Utilise l'API gratuite ip-api.com (100 requêtes/minute max)
"""

import requests
import json
import sys

class InfoIP:
    def __init__(self):
        self.api_url = "http://ip-api.com/json/"
    
    def obtenir_info(self, ip=None):
        """
        Récupère les informations d'une IP
        Si aucune IP n'est fournie, utilise l'IP publique actuelle
        """
        try:
            if ip:
                url = f"{self.api_url}{ip}?lang=fr"
            else:
                url = f"{self.api_url}?lang=fr"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                return data
            else:
                return {"erreur": f"Impossible d'obtenir les infos pour {ip or 'votre IP'}"}
                
        except requests.exceptions.RequestException as e:
            return {"erreur": f"Erreur de connexion: {e}"}
        except json.JSONDecodeError:
            return {"erreur": "Erreur lors du décodage de la réponse"}
    
    def afficher_info(self, ip=None):
        """Affiche les informations d'une IP de manière formatée"""
        print("🔍 Recherche des informations IP...\n")
        
        data = self.obtenir_info(ip)
        
        if "erreur" in data:
            print(f"❌ {data['erreur']}")
            return
        
        print("📍 INFORMATIONS IP")
        print("=" * 50)
        print(f"🌐 Adresse IP    : {data.get('query', 'N/A')}")
        print(f"🏠 FAI           : {data.get('isp', 'N/A')}")
        print(f"🏢 Organisation  : {data.get('org', 'N/A')}")
        print(f"🌍 Pays          : {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})")
        print(f"🏛️  Région        : {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')})")
        print(f"🏙️  Ville         : {data.get('city', 'N/A')}")
        print(f"📮 Code postal   : {data.get('zip', 'N/A')}")
        print(f"🕐 Fuseau horaire: {data.get('timezone', 'N/A')}")
        print(f"📍 Coordonnées   : {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
        
        # Affichage du type de connexion si disponible
        if data.get('mobile'):
            print("📱 Type          : Connexion mobile")
        elif data.get('proxy'):
            print("🔒 Type          : Proxy détecté")
        else:
            print("💻 Type          : Connexion fixe")

def main():
    """Fonction principale pour utilisation en ligne de commande"""
    info_ip = InfoIP()
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(f"Analyse de l'IP: {ip}")
        info_ip.afficher_info(ip)
    else:
        print("Analyse de votre IP publique:")
        info_ip.afficher_info()

# Exemple d'utilisation simple
if __name__ == "__main__":
    # Utilisation basique
    ip_analyzer = InfoIP()
    
    print("=== EXEMPLE 1: Votre IP publique ===")
    ip_analyzer.afficher_info()
    
    print("\n=== EXEMPLE 2: IP spécifique ===")
    ip_analyzer.afficher_info("8.8.8.8")
    
    print("\n=== EXEMPLE 3: Récupération des données brutes ===")
    data = ip_analyzer.obtenir_info("1.1.1.1")
    if "erreur" not in data:
        print(f"Pays: {data['country']}, Ville: {data['city']}")