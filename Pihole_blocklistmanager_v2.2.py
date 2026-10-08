import os
import sys
import subprocess
import urllib3
import re
import shutil
import time
import threading
import queue
import platform

# =========================================================================
# DEBUGGING & STABILITÄTS-ENGINE
# =========================================================================
DEBUG_MODE = True

if DEBUG_MODE:
    import faulthandler
    faulthandler.enable() # Zwingt Linux bei Segfaults den Traceback ins Terminal zu schreiben

def dprint(msg):
    """Forensisches Debugging direkt ins Terminal (umgeht jegliche GUI-Hänger)"""
    if DEBUG_MODE:
        t = time.strftime("%H:%M:%S")
        sys.stderr.write(f"[DEBUG] {t} - {msg}\n")
        sys.stderr.flush()

dprint("Skript v2.0 startet. Prüfe Abhängigkeiten...")

# =========================================================================
# AUTO-INSTALLER FÜR ABHÄNGIGKEITEN
# =========================================================================
def ensure_dependencies():
    required_packages = ['requests', 'paramiko', 'cryptography']
    missing = []
    for p in required_packages:
        try:
            __import__(p)
        except ImportError:
            missing.append(p)
    if missing:
        dprint(f"Installiere fehlende Pakete: {missing}")
        try:
            # Hinzugefügt: --break-system-packages für neuere Debian/Mint Versionen (PEP 668)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--break-system-packages"] + missing)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            dprint(f"Fehler bei Auto-Installation: {e}")
            sys.exit(1)

ensure_dependencies()

# --- Ab hier normale Imports ---
import json
import base64
import requests
import paramiko
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# SSL Warnungen für alte Server ignorieren
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# PAYLOAD BEREICH - HIER SCHREIBT DAS SCRIPT SEINE DATEN REIN
# ==============================================================================
__VERSION__ = "2.2"

### Diese 3 Variablen leeren damit der Tresor leer ist ###
__PAYLOAD_SALT__ = ""
__ENCRYPTED_PAYLOAD__ = ""
__PLAINTEXT_LINKS__ = "http://sysctl.org/cameleon/hosts\nhttps://adaway.org/hosts.txt\nhttps://big.oisd.nl\nhttps://bitbucket.org/ethanr/dns-blacklists/raw/8575c9f96e5b4a1308f2f12394abd86d0927a4a0/bad_lists/Mandiant_APT1_Report_Appendix_D.txt\nhttps://blocklist.site/app/dl/crypto\nhttps://blocklist.site/app/dl/tracking\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/fake.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/popupads.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/tif.medium.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/ultimate.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/dnsmasq/fake.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/dnsmasq/popupads.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/dnsmasq/tif.medium.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/domains/dga30.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/domains/nrd7.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/domains/tif.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/domains/ultimate.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/hosts/tif.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/hosts/ultimate-compressed.txt\nhttps://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/hosts/ultimate.txt\nhttps://dbl.oisd.nl/\nhttps://gist.githubusercontent.com/VirtuBox/f09968a2d27bc00ba58b3617c61dc54e/raw/56723b76a70e87a8e2344daa7637cec778a54fd7/microsoft-dns-block.txt\nhttps://gist.githubusercontent.com/adamloving/4401361/raw/e81212c3caecb54b87ced6392e0a0de2b6466287/temporary-email-address-domains\nhttps://gist.githubusercontent.com/anudeepND/adac7982307fec6ee23605e281a57f1a/raw/5b8582b906a9497624c3f3187a49ebc23a9cf2fb/Test.txt\nhttps://gist.githubusercontent.com/jamesonev/7e188c35fd5ca754c970e3a1caf045ef/raw/9ee7a249c2287c19cb7a31127fd4c82c56f6463f/disposableEmailDomains.txt\nhttps://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt\nhttps://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt\nhttps://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt\nhttps://hosts-file.net/ad_servers.txt\nhttps://hosts-file.net/emd.txt\nhttps://hosts-file.net/exp.txt\nhttps://hosts-file.net/grm.txt\nhttps://hosts-file.net/psh.txt\nhttps://hostsfile.org/Downloads/hosts.txt\nhttps://mirror.cedia.org.ec/malwaredomains/immortal_domains.txt\nhttps://mirror1.malwaredomains.com/files/justdomains\nhttps://nsfw.oisd.nl\nhttps://osint.digitalside.it/Threat-Intel/lists/latestdomains.txt\nhttps://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts;showintro=0\nhttps://phishing.army/download/phishing_army_blocklist.txt\nhttps://phishing.army/download/phishing_army_blocklist_extended.txt\nhttps://ransomwaretracker.abuse.ch/downloads/CW_C2_DOMBL.txt\nhttps://ransomwaretracker.abuse.ch/downloads/LY_C2_DOMBL.txt\nhttps://ransomwaretracker.abuse.ch/downloads/RW_DOMBL.txt\nhttps://ransomwaretracker.abuse.ch/downloads/TC_C2_DOMBL.txt\nhttps://ransomwaretracker.abuse.ch/downloads/TL_C2_DOMBL.txt\nhttps://raw.github.com/notracking/hosts-blocklists/master/hostnames.txt\nhttps://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/combined_disguised_trackers_justdomains.txt\nhttps://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_ads.txt\nhttps://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers.txt\nhttps://raw.githubusercontent.com/AmnestyTech/investigations/master/2021-07-18_nso/domains.txt\nhttps://raw.githubusercontent.com/ChefTyler/MiscHostsFiles/master/ChanBlocker.txt\nhttps://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt\nhttps://raw.githubusercontent.com/Dawsey21/Lists/master/main-blacklist.txt\nhttps://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts\nhttps://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts\nhttps://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts\nhttps://raw.githubusercontent.com/Monstanner/DuckDuckGo-Fakeshops-Blocklist/main/Blockliste\nhttps://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/AmazonFireTV.txt\nhttps://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV.txt\nhttps://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt\nhttps://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADomains.txt\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Corona-Blocklist\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DatingSites\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/AddikoBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/AnadiBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/BKSBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Bank99\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/BankBurgenland\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Bawag\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/ConsorsFinanz\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Denizbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Easybank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Eurambank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Hypotirol\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Kommunalkreditinvest\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/LichtensteinischeLandesbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/N26\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/OberBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/PrivatBankRaiffeisenlandesbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/RaiffeisenBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Raiffeisenzertifikate\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/RenaultBankdirekt\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/SWKBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/SantanderBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/SchelhammerCapitalBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Schoellerbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/SpardaBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/SparkasseBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/TFBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/Teambank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/UniCreditBankAustria\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankKaernten\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankNiederoesterreich\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankOberoesterreich\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankSalzburg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankSteiermark\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankTirol\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankVorarlberg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/VolksbankWien\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/AT/ZuercherKantonalbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/AargauischeKantonalbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/AlternativeBankSchweiz\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Arabbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/BCJ-BanqueCantonaleduJura\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/BCN-BanqueCantonaleNeuchateloise\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/BCVS-BanqueCantonaleduValais\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/BNP-Paribas\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/BankCler\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/CIC\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Ca-Indosuez\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Cash\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Citi\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Credit-Suisse-AG\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/DZ-Privatbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Gemeinschaftsbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/HalvetischeBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/HelvetischeBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Heritage\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/HypoVoralberg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Hypobank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/JSafraSarasin\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/LGTBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Mbaerbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Migrosbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Monyland\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/NeonSchwitzerlandAG\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/ObwaldnerKantonalbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/OneSwissBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/PKB\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/PPI-Schweiz\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/PostFinance\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Raiffeisen\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/SNB-SchweizerischeNationalbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/SaxoBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/SchwyzerKantonalbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Swissbanking\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/SyzGroup\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/UBS\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/VPBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/Vontobel\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/CH/ZKB\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/BadenWuertemberg1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/BadenWuertemberg2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/BadenWuerttemberg1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/BadenWuerttemberg2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Bayern1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Bayern2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Bayern3\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Berlin\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Brandenburg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Bremen\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Hamburg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Hessen1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Hessen2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/MecklenburgVorpommern\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/NRW1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/NRW2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/NRW3\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/NRW4\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Niedersachsen1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Niedersachsen2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/RheinlandPfalz\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Saarland\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Sachsen\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/SachsenAnhalt\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/SchleswigHolstein\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Sparkasse/Thueringen\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-0\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-1-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-1-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-3-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-3-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-4\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-5-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-5-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-6\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-7-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-7-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-8-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-8-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-9-Teil-1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-9-Teil-2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/Volks-und-Raiffeisenbank/VR-PLZ-9-Teil-3\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Comdirect\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Commerzbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Consorsbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/DKB\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Deka\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/DeutscheBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/HamburgCommercialBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/HelebaBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Hypovereinsbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/ING\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/KFWBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/LandesbankBadenWuerttemberg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/NRWBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/NorddeutscheLandesbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/PSD-Bank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Pfandbriefbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Postbank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/SantanderBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Sparda-Bank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/StaatsbankBadenWuerttemberg\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/Targobank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting/DE/sonstige_Banken/VolkswagenBank\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting3\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/DomainSquatting4\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Fake-Science\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/MS-Office-Telemetry\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Phishing-Angriffe\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Streaming\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/SupportingRussia\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/Win10Telemetry\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/child-protection\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/crypto\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/easylist\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/gambling\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/malware\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/notserious\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock1\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock2\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock3\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock4\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock5\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/pornblock6\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/proxies\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/samsung\nhttps://raw.githubusercontent.com/RPiList/specials/master/Blocklisten/spam.mails\nhttps://raw.githubusercontent.com/RPiList/specials/refs/heads/master/Blocklisten/Corona-Blocklist\nhttps://raw.githubusercontent.com/SoftCreatR/fakerando-domains/main/all.txt\nhttps://raw.githubusercontent.com/Spam404/lists/master/adblock-list.txt\nhttps://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/KADhosts/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/SpotifyAds/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/UncheckyAds/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.2o7Net/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.Risk/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.Spam/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/data/tyzbit/hosts\nhttps://raw.githubusercontent.com/StevenBlack/hosts/master/hosts\nhttps://raw.githubusercontent.com/SweetSophia/mifitxiaomipiholelist/master/mifitblocklist.txt\nhttps://raw.githubusercontent.com/Zelo72/rpi/master/pihole/blocklists/fake.txt\nhttps://raw.githubusercontent.com/Zelo72/rpi/master/pihole/blocklists/multi.txt\nhttps://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt\nhttps://raw.githubusercontent.com/anudeepND/blacklist/master/facebook.txt\nhttps://raw.githubusercontent.com/anudeepND/youtubeadsblacklist/master/domainlist.txt\nhttps://raw.githubusercontent.com/autinerd/anti-axelspringer-hosts/master/axelspringer-hosts\nhttps://raw.githubusercontent.com/blocklistproject/Lists/master/alt-version/ransomware-nl.txt\nhttps://raw.githubusercontent.com/blocklistproject/Lists/master/alt-version/smart-tv-nl.txt\nhttps://raw.githubusercontent.com/blocklistproject/Lists/master/alt-version/tiktok-nl.txt\nhttps://raw.githubusercontent.com/blocklistproject/Lists/master/alt-version/vaping-nl.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Amazon.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Baidu.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Google.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/HP.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/LG.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Samsung.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Synology.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Twitch.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Ubisoft.txt\nhttps://raw.githubusercontent.com/bloodhunterd/pi-hole-blocklists/master/Xiaomi.txt\nhttps://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt\nhttps://raw.githubusercontent.com/daisy1754/jp-disposable-emails/master/list.txt\nhttps://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf\nhttps://raw.githubusercontent.com/disposable/disposable/master/blacklist.txt\nhttps://raw.githubusercontent.com/disposable/disposable/master/greylist.txt\nhttps://raw.githubusercontent.com/disposable/static-disposable-lists/master/generator-email-hosts.txt\nhttps://raw.githubusercontent.com/disposable/static-disposable-lists/master/mail-data-hosts-net.txt\nhttps://raw.githubusercontent.com/elliotwutingfeng/Inversion-DNSBL-Blocklists/main/Google_hostnames_ABP.txt\nhttps://raw.githubusercontent.com/flotwig/disposable-email-addresses/master/domains.txt\nhttps://raw.githubusercontent.com/gieljnssns/Social-media-Blocklists/master/pihole-tiktok.txt\nhttps://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt\nhttps://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/multi.txt\nhttps://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/tif.txt\nhttps://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/share/facebook.txt\nhttps://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/share/microsoft.txt\nhttps://raw.githubusercontent.com/jmdugan/blocklists/master/corporations/facebook/all\nhttps://raw.githubusercontent.com/krombopulosM/TikTok-blocklist/master/tiktok%20blocklist.txt\nhttps://raw.githubusercontent.com/matomo-org/referrer-spam-blacklist/master/spammers.txt\nhttps://raw.githubusercontent.com/namePlayer/dhl-scamlist/main/dns-blocklists/pihole-blacklist\nhttps://raw.githubusercontent.com/nice42q/gold-de-fakeshops/refs/heads/main/blocklist-domains.txt\nhttps://raw.githubusercontent.com/notracking/hosts-blocklists/master/adblock/adblock.txt\nhttps://raw.githubusercontent.com/quidsup/notrack/master/malicious-sites.txt\nhttps://raw.githubusercontent.com/quidsup/notrack/master/trackers.txt\nhttps://raw.githubusercontent.com/stopforumspam/disposable_email_domains/master/blacklist.txt\nhttps://raw.githubusercontent.com/tsirolnik/spam-domains-list/master/spamdomains.txt\nhttps://raw.githubusercontent.com/uBlock-LLC/uBlock/master/assets/thirdparties/mirror1.malwaredomains.com/files/justdomains\nhttps://raw.githubusercontent.com/uBlock-LLC/uBlock/master/assets/thirdparties/pgl.yoyo.org/as/serverlist\nhttps://raw.githubusercontent.com/uBlock-LLC/uBlock/master/assets/thirdparties/publicsuffix.org/list/effective_tld_names.dat\nhttps://raw.githubusercontent.com/uBlock-LLC/uBlock/master/assets/thirdparties/www.malwaredomainlist.com/hostslist/hosts.txt\nhttps://raw.githubusercontent.com/wesbos/burner-email-providers/master/prune/alive.txt\nhttps://raw.githubusercontent.com/wesbos/burner-email-providers/master/prune/dead.txt\nhttps://raw.githubusercontent.com/wlqY8gkVb9w1Ck5MVD4lBre9nWJez8/W10TelemetryBlocklist/master/W10TelemetryBlocklist\nhttps://reddestdream.github.io/Projects/MinimalHosts/etc/MinimalHostsBlocker/minimalhosts\nhttps://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt\nhttps://s3.amazonaws.com/lists.disconnect.me/simple_malvertising.txt\nhttps://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt\nhttps://someonewhocares.org/hosts/zero/hosts\nhttps://urlhaus.abuse.ch/downloads/hostfile/\nhttps://v.firebog.net/hosts/AdguardDNS.txt\nhttps://v.firebog.net/hosts/Airelle-hrsk.txt\nhttps://v.firebog.net/hosts/Airelle-trc.txt\nhttps://v.firebog.net/hosts/Easylist.txt\nhttps://v.firebog.net/hosts/Easyprivacy.txt\nhttps://v.firebog.net/hosts/Prigent-Ads.txt\nhttps://v.firebog.net/hosts/Prigent-Malware.txt\nhttps://v.firebog.net/hosts/Prigent-Phishing.txt\nhttps://v.firebog.net/hosts/Shalla-mal.txt\nhttps://v.firebog.net/hosts/static/w3kbl.txt\nhttps://www.einmalzahlungzweihundert.de/bl-einmalzahlung.txt\nhttps://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt\nhttps://www.malwaredomainlist.com/hostslist/hosts.txt\nhttps://www.squidblacklist.org/downloads/dg-ads.acl\nhttps://www.squidblacklist.org/downloads/dg-malicious.acl\nhttps://zerodot1.gitlab.io/CoinBlockerLists/hosts\nhttps://zeustracker.abuse.ch/blocklist.php?download=domainblocklist"
# ==============================================================================

# Globale Zustände für Entkopplung
GLOBAL_PW = None
GLOBAL_SALT = None
GLOBAL_CONFIG = {"lang": "de", "theme": "dark"}

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|\[K|\x08|\r')

LANG = {
    "de": {
        "title": f"Pi-Hole Blocklist Manager v{__VERSION__}",
        "links_frame": "Quell-Links (Hier eintragen/bearbeiten)",
        "btn_import_links": "🔗 Quell-Links Import",
        "btn_import_blocklist": "🛡️ Blockliste Import",
        "btn_export_links": "💾 Links Export",
        "btn_help": "❓ Hilfe / Info",
        "btn_start": "▶ Speichern & Start",
        "sec_frame": "Sicherheit, Design & Sprache",
        "btn_clear": "🗑 Tresor leeren",
        "btn_pw": "🔑 Passwort ändern",
        "up_frame": "1. Upload Server (Webserver)",
        "pi_frame": "2. Pi-Hole Server (Update & Reboot)",
        "lbl_host": "Host/IP:",
        "lbl_user": "User:",
        "lbl_pass": "Passwort:",
        "lbl_path": "Zielpfad:",
        "lbl_cmd": "Befehl:",
        "btn_up_only": "☁ Nur Upload",
        "btn_pi_only": "🔄 Nur Update",
        "btn_both": "🚀 Upload & Update",
        "btn_term": "💻 SSH Terminal",
        "log_frame": "Protokoll (Log)",
        "stat_title": "📊 Live-Status",
        "welcome_log": "Bereit für Aufgaben. Konfiguration geladen.",
        "default_links": "# Trage hier deine Blocklisten-URLs ein (eine pro Zeile)...",
        "help_text": "HILFE & ANLEITUNG\n\n1. Quell-Links: Trage URLs links ein oder nutze '🔗 Quell-Links Import'.\n2. Eigene Blocklisten: Nutze '🛡️ Blockliste Import' für große Offline-Dateien (werden beim Start gemerged).\n3. Aktionen (Rechts): Du kannst nun gezielt nur Hochladen, nur Pi-Hole Updaten oder Beides ausführen.",
        "ask_local_title": "Lokale Liste gefunden",
        "ask_local_msg": "Es wurde eine bestehende '{0}' ({1:.2f} MB) lokal gefunden.\n\nSoll diese in den Merge-Prozess (Zusammenführung) einbezogen werden?\n(Klicke 'Nein' um frisch zu beginnen)",
        "ask_remote_title": "Remote Liste gefunden",
        "ask_remote_msg": "Lokal wurde keine Liste gefunden, aber auf dem Server existiert eine alte Blockliste:\n{0} ({1:.2f} MB)\n\nSoll diese heruntergeladen und in den Merge einbezogen werden?",
        "term_choice": "Welchen Server möchtest du per SSH öffnen?",
        "term_up": "☁ Upload Server",
        "term_pi": "🕳️ Pi-Hole Server"
    },
    "en": {
        "title": f"Pi-Hole Blocklist Manager v{__VERSION__}",
        "links_frame": "Source Links (Edit here)",
        "btn_import_links": "🔗 Import Links",
        "btn_import_blocklist": "🛡️ Import Blocklist",
        "btn_export_links": "💾 Export Links",
        "btn_help": "❓ Help / Info",
        "btn_start": "▶ Save & Start",
        "sec_frame": "Security, Theme & Language",
        "btn_clear": "🗑 Clear Vault",
        "btn_pw": "🔑 Change Password",
        "up_frame": "1. Upload Server",
        "pi_frame": "2. Pi-Hole Server",
        "lbl_host": "Host/IP:",
        "lbl_user": "User:",
        "lbl_pass": "Password:",
        "lbl_path": "Target Path:",
        "lbl_cmd": "Command:",
        "btn_up_only": "☁ Upload Only",
        "btn_pi_only": "🔄 Update Only",
        "btn_both": "🚀 Upload & Update",
        "btn_term": "💻 SSH Terminal",
        "log_frame": "Protocol (Log)",
        "stat_title": "📊 Live Status",
        "welcome_log": "Ready for tasks. Configuration loaded.",
        "default_links": "# Enter your blocklist URLs here (one per line)...",
        "help_text": "HELP & INSTRUCTIONS\n\n1. Source Links: Enter URLs on the left or use '🔗 Import Links'.\n2. Custom Blocklists: Use '🛡️ Import Blocklist' for large offline files (merged on start).\n3. Actions (Right): You can now selectively just Upload, just Update Pi-Hole, or do Both.",
        "ask_local_title": "Local list found",
        "ask_local_msg": "An existing local '{0}' ({1:.2f} MB) was found.\n\nShould this be included in the merge process?\n(Click 'No' to start fresh)",
        "ask_remote_title": "Remote list found",
        "ask_remote_msg": "No local list was found, but an old blocklist exists on the server:\n{0} ({1:.2f} MB)\n\nShould it be downloaded and included in the merge process?",
        "term_choice": "Which server do you want to connect to?",
        "term_up": "☁ Upload Server",
        "term_pi": "🕳️ Pi-Hole Server"
    }
}

def t(key):
    lang = GLOBAL_CONFIG.get("lang", "de")
    return LANG[lang].get(key, key)

def get_colors():
    theme = GLOBAL_CONFIG.get("theme", "dark")
    if theme == "dark":
        return {"bg_main": "#2b2b2b", "bg_panel": "#3c3f41", "bg_input": "#1e1e1e", "fg_text": "#ffffff", "fg_log": "#a9b7c6"}
    return {"bg_main": "#f0f0f0", "bg_panel": "#ffffff", "bg_input": "#ffffff", "fg_text": "#000000", "fg_log": "#333333"}

# =========================================================================
# GLOBAL KRYPTO (Stand-Alone)
# =========================================================================
def save_payload_to_script(pw, salt, config_dict, links_text):
    if not pw or not salt: return
    dprint("Sichere Payload in Script-Datei...")
    try:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(pw.encode()))
        f = Fernet(key)
        enc_config = f.encrypt(json.dumps(config_dict).encode()).decode()
        links_plaintext = json.dumps(links_text)
        
        script_path = os.path.abspath(sys.argv[0])
        with open(script_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(script_path, "w", encoding="utf-8") as file:
            for line in lines:
                if line.startswith('__ENCRYPTED_PAYLOAD__ ='):
                    file.write(f'__ENCRYPTED_PAYLOAD__ = "{enc_config}"\n')
                elif line.startswith('__PAYLOAD_SALT__ ='):
                    file.write(f'__PAYLOAD_SALT__ = "{salt.hex()}"\n')
                elif line.startswith('__PLAINTEXT_LINKS__ ='):
                    file.write(f'__PLAINTEXT_LINKS__ = {links_plaintext}\n')
                else:
                    file.write(line)
        dprint("Speichern erfolgreich.")
    except Exception as e:
        dprint(f"Fehler beim Speichern: {e}")

# =========================================================================
# HAUPTANWENDUNG (Sicher und entkoppelt)
# =========================================================================
class PiholeBlocklistManager:
    def __init__(self, parent_frame):
        dprint("Initialisiere Haupt-App-Klasse...")
        self.root = parent_frame
        self.main_window = parent_frame.winfo_toplevel()
        
        self.work_dir = "pihole_data"
        self.download_dir = os.path.join(self.work_dir, "downloads")
        self.output_file = "BlocklisteFertig.txt"
        self.custom_blocklist_file = os.path.join(self.work_dir, "custom_blocklist.txt")
        self.total_dl_size = 0
        
        self.log_queue = queue.Queue()
        
        self.build_main_gui()
        # Wichtig: Speichere beim Schließen des Fensters
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.process_log_queue()

    def process_log_queue(self):
        try:
            for _ in range(50):
                message, tag = self.log_queue.get_nowait()
                clean_msg = ANSI_ESCAPE.sub('', message)
                at_bottom = self.text_log.yview()[1] >= 0.95
                
                if tag: self.text_log.insert(tk.END, clean_msg + "\n", tag)
                else: self.text_log.insert(tk.END, clean_msg + "\n")
                
                if at_bottom: self.text_log.see(tk.END)
        except queue.Empty: pass
        finally: self.root.after(100, self.process_log_queue)

    def log(self, message, tag=None):
        self.log_queue.put((message, tag))

    def build_main_gui(self):
        c = get_colors()
        
        try:
            style = ttk.Style()
            if "clam" in style.theme_names(): style.theme_use('clam')
            style.configure("TProgressbar", thickness=15, background="#4CAF50", troughcolor=c["bg_input"], bordercolor=c["bg_main"])
        except Exception as e:
            dprint(f"Theme-Warnung (Ignoriert): {e}")

        # --- LINKS ---
        left = tk.Frame(self.root, bg=c["bg_main"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        links_lf = tk.LabelFrame(left, text=t("links_frame"), padx=10, pady=10, bg=c["bg_main"], fg=c["fg_text"])
        links_lf.pack(fill=tk.BOTH, expand=True)

        txt_links_frame = tk.Frame(links_lf, bg=c["bg_main"])
        txt_links_frame.pack(fill=tk.BOTH, expand=True)
        # Font-Fix gegen Wayland-Segfault beim Metric-Lookup nach Resize
        self.text_links = tk.Text(txt_links_frame, wrap=tk.WORD, width=50, relief=tk.FLAT, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"], font=("Arial", 10))
        scroll_links = ttk.Scrollbar(txt_links_frame, orient="vertical", command=self.text_links.yview)
        self.text_links.configure(yscrollcommand=scroll_links.set)
        scroll_links.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_links.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        btn_grid = tk.Frame(links_lf, bg=c["bg_main"])
        btn_grid.pack(fill=tk.X, pady=(10, 0))
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        btn_grid.columnconfigure(2, weight=1)
        
        tk.Button(btn_grid, text=t("btn_import_links"), bg="#FF9800", fg="white", font=("Arial", 10, "bold"), command=self.import_links, relief=tk.FLAT).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        tk.Button(btn_grid, text=t("btn_import_blocklist"), bg="#E64A19", fg="white", font=("Arial", 10, "bold"), command=self.import_custom_blocklist, relief=tk.FLAT).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        tk.Button(btn_grid, text=t("btn_export_links"), bg="#607D8B", fg="white", font=("Arial", 10, "bold"), command=self.export_links, relief=tk.FLAT).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        
        tk.Button(btn_grid, text=t("btn_help"), bg="#00BCD4", fg="white", font=("Arial", 10, "bold"), command=self.show_help, relief=tk.FLAT).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        tk.Button(btn_grid, text=t("btn_start"), bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.start_processing, relief=tk.FLAT).grid(row=1, column=1, columnspan=2, sticky="ew", padx=2, pady=2)

        sec_frame = tk.LabelFrame(left, text=t("sec_frame"), padx=10, pady=10, bg=c["bg_main"], fg=c["fg_text"])
        sec_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(sec_frame, text=t("btn_clear"), bg="#f44336", fg="white", font=("Arial", 9, "bold"), command=self.prompt_clear_payload, relief=tk.FLAT).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        tk.Button(sec_frame, text=t("btn_pw"), bg="#607D8B", fg="white", font=("Arial", 9, "bold"), command=self.prompt_change_password, relief=tk.FLAT).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        tk.Button(sec_frame, text="🌗 Theme", bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), command=self.toggle_theme, relief=tk.FLAT).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        tk.Button(sec_frame, text="🌍 DE/EN", bg="#00BCD4", fg="white", font=("Arial", 9, "bold"), command=self.toggle_lang, relief=tk.FLAT).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        sec_frame.columnconfigure(0, weight=1); sec_frame.columnconfigure(1, weight=1)

        # --- RECHTS ---
        right = tk.Frame(self.root, bg=c["bg_main"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ssh_cont = tk.Frame(right, bg=c["bg_main"])
        ssh_cont.pack(fill=tk.X, pady=(0, 10))
        
        # 1. Upload
        up_lf = tk.LabelFrame(ssh_cont, text=t("up_frame"), padx=10, pady=5, bg=c["bg_main"], fg=c["fg_text"])
        up_lf.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        self.entry_up_host = self.add_field(up_lf, t("lbl_host"), 0, 0)
        self.entry_up_user = self.add_field(up_lf, t("lbl_user"), 0, 2)
        self.entry_up_pass = self.add_field(up_lf, t("lbl_pass"), 1, 0, secret=True)
        self.entry_up_path = self.add_field(up_lf, t("lbl_path"), 1, 2)
        
        up_lf.columnconfigure(1, weight=1)
        up_lf.columnconfigure(3, weight=1)

        # 2. PiHole
        pi_lf = tk.LabelFrame(ssh_cont, text=t("pi_frame"), padx=10, pady=5, bg=c["bg_main"], fg=c["fg_text"])
        pi_lf.pack(side=tk.TOP, fill=tk.X)
        self.entry_pi_host = self.add_field(pi_lf, t("lbl_host"), 0, 0)
        self.entry_pi_user = self.add_field(pi_lf, t("lbl_user"), 0, 2)
        self.entry_pi_pass = self.add_field(pi_lf, t("lbl_pass"), 1, 0, secret=True)
        self.entry_pi_cmd = self.add_field(pi_lf, t("lbl_cmd"), 1, 2)
        
        pi_lf.columnconfigure(1, weight=1)
        pi_lf.columnconfigure(3, weight=1)

        # 3. Aktionen
        act_frame = tk.Frame(ssh_cont, bg=c["bg_main"])
        act_frame.pack(fill=tk.X, pady=(10, 0))
        act_frame.columnconfigure(0, weight=1); act_frame.columnconfigure(1, weight=1); act_frame.columnconfigure(2, weight=1)
        
        tk.Button(act_frame, text=t("btn_up_only"), bg="#FF5722", fg="white", font=("Arial", 10, "bold"), command=lambda: self.trigger_ssh(True, False), relief=tk.FLAT).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(act_frame, text=t("btn_pi_only"), bg="#009688", fg="white", font=("Arial", 10, "bold"), command=lambda: self.trigger_ssh(False, True), relief=tk.FLAT).grid(row=0, column=1, sticky="ew", padx=2)
        tk.Button(act_frame, text=t("btn_both"), bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=lambda: self.trigger_ssh(True, True), relief=tk.FLAT).grid(row=0, column=2, sticky="ew", padx=2)
        
        tk.Button(ssh_cont, text=t("btn_term"), bg="#37474F", fg="white", font=("Arial", 10, "bold"), command=self.open_ssh_terminal, relief=tk.FLAT).pack(fill=tk.X, pady=(5, 0))

        # Status & Log
        stat_lf = tk.LabelFrame(right, text=t("stat_title"), padx=10, pady=5, bg=c["bg_main"], fg=c["fg_text"])
        stat_lf.pack(fill=tk.X, pady=(0, 10))
        self.lbl_stat_dl = tk.Label(stat_lf, text="Download-Größe: 0 MB", font=("Arial", 9), bg=c["bg_main"], fg=c["fg_text"])
        self.lbl_stat_dl.pack(anchor="w")
        self.lbl_stat_ram = tk.Label(stat_lf, text="RAM: 0 MB", font=("Arial", 9), bg=c["bg_main"], fg=c["fg_text"])
        self.lbl_stat_ram.pack(anchor="w")
        self.lbl_stat_old = tk.Label(stat_lf, text="Alte Liste: Unbekannt", font=("Arial", 9), bg=c["bg_main"], fg=c["fg_text"])
        self.lbl_stat_old.pack(anchor="w")

        log_lf = tk.LabelFrame(right, text=t("log_frame"), padx=10, pady=5, bg=c["bg_main"], fg=c["fg_text"])
        log_lf.pack(fill=tk.BOTH, expand=True)
        tk.Button(log_lf, text="💾 Export", bg="#8D6E63", fg="white", font=("Arial", 8, "bold"), command=self.export_log, relief=tk.FLAT).pack(anchor="e", pady=(0, 5))
        
        log_txt_frame = tk.Frame(log_lf, bg=c["bg_main"])
        log_txt_frame.pack(fill=tk.BOTH, expand=True)
        # Font-Fix auch hier gegen Wayland-Segfault
        self.text_log = tk.Text(log_txt_frame, wrap=tk.WORD, relief=tk.FLAT, bg=c["bg_panel"], fg=c["fg_log"], insertbackground=c["fg_text"], font=("Arial", 10))
        log_scroll = ttk.Scrollbar(log_txt_frame, orient="vertical", command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_log.bind("<Key>", lambda e: "break")
        
        self.progress_bar = ttk.Progressbar(right, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Tags für Farben
        dark = GLOBAL_CONFIG.get("theme", "dark") == "dark"
        self.text_log.tag_config("error", foreground="#f44336" if dark else "#d32f2f")
        self.text_log.tag_config("success", foreground="#4CAF50" if dark else "#2E7D32")
        self.text_log.tag_config("warning", foreground="#FFEB3B" if dark else "#F57F17")
        self.text_log.tag_config("pihole", foreground="#E040FB" if dark else "#7B1FA2")
        self.text_log.tag_config("info", foreground="#03A9F4" if dark else "#0277BD")

        # INIT DATA
        self.load_config_to_gui()
        if __PLAINTEXT_LINKS__:
            self.text_links.insert(tk.END, __PLAINTEXT_LINKS__)
        else:
            self.text_links.insert(tk.END, t("default_links"))
        self.log(t("welcome_log"), "info")

    def add_field(self, parent, label, r, c_idx, secret=False):
        c = get_colors()
        tk.Label(parent, text=label, bg=c["bg_main"], fg=c["fg_text"]).grid(row=r, column=c_idx, sticky="w")
        ent = tk.Entry(parent, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"], relief=tk.SOLID, borderwidth=1, show="*" if secret else "")
        ent.grid(row=r, column=c_idx+1, padx=5, pady=2, sticky="ew")
        return ent

    def sync_memory(self):
        GLOBAL_CONFIG["up_host"] = self.entry_up_host.get()
        GLOBAL_CONFIG["up_user"] = self.entry_up_user.get()
        GLOBAL_CONFIG["up_pass"] = self.entry_up_pass.get()
        GLOBAL_CONFIG["up_path"] = self.entry_up_path.get()
        GLOBAL_CONFIG["pi_host"] = self.entry_pi_host.get()
        GLOBAL_CONFIG["pi_user"] = self.entry_pi_user.get()
        GLOBAL_CONFIG["pi_pass"] = self.entry_pi_pass.get()
        GLOBAL_CONFIG["pi_cmd"] = self.entry_pi_cmd.get()

    def on_closing(self):
        self.sync_memory()
        save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, self.text_links.get("1.0", tk.END).strip())
        self.main_window.destroy()
        sys.exit(0)

    def toggle_theme(self):
        self.sync_memory()
        GLOBAL_CONFIG["theme"] = "light" if GLOBAL_CONFIG.get("theme", "dark") == "dark" else "dark"
        save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, self.text_links.get("1.0", tk.END).strip())
        messagebox.showinfo("Neustart", "Bitte starte das Programm neu, um das Theme zu übernehmen.")
        self.main_window.destroy()
        sys.exit(0)
        
    def toggle_lang(self):
        self.sync_memory()
        GLOBAL_CONFIG["lang"] = "en" if GLOBAL_CONFIG.get("lang", "de") == "de" else "de"
        save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, self.text_links.get("1.0", tk.END).strip())
        messagebox.showinfo("Restart", "Please restart for language changes.")
        self.main_window.destroy()
        sys.exit(0)

    def load_config_to_gui(self):
        def se(widget, val):
            if val: widget.delete(0, tk.END); widget.insert(0, val)
        se(self.entry_up_host, GLOBAL_CONFIG.get("up_host", ""))
        se(self.entry_up_user, GLOBAL_CONFIG.get("up_user", "root"))
        se(self.entry_up_pass, GLOBAL_CONFIG.get("up_pass", ""))
        se(self.entry_up_path, GLOBAL_CONFIG.get("up_path", "/var/www/html/blocklist/BlocklisteFertig.txt"))
        se(self.entry_pi_host, GLOBAL_CONFIG.get("pi_host", ""))
        se(self.entry_pi_user, GLOBAL_CONFIG.get("pi_user", "root"))
        se(self.entry_pi_pass, GLOBAL_CONFIG.get("pi_pass", ""))
        se(self.entry_pi_cmd, GLOBAL_CONFIG.get("pi_cmd", "pihole -g; reboot"))

    def import_links(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if f: 
            with open(f, "r", encoding='utf-8', errors='ignore') as file: 
                self.text_links.insert(tk.END, "\n" + file.read())

    def import_custom_blocklist(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if f: 
            os.makedirs(self.work_dir, exist_ok=True)
            with open(f, 'r', encoding='utf-8', errors='ignore') as f_in:
                c = f_in.read()
            with open(self.custom_blocklist_file, 'a', encoding='utf-8', errors='ignore') as f_out:
                f_out.write("\n" + c)
            self.log(f"🛡️ Lokale Blockliste ({os.path.basename(f)}) zwischengespeichert!", "success")

    def export_links(self):
        urls = self.extract_urls()
        if not urls:
            messagebox.showwarning("Keine Links", "Keine gültigen Links zum Exportieren gefunden.")
            return
            
        f = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialfile="Pihole_Quell_Links.txt", 
            filetypes=[("Text", "*.txt")]
        )
        if f:
            with open(f, 'w', encoding='utf-8') as fl:
                fl.write("\n".join(urls))
            messagebox.showinfo("Export erfolgreich", f"{len(urls)} Quell-Links wurden erfolgreich exportiert.")

    def show_help(self): messagebox.showinfo("Hilfe", t("help_text"))

    def prompt_clear_payload(self):
        if messagebox.askyesno("Reset", "Alles löschen?"):
            global GLOBAL_CONFIG
            GLOBAL_CONFIG = {"lang": "de", "theme": "dark"}
            save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, "")
            if os.path.exists(self.custom_blocklist_file):
                try: os.remove(self.custom_blocklist_file)
                except: pass
            self.main_window.destroy()
            sys.exit(0)

    def prompt_change_password(self):
        c = get_colors()
        self.pw_dialog = tk.Toplevel(self.root)
        self.pw_dialog.title("Passwort ändern")
        self.pw_dialog.geometry("350x250")
        self.pw_dialog.configure(bg=c["bg_main"])
        self.pw_dialog.grab_set()
        tk.Label(self.pw_dialog, text="Neues Master-Passwort:", bg=c["bg_main"], fg=c["fg_text"]).pack(pady=(15, 5))
        p1 = tk.Entry(self.pw_dialog, show="*", width=25, bg=c["bg_input"], fg=c["fg_text"], relief=tk.FLAT)
        p1.pack(); p1.focus()
        tk.Label(self.pw_dialog, text="Wiederholen:", bg=c["bg_main"], fg=c["fg_text"]).pack(pady=(10, 5))
        p2 = tk.Entry(self.pw_dialog, show="*", width=25, bg=c["bg_input"], fg=c["fg_text"], relief=tk.FLAT)
        p2.pack()
        def save_pw():
            global GLOBAL_PW, GLOBAL_SALT
            if p1.get() != p2.get() or not p1.get():
                messagebox.showerror("Fehler", "Ungleich!", parent=self.pw_dialog)
                return
            GLOBAL_PW = p1.get()
            GLOBAL_SALT = os.urandom(16)
            self.sync_memory()
            save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, self.text_links.get("1.0", tk.END).strip())
            self.pw_dialog.destroy()
            messagebox.showinfo("OK", "Passwort geändert!")
        tk.Button(self.pw_dialog, text="Speichern", bg="#FF9800", fg="white", command=save_pw, relief=tk.FLAT).pack(pady=15)

    def export_log(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Log.txt", filetypes=[("Text", "*.txt")])
        if f:
            with open(f, 'w', encoding='utf-8') as fl: fl.write(self.text_log.get("1.0", tk.END))
            messagebox.showinfo("OK", "Exportiert.")

    def update_status(self, dl_size=None, old_list_status=None):
        if dl_size is not None:
            self.total_dl_size += dl_size
            mb = self.total_dl_size / (1024 * 1024)
            
            txt_dl = f"Download-Größe: {mb:.2f} MB" if GLOBAL_CONFIG.get("lang", "de") == "de" else f"Download Size: {mb:.2f} MB"
            self.lbl_stat_dl.config(text=txt_dl)
            
            est_ram = mb * 3.5
            txt_ram = f"Geschätzter RAM-Bedarf: ~ {est_ram:.1f} MB" if GLOBAL_CONFIG.get("lang", "de") == "de" else f"Estimated RAM usage: ~ {est_ram:.1f} MB"
            self.lbl_stat_ram.config(text=txt_ram)
            
        if old_list_status is not None:
            txt_old = f"Alte Blockliste: {old_list_status}" if GLOBAL_CONFIG.get("lang", "de") == "de" else f"Old Blocklist: {old_list_status}"
            self.lbl_stat_old.config(text=txt_old)

    def ask_yes_no_threadsafe(self, title, message):
        result = [None]
        event = threading.Event()
        def ask():
            result[0] = messagebox.askyesno(title, message, parent=self.root)
            event.set()
        self.root.after(0, ask)
        event.wait()
        return result[0]

    # =========================================================================
    # CORE: PRE-FLIGHT CHECK, DOWNLOAD & SORT
    # =========================================================================
    def extract_urls(self):
        raw_lines = self.text_links.get("1.0", tk.END).splitlines()
        urls = set()
        for line in raw_lines:
            line = line.strip()
            if not line or line.startswith("#"): 
                continue
            if "[i] Target:" in line: 
                urls.add(line.replace("[i] Target: ", "").strip())
            elif line.startswith("http"): 
                urls.add(line)
        return sorted(list(urls))

    def start_processing(self):
        self.sync_memory()
        
        urls = self.extract_urls()
        
        if not urls:
            messagebox.showwarning("Keine Links", "Keine gültigen Links gefunden.")
            return
            
        self.text_links.delete("1.0", tk.END)
        self.text_links.insert(tk.END, "\n".join(urls))
        save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, "\n".join(urls))
        
        self.total_dl_size = 0
        if os.path.exists(self.custom_blocklist_file):
            self.total_dl_size += os.path.getsize(self.custom_blocklist_file)
            
        self.update_status(dl_size=0, old_list_status="Prüfe...")
        self.log(f"\n--- STARTE VERARBEITUNG ({len(urls)} URLs) ---", "info")
        
        threading.Thread(target=self.process_workflow, args=(urls,), daemon=True).start()

    def process_workflow(self, urls):
        self.root.after(0, lambda: self.progress_bar.config(maximum=len(urls), value=0))
        
        self.log("Suche nach bereits existierenden Blocklisten...", "info")
        
        if os.path.exists(self.output_file):
            sz_bytes = os.path.getsize(self.output_file)
            sz_mb = sz_bytes / (1024 * 1024)
            use_local = self.ask_yes_no_threadsafe(
                t("ask_local_title"), 
                t("ask_local_msg").format(self.output_file, sz_mb)
            )
            if not use_local:
                try: os.remove(self.output_file)
                except: pass
                self.log("Lokale Liste gelöscht. Starte frisch.", "warning")
            else:
                self.log("Lokale Liste wird in den Merge einbezogen.", "success")
                self.root.after(0, self.update_status, sz_bytes, f"Lokal (Integriert, {sz_mb:.2f} MB)")
        else:
            up_host = GLOBAL_CONFIG.get("up_host", "")
            up_user = GLOBAL_CONFIG.get("up_user", "")
            up_pass = GLOBAL_CONFIG.get("up_pass", "")
            up_path = GLOBAL_CONFIG.get("up_path", "")

            if up_host and up_user and up_path:
                self.log(f"Prüfe Server {up_host} auf alte Liste...", "info")
                try:
                    ssh_up = paramiko.SSHClient()
                    ssh_up.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_up.connect(up_host, username=up_user, password=up_pass, timeout=5)
                    sftp = ssh_up.open_sftp()
                    
                    remote_exists = False
                    remote_size_mb = 0.0
                    try:
                        r_stat = sftp.stat(up_path)
                        remote_exists = True
                        remote_size_mb = r_stat.st_size / (1024 * 1024)
                    except IOError:
                        pass

                    if remote_exists:
                        use_remote = self.ask_yes_no_threadsafe(
                            t("ask_remote_title"),
                            t("ask_remote_msg").format(up_path, remote_size_mb)
                        )
                        if use_remote:
                            self.log("Lade alte Liste vom Server herunter...", "info")
                            sftp.get(up_path, self.output_file)
                            self.log("✅ Alte Liste erfolgreich vom Server geladen!", "success")
                            
                            sz_bytes = os.path.getsize(self.output_file)
                            sz_mb = sz_bytes / (1024 * 1024)
                            self.root.after(0, self.update_status, sz_bytes, f"Remote geladen ({sz_mb:.2f} MB)")
                        else:
                            self.log("Remote Liste wird ignoriert.", "warning")
                            self.root.after(0, self.update_status, None, "Ignoriert")
                    else:
                        self.log("Keine alte Liste auf dem Server gefunden.", "info")
                        self.root.after(0, self.update_status, None, "Keine gefunden")

                    sftp.close()
                    ssh_up.close()
                except Exception as e:
                    self.log(f"Konnte nicht auf Remote-Liste prüfen: {e}", "warning")
                    self.root.after(0, self.update_status, None, "Prüfung fehlgeschlagen")
            else:
                self.root.after(0, self.update_status, None, "Keine")

        # --- STARTE DOWNLOADS ---
        os.makedirs(self.download_dir, exist_ok=True)
        for i, url in enumerate(urls, 1):
            self.log(f"Lade ({i}/{len(urls)}): {url}")
            try:
                r = requests.get(url, timeout=15, verify=False)
                r.raise_for_status()
                
                self.root.after(0, self.update_status, len(r.content))
                
                if 'text/html' in r.headers.get('Content-Type', ''):
                    self.log(f"   -> ⚠️ WARNUNG: HTML statt Text empfangen!", "warning")
                with open(os.path.join(self.download_dir, f"h_{i}.txt"), 'w', encoding='utf-8') as f:
                    f.write(r.text)
            except Exception as e:
                self.log(f"   -> ❌ FEHLER: {e}", "error")
            self.root.after(0, lambda v=i: self.progress_bar.config(value=v))
            
        self.log("\nMerge & Bereinigung läuft...", "info")
        self.merge_and_clean()

    def merge_and_clean(self):
        unique = set()
        pfx = (":: ", "127.0.0.1 ", "0.0.0.0 ", "||", "-", "*.")
        
        if os.path.exists(self.output_file):
            self.log("Lese alte lokale Liste ein...", "info")
            with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f: unique.add(line.strip())

        fps = [os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir)]
        if os.path.exists(self.custom_blocklist_file): fps.append(self.custom_blocklist_file)
        
        self.root.after(0, lambda: self.progress_bar.config(maximum=len(fps), value=0))
        done = 0
        
        def process_file(fp):
            loc = set()
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    for l in f:
                        l = l.strip()
                        if not l or l.startswith(('#', '!')): continue
                        for p in pfx:
                            if l.startswith(p): l = l[len(p):].strip(); break
                        if l.endswith('^'): l = l[:-1]
                        if l.startswith('*') or l.endswith('*'): l = l.strip('*')
                        if l: loc.add(l)
            except: pass
            return loc, os.path.basename(fp)

        with ThreadPoolExecutor() as ex:
            for fut in as_completed([ex.submit(process_file, p) for p in fps]):
                ls, fn = fut.result()
                done += 1
                if done % max(1, len(fps)//10) == 0 or done == len(fps):
                    self.root.after(0, lambda v=done: self.progress_bar.config(value=v))
                self.log(f"✓ {fn} ({len(ls)} Einträge)")
                unique.update(ls)

        self.log("\nSchreibe Datei...", "info")
        ul = list(unique); unique.clear(); ul.sort()
        with open(self.output_file, 'w', encoding='utf-8') as out:
            out.writelines(l + '\n' for l in ul)
        cnt = len(ul); ul.clear()
        
        self.log(f"ERFOLG: {cnt} Einträge gespeichert.", "success")
        try:
            # Löscht nun rigoros den gesamten pihole_data Ordner und seinen Inhalt
            shutil.rmtree(self.work_dir, ignore_errors=True)
            self.log(f"Temporärer Arbeitsordner '{self.work_dir}' restlos gelöscht.", "success")
        except Exception as e:
            self.log(f"Warnung beim Löschen des Temp-Ordners: {e}", "warning")

    # =========================================================================
    # CORE: SPLIT UPLOAD & UPDATE & TERMINAL
    # =========================================================================
    def trigger_ssh(self, do_upload, do_update):
        if do_upload and not os.path.exists(self.output_file):
            messagebox.showerror("Fehler", f"Datei {self.output_file} existiert nicht. Bitte erst generieren!")
            return
        self.sync_memory()
        save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, self.text_links.get("1.0", tk.END).strip())
        c = GLOBAL_CONFIG
        if do_upload and not all([c["up_host"], c["up_user"], c["up_pass"], c["up_path"]]):
            messagebox.showwarning("Fehlende Daten", "Bitte Upload-Felder ausfüllen!")
            return
        if do_update and not all([c["pi_host"], c["pi_user"], c["pi_pass"], c["pi_cmd"]]):
            messagebox.showwarning("Fehlende Daten", "Bitte Pi-Hole-Felder ausfüllen!")
            return

        mode_str = "UPLOAD & UPDATE" if do_upload and do_update else ("NUR UPLOAD" if do_upload else "NUR UPDATE")
        self.log(f"\n--- STARTE {mode_str} ---", "info")
        threading.Thread(target=self.ssh_split_workflow, args=(do_upload, do_update), daemon=True).start()

    def ssh_split_workflow(self, do_upload, do_update):
        c = GLOBAL_CONFIG
        
        if do_upload:
            try:
                self.log(f"Verbinde Webserver {c['up_host']}...", "info")
                ssh_up = paramiko.SSHClient(); ssh_up.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_up.connect(c['up_host'], username=c['up_user'], password=c['up_pass'], timeout=10)
                self.log("Starte SFTP Übertragung...", "info")
                sftp = ssh_up.open_sftp()
                
                def cb(t, m): 
                    self.root.after(0, lambda: self.progress_bar.config(maximum=m, value=t))
                    
                sftp.put(self.output_file, c['up_path'], callback=cb)
                sftp.close(); ssh_up.close()
                self.log("✅ Upload erfolgreich!\n", "success")
            except Exception as e:
                self.log(f"❌ Upload Fehler: {e}", "error")
                return

        if do_update:
            try:
                self.log(f"Verbinde Pi-Hole Server {c['pi_host']}...", "info")
                ssh_pi = paramiko.SSHClient(); ssh_pi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_pi.connect(c['pi_host'], username=c['pi_user'], password=c['pi_pass'], timeout=10)
                
                _, stdout, _ = ssh_pi.exec_command('which screen')
                has_screen = bool(stdout.read().strip())
                
                custom_cmd = c['pi_cmd']
                if c['pi_user'].strip().lower() != 'root':
                    custom_cmd = custom_cmd.replace("sudo ", f"echo \"{c['pi_pass']}\" | sudo -S ")
                    
                if has_screen:
                    cmd = f"screen -dmS pi_upd bash -lc '{{ {custom_cmd} ; echo \"===PIHOLE_UPDATE_DONE===\" ; }} > /tmp/pi_upd.log 2>&1'"
                else:
                    cmd = f"nohup bash -lc '{{ {custom_cmd} ; echo \"===PIHOLE_UPDATE_DONE===\" ; }} > /tmp/pi_upd.log 2>&1' > /dev/null 2>&1 &"
                
                ssh_pi.exec_command('rm -f /tmp/pi_upd.log'); time.sleep(1)
                self.log(f"Starte Befehl(e): {c['pi_cmd']}", "info")
                ssh_pi.exec_command(cmd)
                
                self.log("📡 Lese Live-Ausgabe:", "pihole")
                lidx = 0; done = False
                while True:
                    try:
                        _, out, err = ssh_pi.exec_command('cat /tmp/pi_upd.log', timeout=5)
                        e_str = err.read().decode().strip()
                        if "No such file" in e_str: time.sleep(2); continue
                        
                        lines = out.readlines()
                        if lines and len(lines) > lidx:
                            for l in lines[lidx:]:
                                cl = l.strip()
                                if cl == "===PIHOLE_UPDATE_DONE===": done = True; break
                                if cl: self.log(f"[Pi-Hole] {cl}", "pihole")
                            lidx = len(lines)
                            
                        if done:
                            self.log("✅ Update auf dem Server abgeschlossen.", "success")
                            break
                        time.sleep(2)
                    except Exception:
                        self.log("🔌 SSH Verbindung getrennt (Vermutlich wegen Reboot).", "warning")
                        break
            except Exception as e:
                self.log(f"❌ Update Fehler: {e}", "error")
            finally:
                ssh_pi.close()

    def open_ssh_terminal(self):
        self.sync_memory()
        c = GLOBAL_CONFIG
        
        term_dialog = tk.Toplevel(self.root)
        term_dialog.title(t("btn_term"))
        term_dialog.geometry("350x150")
        term_dialog.configure(bg=get_colors()["bg_main"])
        term_dialog.grab_set()

        term_dialog.update_idletasks()
        x = (term_dialog.winfo_screenwidth() // 2) - 175
        y = (term_dialog.winfo_screenheight() // 2) - 75
        term_dialog.geometry(f"+{x}+{y}")

        tk.Label(term_dialog, text=t("term_choice"), bg=get_colors()["bg_main"], fg=get_colors()["fg_text"], font=("Arial", 10)).pack(pady=20)

        def connect_to(host_type):
            term_dialog.destroy()
            if host_type == 'up':
                host, user, pwd = c.get("up_host"), c.get("up_user"), c.get("up_pass")
            else:
                host, user, pwd = c.get("pi_host"), c.get("pi_user"), c.get("pi_pass")

            if not host or not user or not pwd:
                messagebox.showwarning("Fehler", "Bitte SSH Daten für diesen Server ausfüllen!")
                return

            sys_os = platform.system().lower()
            env = os.environ.copy()
            env['SSHPASS'] = pwd
            safe_opts = "-o StrictHostKeyChecking=no -o LogLevel=ERROR"
            ssh_cmd = f"sshpass -e ssh {safe_opts} {user}@{host}"
            
            try:
                if sys_os == 'windows':
                    subprocess.Popen(['cmd', '/c', f'start cmd /k {ssh_cmd}'], env=env)
                elif sys_os == 'darwin':
                    subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "{ssh_cmd}"'], env=env)
                else:
                    success = False
                    terminals = [
                        ['gnome-terminal', '--', 'bash', '-c', ssh_cmd], 
                        ['xfce4-terminal', '-e', ssh_cmd], 
                        ['konsole', '-e', ssh_cmd], 
                        ['xterm', '-e', ssh_cmd]
                    ]
                    for term in terminals:
                        try:
                            subprocess.Popen(term, env=env)
                            success = True; break
                        except FileNotFoundError: continue
                    if not success:
                        messagebox.showerror("Fehler", "Kein unterstütztes Terminal (gnome/xfce4/konsole/xterm) gefunden.\nBitte 'sshpass' installieren.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Terminal nicht öffnen: {e}")

        btn_frame = tk.Frame(term_dialog, bg=get_colors()["bg_main"])
        btn_frame.pack(fill=tk.X, padx=10)
        
        tk.Button(btn_frame, text=t("term_up"), bg="#FF5722", fg="white", font=("Arial", 9, "bold"), command=lambda: connect_to('up'), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Button(btn_frame, text=t("term_pi"), bg="#009688", fg="white", font=("Arial", 9, "bold"), command=lambda: connect_to('pi'), relief=tk.FLAT).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)


# =========================================================================
# NEUER BOOTLOADER: SINGLE-WINDOW-LIFECYCLE (ANTI-SEGFAULT-ENGINE)
# =========================================================================
def boot_app():
    dprint("Initiiere tk.Tk()...")
    try:
        root = tk.Tk()
    except Exception as e:
        dprint(f"KRITISCHER FEHLER BEI tk.Tk(): {e}")
        sys.exit(1)

    c = get_colors()
    root.title("Sicherheits-Tresor")
    root.configure(bg=c["bg_main"])

    # Zentriere das Fenster für den Login
    w, h = 400, 250
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws//2) - (w//2)
    y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Der sichere Container, in dem ALLES (Login und Main-App) abwechselnd stattfindet
    main_container = tk.Frame(root, bg=c["bg_main"])
    main_container.pack(fill=tk.BOTH, expand=True)

    # --- LOGIN UI WIRD IM CONTAINER GEBAUT ---
    login_frame = tk.Frame(main_container, bg=c["bg_main"])
    login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(login_frame, text="🔑 Pi-Hole Manager Login", bg=c["bg_main"], fg=c["fg_text"], font=("Arial", 12, "bold")).pack(pady=(0, 15))
    
    is_new = (__ENCRYPTED_PAYLOAD__ == "")
    tk.Label(login_frame, text="Neues Master-Passwort erstellen:" if is_new else "Master-Passwort eingeben:", bg=c["bg_main"], fg=c["fg_text"]).pack()

    pw_ent = tk.Entry(login_frame, show="*", width=30, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"])
    pw_ent.pack(pady=5)
    pw_ent.focus()

    pw_ent2 = None
    if is_new:
        tk.Label(login_frame, text="Wiederholen:", bg=c["bg_main"], fg=c["fg_text"]).pack()
        pw_ent2 = tk.Entry(login_frame, show="*", width=30, bg=c["bg_input"], fg=c["fg_text"], insertbackground=c["fg_text"])
        pw_ent2.pack(pady=5)

    def submit(e=None):
        global GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG
        p1 = pw_ent.get()
        login_success = False
        
        if is_new:
            if p1 != pw_ent2.get() or not p1:
                messagebox.showerror("Fehler", "Passwörter ungleich!", parent=root)
                return
            GLOBAL_PW = p1
            GLOBAL_SALT = os.urandom(16)
            GLOBAL_CONFIG = {"lang": "de", "theme": "dark"}
            save_payload_to_script(GLOBAL_PW, GLOBAL_SALT, GLOBAL_CONFIG, __PLAINTEXT_LINKS__)
            login_success = True
        else:
            GLOBAL_PW = p1
            GLOBAL_SALT = bytes.fromhex(__PAYLOAD_SALT__)
            try:
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=GLOBAL_SALT, iterations=100000)
                key = base64.urlsafe_b64encode(kdf.derive(GLOBAL_PW.encode()))
                f = Fernet(key)
                dec = f.decrypt(__ENCRYPTED_PAYLOAD__.encode()).decode()
                GLOBAL_CONFIG = json.loads(dec)
                login_success = True
            except Exception:
                messagebox.showerror("Fehler", "Falsches Passwort!", parent=root)
                pw_ent.delete(0, tk.END)

        if login_success:
            dprint("Login OK. Zerstöre Login-Frame und bereite WM-Resize vor...")
            # Wir zerstören NUR den Login-Kasten, das Hauptfenster bleibt unberührt offen
            login_frame.destroy() 
            
            c_main = get_colors()
            root.configure(bg=c_main["bg_main"])
            main_container.configure(bg=c_main["bg_main"])
            
            root.title(f"Pi-Hole Blocklist Manager v{__VERSION__}")
            w_main, h_main = 1600, 900
            x_main = (ws//2) - (w_main//2)
            y_main = (hs//2) - (h_main//2)
            root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")
            root.minsize(1050, 700)
            
            # Zwingt Linux (Wayland/X11) die Größenänderung durchzuführen BEVOR die Widgets existieren
            root.update() 
            
            dprint("Warte 500ms auf Wayland/X11 Sync vor Widget-Bau...")
            # Exakt hier ist der Schutzschild: Eine halbe Sekunde Pause, damit der Compositor nicht abstürzt
            root.after(500, lambda: PiholeBlocklistManager(main_container))

    # Falls der Benutzer das Fenster übers "X" im Login schließt
    def on_close_login():
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_close_login)

    tk.Button(login_frame, text="Starten", command=submit, bg="#4CAF50", fg="white", relief=tk.FLAT, padx=20).pack(pady=20)
    root.bind("<Return>", submit)

    # --- SCHLEIFE (Wird NIE unterbrochen) ---
    root.mainloop() 


if __name__ == "__main__":
    boot_app()
