#!/usr/bin/env python3
"""
Module IP Lookup - Géolocalisation et informations sur les adresses IP
Auteur: Assistant
Version: 1.0
"""

import requests
import json
import socket
import ipaddress
from typing import Dict, Optional, Union
import time

class IPLookup:
    """
    Classe pour effectuer des lookups d'adresses IP
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_valid_ip(self, ip: str) -> bool:
        """
        Vérifie si une adresse IP est valide
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def is_private_ip(self, ip: str) -> bool:
        """
        Vérifie si une adresse IP est privée
        """
        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False
    
    def get_public_ip(self) -> Optional[str]:
        """
        Obtient l'adresse IP publique actuelle
        """
        try:
            response = self.session.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de l'IP publique: {e}")
            return None
    
    def reverse_dns(self, ip: str) -> Optional[str]:
        """
        Effectue une résolution DNS inverse
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except socket.herror:
            return None
    
    def lookup_ipapi(self, ip: str) -> Optional[Dict]:
        """
        Lookup via IP-API (gratuit, pas de clé requise)
        """
        try:
            url = f"http://ip-api.com/json/{ip}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'ip': data.get('query'),
                    'pays': data.get('country'),
                    'code_pays': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'ville': data.get('city'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'organisation': data.get('org'),
                    'as_number': data.get('as'),
                    'mobile': data.get('mobile'),
                    'proxy': data.get('proxy'),
                    'hosting': data.get('hosting')
                }
            return None
        except Exception as e:
            print(f"Erreur IP-API: {e}")
            return None
    
    def lookup_ipwhois(self, ip: str) -> Optional[Dict]:
        """
        Lookup via ipwhois.app (gratuit)
        """
        try:
            url = f"http://ipwhois.app/json/{ip}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data.get('success'):
                return {
                    'ip': data.get('ip'),
                    'pays': data.get('country'),
                    'code_pays': data.get('country_code'),
                    'region': data.get('region'),
                    'ville': data.get('city'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone_name'),
                    'isp': data.get('isp'),
                    'organisation': data.get('org'),
                    'as_number': data.get('asn')
                }
            return None
        except Exception as e:
            print(f"Erreur ipwhois: {e}")
            return None
    
    def lookup_comprehensive(self, ip: str) -> Dict:
        """
        Lookup complet avec plusieurs sources
        """
        if not self.is_valid_ip(ip):
            return {'erreur': 'Adresse IP invalide'}
        
        if self.is_private_ip(ip):
            return {'erreur': 'Adresse IP privée - pas de géolocalisation disponible'}
        
        result = {
            'ip': ip,
            'reverse_dns': self.reverse_dns(ip),
            'est_privee': self.is_private_ip(ip)
        }
        
        # Essaie IP-API en premier
        print(f"Recherche d'informations pour {ip}...")
        geo_data = self.lookup_ipapi(ip)
        
        # Si échec, essaie ipwhois
        if not geo_data:
            print("Tentative avec source alternative...")
            geo_data = self.lookup_ipwhois(ip)
        
        if geo_data:
            result.update(geo_data)
        else:
            result['erreur'] = 'Aucune information géographique trouvée'
        
        return result
    
    def lookup_multiple(self, ips: list) -> Dict:
        """
        Lookup de plusieurs IPs avec délai pour éviter le rate limiting
        """
        results = {}
        for i, ip in enumerate(ips):
            print(f"Traitement {i+1}/{len(ips)}: {ip}")
            results[ip] = self.lookup_comprehensive(ip)
            
            # Délai pour éviter le rate limiting
            if i < len(ips) - 1:
                time.sleep(1)
        
        return results
    
    def format_result(self, data: Dict) -> str:
        """
        Formate les résultats pour un affichage lisible
        """
        if 'erreur' in data:
            return f"❌ Erreur: {data['erreur']}"
        
        output = []
        output.append(f"🌐 IP: {data.get('ip', 'N/A')}")
        
        if data.get('reverse_dns'):
            output.append(f"🔗 DNS inversé: {data['reverse_dns']}")
        
        if data.get('pays'):
            output.append(f"🏳️  Pays: {data['pays']} ({data.get('code_pays', 'N/A')})")
        
        if data.get('region'):
            output.append(f"📍 Région: {data['region']}")
        
        if data.get('ville'):
            output.append(f"🏙️  Ville: {data['ville']}")
        
        if data.get('latitude') and data.get('longitude'):
            output.append(f"📌 Coordonnées: {data['latitude']}, {data['longitude']}")
        
        if data.get('timezone'):
            output.append(f"🕐 Fuseau horaire: {data['timezone']}")
        
        if data.get('isp'):
            output.append(f"🌐 Fournisseur: {data['isp']}")
        
        if data.get('organisation'):
            output.append(f"🏢 Organisation: {data['organisation']}")
        
        if data.get('as_number'):
            output.append(f"🔢 ASN: {data['as_number']}")
        
        # Indicateurs de sécurité
        indicators = []
        if data.get('mobile'):
            indicators.append("📱 Mobile")
        if data.get('proxy'):
            indicators.append("🔒 Proxy")
        if data.get('hosting'):
            indicators.append("🖥️  Hébergement")
        
        if indicators:
            output.append(f"⚠️  Indicateurs: {', '.join(indicators)}")
        
        return '\n'.join(output)


def main():
    """
    Fonction principale pour démonstration
    """
    lookup = IPLookup()
    
    print("=== Module IP Lookup - Démonstration ===\n")
    
    # Obtenir l'IP publique
    print("1. Récupération de votre IP publique:")
    public_ip = lookup.get_public_ip()
    if public_ip:
        print(f"Votre IP publique: {public_ip}\n")
    
    # Exemples d'IPs à tester
    test_ips = [
        "8.8.8.8",           # Google DNS
        "1.1.1.1",           # Cloudflare DNS
        "208.67.222.222",    # OpenDNS
    ]
    
    if public_ip:
        test_ips.append(public_ip)
    
    print("2. Test sur plusieurs adresses IP:")
    print("-" * 50)
    
    for ip in test_ips:
        print(f"\n🔍 Analyse de {ip}:")
        result = lookup.lookup_comprehensive(ip)
        print(lookup.format_result(result))
        print("-" * 50)
    
    print("\n3. Exemple d'utilisation programmatique:")
    print("```python")
    print("from ip_lookup import IPLookup")
    print("")
    print("lookup = IPLookup()")
    print("result = lookup.lookup_comprehensive('8.8.8.8')")
    print("print(lookup.format_result(result))")
    print("```")


if __name__ == "__main__":
    main()