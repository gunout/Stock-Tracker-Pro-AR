import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import pytz
import warnings
import random
from requests.exceptions import HTTPError, ConnectionError
import urllib3
warnings.filterwarnings('ignore')

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration de la page
st.set_page_config(
    page_title="Tracker Bourse Arabe - Marchés du Moyen-Orient",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration du fuseau horaire
USER_TIMEZONE = pytz.timezone('Europe/Paris')  # UTC+1/UTC+2
ARAB_TIMEZONES = {
    'Saudi Arabia': pytz.timezone('Asia/Riyadh'),  # UTC+3
    'UAE': pytz.timezone('Asia/Dubai'),  # UTC+4
    'Qatar': pytz.timezone('Asia/Qatar'),  # UTC+3
    'Kuwait': pytz.timezone('Asia/Kuwait'),  # UTC+3
    'Egypt': pytz.timezone('Africa/Cairo'),  # UTC+2
    'Morocco': pytz.timezone('Africa/Casablanca'),  # UTC+0/UTC+1
    'Jordan': pytz.timezone('Asia/Amman'),  # UTC+3
    'Lebanon': pytz.timezone('Asia/Beirut'),  # UTC+2/UTC+3
    'Tunisia': pytz.timezone('Africa/Tunis'),  # UTC+1
    'Oman': pytz.timezone('Asia/Muscat'),  # UTC+4
    'Bahrain': pytz.timezone('Asia/Bahrain'),  # UTC+3
    'Palestine': pytz.timezone('Asia/Hebron'),  # UTC+2/UTC+3
    'Iraq': pytz.timezone('Asia/Baghdad'),  # UTC+3
    'Syria': pytz.timezone('Asia/Damascus'),  # UTC+2/UTC+3
    'Yemen': pytz.timezone('Asia/Aden'),  # UTC+3
    'Libya': pytz.timezone('Africa/Tripoli'),  # UTC+2
    'Algeria': pytz.timezone('Africa/Algiers'),  # UTC+1
    'Mauritania': pytz.timezone('Africa/Nouakchott'),  # UTC+0
    'Sudan': pytz.timezone('Africa/Khartoum'),  # UTC+2
    'Comoros': pytz.timezone('Indian/Comoro'),  # UTC+3
    'Djibouti': pytz.timezone('Africa/Djibouti'),  # UTC+3
    'Somalia': pytz.timezone('Africa/Mogadishu'),  # UTC+3
}

# Style CSS personnalisé
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    
    .main-header {
        font-size: 2.5rem;
        color: #006C35;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Amiri', serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #00843D 0%, #FFFFFF 50%, #CE1126 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .arabic-text {
        font-family: 'Amiri', serif;
        font-size: 1.2rem;
        direction: rtl;
        text-align: right;
    }
    .stock-price {
        font-size: 2.5rem;
        font-weight: bold;
        color: #006C35;
        text-align: center;
    }
    .stock-change-positive {
        color: #00843D;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .stock-change-negative {
        color: #CE1126;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .portfolio-table {
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
    }
    .timezone-badge {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 0.5rem 1rem;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .arab-market-note {
        background: linear-gradient(135deg, #00843D 0%, #FFFFFF 50%, #CE1126 100%);
        color: #000000;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
        font-family: 'Amiri', serif;
    }
    .tadawul-badge {
        background-color: #006C35;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
    }
    .dfm-badge {
        background-color: #CE1126;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
    }
    .qe-badge {
        background-color: #8A1538;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
    }
    .egx-badge {
        background-color: #000000;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
    }
    .casa-badge {
        background-color: #C1272D;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
    }
    .demo-mode-badge {
        background-color: #ff9800;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .friday-note {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if 'price_alerts' not in st.session_state:
    st.session_state.price_alerts = []

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        # Saudi Arabia (Tadawul) - .SR
        '2222.SR',  # Saudi Aramco
        '1180.SR',  # Al Rajhi Bank
        '2010.SR',  # SABIC
        '1120.SR',  # Alinma Bank
        '1150.SR',  # Alinma Bank
        '1211.SR',  # Saudi National Bank
        '1010.SR',  # Riyad Bank
        '1060.SR',  # Samba Financial Group
        '1080.SR',  # Saudi Fransi
        '1090.SR',  # SAIB
        '7010.SR',  # STC
        '5110.SR',  # Ma'aden
        '2290.SR',  # Yanbu Cement
        '3003.SR',  # Almarai
        '2050.SR',  # Savola
        '4001.SR',  # Saudi Electricity
        '4030.SR',  # ACWA Power
        '6012.SR',  # Rabigh Refining
        
        # UAE - Dubai (DFM) - .DU
        'DUBAI.DU',  # Dubai Financial Market
        'EMIRATES.DU',  # Emirates NBD
        'EMAAR.DU',  # Emaar Properties
        'DEWA.DU',  # Dubai Electricity
        'DIB.DU',  # Dubai Islamic Bank
        'SALAM.DU',  # Salam International
        'AIRARABIA.DU',  # Air Arabia
        'AMANAT.DU',  # Amanat Holdings
        'ARKAN.DU',  # Arkan
        'DFM.DU',  # Dubai Financial Market
        'DXBENT.DU',  # DXB Entertainments
        'EMIRATES.DU',  # Emirates Integrated Telecom
        'GFH.DU',  # GFH Financial
        'GULFNAV.DU',  # Gulf Navigation
        'NCTH.DU',  # National Cement
        'TABREED.DU',  # Tabreed
        
        # UAE - Abu Dhabi (ADX) - .AD
        'FAB.AD',  # First Abu Dhabi Bank
        'ADNOC.AD',  # ADNOC Distribution
        'ADIB.AD',  # Abu Dhabi Islamic Bank
        'ALDAR.AD',  # Aldar Properties
        'TAQA.AD',  # Abu Dhabi National Energy
        'ETISALAT.AD',  # Etisalat
        'ADCB.AD',  # Abu Dhabi Commercial Bank
        'UNB.AD',  # Union National Bank
        'RAKBANK.AD',  # National Bank of Ras Al Khaimah
        'SHARJAH.AD',  # Sharjah Islamic Bank
        'ADAVATION.AD',  # Abu Dhabi Aviation
        'ADNH.AD',  # Abu Dhabi National Hotels
        'AGTHIA.AD',  # Agthia Group
        'ARAMEX.AD',  # Aramex
        'DANA.AD',  # Dana Gas
        'FUJAIRAH.AD',  # Fujairah Cement
        
        # Qatar (QSE) - .QA
        'QNBK.QA',  # Qatar National Bank
        'IQCD.QA',  # Industries Qatar
        'QIBK.QA',  # Qatar Islamic Bank
        'ORDS.QA',  # Ooredoo
        'QEWS.QA',  # Qatar Electricity & Water
        'CBQK.QA',  # Commercial Bank
        'QIIK.QA',  # Qatar International Islamic Bank
        'QIGD.QA',  # Qatari German Medical
        'QNCD.QA',  # Qatar Navigation
        'QGTS.QA',  # Qatar Gas Transport
        'QCFS.QA',  # Qatar Fuel
        'QAMC.QA',  # Qatar Aluminum
        'QIMD.QA',  # Qatar Industrial Manufacturing
        'QOIS.QA',  # Qatar Oman Investment
        'QNNS.QA',  # Qatar National Cement
        'WDAM.QA',  # Widam Food
        
        # Kuwait (Boursa Kuwait) - .KW
        'NBK.KW',  # National Bank of Kuwait
        'ZAIN.KW',  # Zain Group
        'KFH.KW',  # Kuwait Finance House
        'AGILITY.KW',  # Agility
        'BURGAN.KW',  # Burgan Bank
        'GBK.KW',  # Gulf Bank
        'CBK.KW',  # Commercial Bank of Kuwait
        'ABK.KW',  # Ahli United Bank
        'KIB.KW',  # Kuwait International Bank
        'KCIN.KW',  # Kuwait Cement
        'KPPC.KW',  # Kuwait Projects
        'MABANEE.KW',  # Mabanee
        'NATIONAL.KW',  # National Industries Group
        'SAK.KW',  # Al-Safat Investment
        
        # Egypt (EGX) - .CA
        'COMI.CA',  # Commercial International Bank
        'JUFO.CA',  # El Sewedy Electric
        'TMGH.CA',  # Talaat Moustafa Group
        'EFGD.CA',  # EFG Hermes
        'ESRS.CA',  # Ezz Steel
        'ORWE.CA',  # Orascom Construction
        'ORTE.CA',  # Orascom Telecom
        'OTMT.CA',  # OTMT
        'PHDC.CA',  # Palm Hills Developments
        'SKPC.CA',  # Sidi Kerir Petrochemicals
        'SUGR.CA',  # Sugar and Integrated Industries
        'SWDY.CA',  # Elsewedy Electric
        'TALAAT.CA',  # Talaat Moustafa
        'ABUK.CA',  # Abu Qir Fertilizers
        'ALEX.CA',  # Alexandria Mineral Oils
        'AMER.CA',  # Amer Group
        
        # Morocco (Casablanca) - .MA
        'ATW.MA',  # Attijariwafa Bank
        'BCP.MA',  # Banque Centrale Populaire
        'BMCE.MA',  # BMCE Bank
        'BOA.MA',  # Bank Of Africa
        'IAM.MA',  # Maroc Telecom
        'LAC.MA',  # LafargeHolcim Maroc
        'COS.MA',  # Cosumar
        'CMA.MA',  # Ciments du Maroc
        'SNI.MA',  # Société Nationale d'Investissement
        'ADH.MA',  # Addoha
        'RDS.MA',  # Réalisations et Développements
        'MNG.MA',  # Managem
        'SAM.MA',  # Sonasid
        'DLM.MA',  # Delattre Levivier
        'IBK.MA',  # IB Maroc
        'SRM.MA',  # Stroc Industrie
        
        # Jordan (Amman) - .JO
        'ARBK.JO',  # Arab Bank
        'JOBK.JO',  # Jordan Islamic Bank
        'HIK.JO',  # Hikma Pharmaceuticals
        'JOEP.JO',  # Jordan Electric Power
        'JOPT.JO',  # Jordan Petroleum Refinery
        'APOT.JO',  # Arab Potash
        'JPHC.JO',  # Jordan Phosphate Mines
        'UMIC.JO',  # Union Investment
        'JOVC.JO',  # Jordan Vegetable Oil
        'JOST.JO',  # Jordan Steel
        'JOCK.JO',  # Jordan Cement
        'JOTF.JO',  # Jordan Telecom
        'JOTL.JO',  # Jordan Telecom
        'JOMG.JO',  # Jordan Magnesia
        
        # Oman (MSM) - .OM
        'BKMB.OM',  # Bank Muscat
        'BKDB.OM',  # Bank Dhofar
        'OIBK.OM',  # Oman International Bank
        'SBKI.OM',  # Sohar Bank
        'ONIC.OM',  # Oman National Investment
        'ORDS.OM',  # Ooredoo Oman
        'OPTP.OM',  # Oman Petroleum
        'OMCI.OM',  # Oman Cement
        'RCCI.OM',  # Raysut Cement
        'SALU.OM',  # Salalah Mills
        'OMGR.OM',  # Oman Gulf
        'OMDS.OM',  # Oman & Dubai
        
        # Bahrain (BHB) - .BH
        'BBK.BH',  # Bank of Bahrain and Kuwait
        'NBK.BH',  # National Bank of Bahrain
        'ABC.BH',  # Arab Banking Corporation
        'BISB.BH',  # Bahrain Islamic Bank
        'KHCB.BH',  # Khaleeji Commercial Bank
        'BATELCO.BH',  # Batelco
        'BMMI.BH',  # BMMI
        'GFH.BH',  # GFH Financial
        'INOVEST.BH',  # Inovest
        'SEEF.BH',  # Seef Properties
        
        # Tunisia (BVMT) - .TN
        'BH.TN',  # Banque de l'Habitat
        'BIAT.TN',  # BIAT
        'BT.TN',  # Banque de Tunisie
        'STB.TN',  # STB Bank
        'ATB.TN',  # ATB Bank
        'UIB.TN',  # UIB
        'TUNISAIR.TN',  # Tunisair
        'SOTETEL.TN',  # Sotetel
        'TELNET.TN',  # Telnet
        'SOPAT.TN',  # Sopat
        'SOTRAPIL.TN',  # Sotrapil
        'SOTUVER.TN',  # Sotuver
        
        # Palestine (PEX) - .PS
        'BOP.PS',  # Bank of Palestine
        'PALTRADE.PS',  # Palestine Trade
        'PADICO.PS',  # Palestine Development
        'APIC.PS',  # Arab Palestinian Investment
        'PALTEL.PS',  # Palestine Telecom
        'PEC.PS',  # Palestine Electric
        'JPH.PS',  # Jerusalem Pharmaceuticals
        'NIC.PS',  # National Insurance
        'WATANIYA.PS',  # Wataniya Mobile
        
        # Lebanon (BSE) - .LB
        'BLOM.LB',  # Blom Bank
        'AUDI.LB',  # Bank Audi
        'BYB.LB',  # Byblos Bank
        'BLF.LB',  # Banque Libano-Française
        'SOLIDERE.LB',  # Solidere
        'HOLCIM.LB',  # Holcim Liban
        'CIMENT.LB',  # Cimenterie Nationale
        'INVEST.LB',  # Lebanese Investment
    ]

if 'notifications' not in st.session_state:
    st.session_state.notifications = []

if 'email_config' not in st.session_state:
    st.session_state.email_config = {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email': '',
        'password': ''
    }

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

if 'last_successful_data' not in st.session_state:
    st.session_state.last_successful_data = {}

# Mapping des suffixes pour les bourses arabes
ARAB_EXCHANGES = {
    '.SR': 'Tadawul - Saudi Arabia (السوق المالية السعودية)',
    '.DU': 'Dubai Financial Market (سوق دبي المالي)',
    '.AD': 'Abu Dhabi Securities Exchange (سوق أبوظبي للأوراق المالية)',
    '.QA': 'Qatar Stock Exchange (بورصة قطر)',
    '.KW': 'Boursa Kuwait (بورصة الكويت)',
    '.CA': 'Egyptian Exchange (البورصة المصرية)',
    '.MA': 'Casablanca Stock Exchange (بورصة الدار البيضاء)',
    '.JO': 'Amman Stock Exchange (بورصة عمان)',
    '.OM': 'Muscat Stock Exchange (بورصة مسقط)',
    '.BH': 'Bahrain Bourse (بورصة البحرين)',
    '.TN': 'Bourse de Tunis (بورصة تونس)',
    '.PS': 'Palestine Exchange (بورصة فلسطين)',
    '.LB': 'Beirut Stock Exchange (بورصة بيروت)',
    '': 'International Listing',
}

# Jours fériés dans les pays arabes (dates variables selon le calendrier lunaire)
# Principaux jours fériés 2024 (approximatifs)
ARAB_HOLIDAYS_2024 = {
    'Saudi Arabia': ['2024-04-10', '2024-04-11', '2024-04-12', '2024-06-15', '2024-06-16', '2024-06-17', '2024-09-22', '2024-09-23'],
    'UAE': ['2024-01-01', '2024-04-10', '2024-04-11', '2024-04-12', '2024-06-15', '2024-06-16', '2024-06-17', '2024-12-02', '2024-12-03'],
    'Qatar': ['2024-02-12', '2024-02-13', '2024-04-10', '2024-04-11', '2024-04-12', '2024-06-15', '2024-06-16', '2024-06-17', '2024-12-18'],
    'Kuwait': ['2024-01-01', '2024-02-25', '2024-02-26', '2024-04-10', '2024-04-11', '2024-04-12', '2024-06-15', '2024-06-16', '2024-06-17'],
    'Egypt': ['2024-01-07', '2024-01-25', '2024-04-09', '2024-04-10', '2024-04-25', '2024-05-01', '2024-06-30', '2024-07-23', '2024-10-06'],
    'Morocco': ['2024-01-01', '2024-01-11', '2024-04-10', '2024-04-11', '2024-05-01', '2024-06-16', '2024-06-17', '2024-07-30', '2024-08-14'],
    'Jordan': ['2024-01-01', '2024-04-10', '2024-04-11', '2024-05-01', '2024-05-25', '2024-06-16', '2024-06-17', '2024-12-25'],
    'Tunisia': ['2024-01-01', '2024-01-14', '2024-03-20', '2024-04-09', '2024-04-10', '2024-04-11', '2024-05-01', '2024-07-25', '2024-08-13'],
    'Oman': ['2024-01-01', '2024-04-10', '2024-04-11', '2024-06-15', '2024-06-16', '2024-07-23', '2024-11-18'],
    'Bahrain': ['2024-01-01', '2024-04-10', '2024-04-11', '2024-05-01', '2024-06-15', '2024-06-16', '2024-12-16', '2024-12-17'],
    'Palestine': ['2024-01-01', '2024-04-10', '2024-04-11', '2024-05-01', '2024-06-16', '2024-06-17', '2024-11-15', '2024-12-25'],
    'Lebanon': ['2024-01-01', '2024-02-09', '2024-03-25', '2024-04-10', '2024-04-11', '2024-05-01', '2024-05-06', '2024-08-15'],
}

# Données de démonstration pour les principales actions arabes
DEMO_DATA = {
    '2222.SR': {
        'name': 'Saudi Aramco (أرامكو السعودية)',
        'current_price': 32.50,
        'previous_close': 32.20,
        'day_high': 32.80,
        'day_low': 32.10,
        'volume': 15000000,
        'market_cap': 6500000000000,  # 6.5 Trillion SAR
        'pe_ratio': 15.2,
        'dividend_yield': 6.5,
        'beta': 0.8,
        'sector': 'Energy',
        'industry': 'Oil & Gas',
        'website': 'www.aramco.com'
    },
    '1180.SR': {
        'name': 'Al Rajhi Bank (مصرف الراجحي)',
        'current_price': 85.50,
        'previous_close': 84.80,
        'day_high': 86.20,
        'day_low': 84.50,
        'volume': 8000000,
        'market_cap': 340000000000,  # 340B SAR
        'pe_ratio': 18.5,
        'dividend_yield': 4.2,
        'beta': 0.9,
        'sector': 'Financials',
        'industry': 'Islamic Banking',
        'website': 'www.alrajhibank.com.sa'
    },
    'QNBK.QA': {
        'name': 'Qatar National Bank (بنك قطر الوطني)',
        'current_price': 18.20,
        'previous_close': 18.05,
        'day_high': 18.35,
        'day_low': 18.00,
        'volume': 5000000,
        'market_cap': 280000000000,  # 280B QAR
        'pe_ratio': 12.8,
        'dividend_yield': 5.5,
        'beta': 0.7,
        'sector': 'Financials',
        'industry': 'Banking',
        'website': 'www.qnb.com'
    },
    'FAB.AD': {
        'name': 'First Abu Dhabi Bank (بنك أبوظبي الأول)',
        'current_price': 15.30,
        'previous_close': 15.15,
        'day_high': 15.45,
        'day_low': 15.10,
        'volume': 6000000,
        'market_cap': 170000000000,  # 170B AED
        'pe_ratio': 14.2,
        'dividend_yield': 4.8,
        'beta': 0.8,
        'sector': 'Financials',
        'industry': 'Banking',
        'website': 'www.bankfab.com'
    },
    'COMI.CA': {
        'name': 'Commercial International Bank (البنك التجاري الدولي)',
        'current_price': 65.50,
        'previous_close': 65.00,
        'day_high': 66.20,
        'day_low': 64.80,
        'volume': 3000000,
        'market_cap': 120000000000,  # 120B EGP
        'pe_ratio': 9.5,
        'dividend_yield': 7.2,
        'beta': 1.1,
        'sector': 'Financials',
        'industry': 'Banking',
        'website': 'www.cibeg.com'
    },
    'ATW.MA': {
        'name': 'Attijariwafa Bank (بنك التجاري وفا)',
        'current_price': 480.00,
        'previous_close': 475.50,
        'day_high': 485.00,
        'day_low': 474.00,
        'volume': 200000,
        'market_cap': 95000000000,  # 95B MAD
        'pe_ratio': 16.8,
        'dividend_yield': 3.5,
        'beta': 0.6,
        'sector': 'Financials',
        'industry': 'Banking',
        'website': 'www.attijariwafabank.com'
    },
    'ARBK.JO': {
        'name': 'Arab Bank (البنك العربي)',
        'current_price': 5.80,
        'previous_close': 5.75,
        'day_high': 5.85,
        'day_low': 5.72,
        'volume': 1000000,
        'market_cap': 3800000000,  # 3.8B JOD
        'pe_ratio': 10.2,
        'dividend_yield': 4.5,
        'beta': 0.5,
        'sector': 'Financials',
        'industry': 'Banking',
        'website': 'www.arabbank.com'
    }
}

# Horaires des marchés arabes (heure locale)
ARAB_MARKET_HOURS = {
    'Saudi Arabia': {'open': 10, 'close': 15, 'tz': 'Asia/Riyadh'},  # 10:00-15:00
    'UAE': {'open': 10, 'close': 14, 'tz': 'Asia/Dubai'},  # 10:00-14:00
    'Qatar': {'open': 9, 'close': 13, 'tz': 'Asia/Qatar'},  # 09:00-13:00
    'Kuwait': {'open': 9, 'close': 13, 'tz': 'Asia/Kuwait'},  # 09:00-13:00
    'Egypt': {'open': 10, 'close': 14, 'tz': 'Africa/Cairo'},  # 10:00-14:00
    'Morocco': {'open': 9, 'close': 15, 'tz': 'Africa/Casablanca'},  # 09:00-15:00
    'Jordan': {'open': 10, 'close': 13, 'tz': 'Asia/Amman'},  # 10:00-13:00
    'Tunisia': {'open': 9, 'close': 13, 'tz': 'Africa/Tunis'},  # 09:00-13:00
    'Oman': {'open': 10, 'close': 14, 'tz': 'Asia/Muscat'},  # 10:00-14:00
    'Bahrain': {'open': 9, 'close': 13, 'tz': 'Asia/Bahrain'},  # 09:00-13:00
    'Palestine': {'open': 10, 'close': 13, 'tz': 'Asia/Hebron'},  # 10:00-13:00
    'Lebanon': {'open': 9, 'close': 13, 'tz': 'Asia/Beirut'},  # 09:00-13:00
}

# Jours de trading (dimanche-jeudi dans la plupart des pays arabes)
ARAB_TRADING_DAYS = [0, 1, 2, 3, 4]  # Dimanche (0) à Jeudi (4) pour les pays arabes

# Devises des pays arabes
ARAB_CURRENCIES = {
    '.SR': 'SAR',  # Saudi Riyal
    '.DU': 'AED',  # UAE Dirham
    '.AD': 'AED',  # UAE Dirham
    '.QA': 'QAR',  # Qatari Riyal
    '.KW': 'KWD',  # Kuwaiti Dinar
    '.CA': 'EGP',  # Egyptian Pound
    '.MA': 'MAD',  # Moroccan Dirham
    '.JO': 'JOD',  # Jordanian Dinar
    '.OM': 'OMR',  # Omani Rial
    '.BH': 'BHD',  # Bahraini Dinar
    '.TN': 'TND',  # Tunisian Dinar
    '.PS': 'JOD',  # Jordanian Dinar (Palestine)
    '.LB': 'LBP',  # Lebanese Pound
}

# Noms des pays
ARAB_COUNTRIES = {
    '.SR': 'Saudi Arabia',
    '.DU': 'UAE - Dubai',
    '.AD': 'UAE - Abu Dhabi',
    '.QA': 'Qatar',
    '.KW': 'Kuwait',
    '.CA': 'Egypt',
    '.MA': 'Morocco',
    '.JO': 'Jordan',
    '.OM': 'Oman',
    '.BH': 'Bahrain',
    '.TN': 'Tunisia',
    '.PS': 'Palestine',
    '.LB': 'Lebanon',
}

# Fonction pour générer des données historiques de démonstration
def generate_demo_history(symbol, period="1mo", interval="1d"):
    """Génère des données historiques simulées pour la démonstration"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    # Prix de base selon le symbole
    if symbol in DEMO_DATA:
        base_price = DEMO_DATA[symbol]['current_price']
        if 'ARAMCO' in symbol or '2222' in symbol:
            volatility = 0.015
        elif 'RAJHI' in symbol or '1180' in symbol:
            volatility = 0.02
        elif 'QNB' in symbol:
            volatility = 0.012
        elif 'FAB' in symbol:
            volatility = 0.018
        else:
            volatility = 0.022
    else:
        # Détection par suffixe
        suffix = next((s for s in ARAB_EXCHANGES.keys() if s and symbol.endswith(s)), '')
        if suffix == '.SR':  # Saudi
            base_price = random.uniform(20, 100)
            volatility = 0.02
        elif suffix in ['.DU', '.AD']:  # UAE
            base_price = random.uniform(5, 50)
            volatility = 0.025
        elif suffix == '.QA':  # Qatar
            base_price = random.uniform(10, 30)
            volatility = 0.018
        elif suffix == '.KW':  # Kuwait
            base_price = random.uniform(0.5, 2)  # KWD élevé
            volatility = 0.015
        elif suffix == '.CA':  # Egypt
            base_price = random.uniform(20, 100)
            volatility = 0.03
        elif suffix == '.MA':  # Morocco
            base_price = random.uniform(200, 1000)
            volatility = 0.02
        elif suffix == '.JO':  # Jordan
            base_price = random.uniform(2, 10)
            volatility = 0.018
        else:
            base_price = random.uniform(10, 500)
            volatility = 0.02
    
    # Générer une série de prix avec une légère tendance
    np.random.seed(hash(symbol) % 42)
    returns = np.random.normal(0.0002, volatility, len(dates))
    price_series = base_price * np.exp(np.cumsum(returns))
    
    # Créer le DataFrame
    df = pd.DataFrame({
        'Open': price_series * (1 - np.random.uniform(0, 0.01, len(dates))),
        'High': price_series * (1 + np.random.uniform(0, 0.02, len(dates))),
        'Low': price_series * (1 - np.random.uniform(0, 0.02, len(dates))),
        'Close': price_series,
        'Volume': np.random.randint(100000, 5000000, len(dates))
    }, index=dates)
    
    # Convertir l'index en timezone-aware
    df.index = df.index.tz_localize(USER_TIMEZONE)
    
    return df

# Fonction pour charger les données avec gestion des erreurs améliorée
@st.cache_data(ttl=600)
def load_stock_data(symbol, period, interval, retry_count=3):
    """Charge les données boursières avec gestion des erreurs et retry"""
    
    # Vérifier si on a des données en cache dans la session
    if st.session_state.demo_mode and symbol in DEMO_DATA:
        return generate_demo_history(symbol, period, interval), DEMO_DATA[symbol]
    
    for attempt in range(retry_count):
        try:
            if attempt > 0:
                time.sleep(2 ** attempt)
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval, timeout=10)
            info = ticker.info
            
            if hist is not None and not hist.empty:
                if hist.index.tz is None:
                    hist.index = hist.index.tz_localize('UTC').tz_convert(USER_TIMEZONE)
                else:
                    hist.index = hist.index.tz_convert(USER_TIMEZONE)
                
                st.session_state.last_successful_data[symbol] = {
                    'hist': hist,
                    'info': info,
                    'timestamp': datetime.now()
                }
                
                return hist, info
            
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                st.warning(f"⚠️ Limite de requêtes atteinte. Tentative {attempt + 1}/{retry_count}...")
            else:
                st.warning(f"⚠️ Erreur: {e}. Tentative {attempt + 1}/{retry_count}...")
    
    # Si toutes les tentatives échouent, utiliser les données en cache
    if symbol in st.session_state.last_successful_data:
        cached = st.session_state.last_successful_data[symbol]
        time_diff = datetime.now() - cached['timestamp']
        if time_diff.total_seconds() < 3600:
            st.info(f"📋 Utilisation des données en cache du {cached['timestamp'].strftime('%H:%M:%S')}")
            return cached['hist'], cached['info']
    
    # Activer le mode démo automatiquement
    if not st.session_state.demo_mode:
        st.session_state.demo_mode = True
        st.info("🔄 Mode démonstration activé - Données simulées")
    
    # Données de démonstration par défaut
    suffix = next((s for s in ARAB_EXCHANGES.keys() if s and symbol.endswith(s)), '')
    country = ARAB_COUNTRIES.get(suffix, 'Arab Market')
    
    demo_info = {
        'longName': f'{symbol} ({country} - Mode démo)',
        'sector': random.choice(['Financials', 'Energy', 'Real Estate', 'Telecom', 'Materials']),
        'industry': 'Various',
        'marketCap': random.randint(1000000000, 50000000000),
        'trailingPE': random.uniform(8, 20),
        'dividendYield': random.uniform(0.02, 0.08),
        'beta': random.uniform(0.5, 1.5),
        'website': 'N/A'
    }
    
    return generate_demo_history(symbol, period, interval), demo_info

def get_exchange_info(symbol):
    """Détermine l'échange pour un symbole"""
    suffix = next((s for s in ARAB_EXCHANGES.keys() if s and symbol.endswith(s)), '')
    exchange = ARAB_EXCHANGES.get(suffix, 'International Listing')
    country = ARAB_COUNTRIES.get(suffix, 'International')
    currency = ARAB_CURRENCIES.get(suffix, 'USD')
    return exchange, country, currency

def get_currency(symbol):
    """Détermine la devise pour un symbole"""
    suffix = next((s for s in ARAB_CURRENCIES.keys() if s and symbol.endswith(s)), '')
    return ARAB_CURRENCIES.get(suffix, 'USD')

def format_arab_currency(value, symbol):
    """Formate la monnaie selon le pays arabe"""
    if value is None or value == 0:
        return "N/A"
    
    currency = get_currency(symbol)
    
    # Formater selon la devise
    if currency == 'SAR':  # Saudi Riyal
        if value >= 1e9:  # Billion
            return f"{value/1e9:.2f} مليار ريال"  # SAR {value/1e9:.2f} B
        elif value >= 1e6:  # Million
            return f"{value/1e6:.2f} مليون ريال"  # SAR {value/1e6:.2f} M
        else:
            return f"{value:.2f} ريال"  # SAR {value:.2f}
    
    elif currency == 'AED':  # UAE Dirham
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار درهم"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون درهم"
        else:
            return f"{value:.2f} درهم"
    
    elif currency == 'QAR':  # Qatari Riyal
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار ريال"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون ريال"
        else:
            return f"{value:.2f} ريال"
    
    elif currency == 'KWD':  # Kuwaiti Dinar (valeur élevée)
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار دينار"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون دينار"
        else:
            return f"{value:.3f} دينار"
    
    elif currency == 'EGP':  # Egyptian Pound
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار جنيه"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون جنيه"
        else:
            return f"{value:.2f} جنيه"
    
    elif currency == 'MAD':  # Moroccan Dirham
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار درهم"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون درهم"
        else:
            return f"{value:.2f} درهم"
    
    elif currency == 'JOD':  # Jordanian Dinar (valeur élevée)
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار دينار"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون دينار"
        else:
            return f"{value:.3f} دينار"
    
    elif currency == 'OMR':  # Omani Rial (valeur élevée)
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار ريال"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون ريال"
        else:
            return f"{value:.3f} ريال"
    
    elif currency == 'BHD':  # Bahraini Dinar (valeur élevée)
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار دينار"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون دينار"
        else:
            return f"{value:.3f} دينار"
    
    elif currency == 'TND':  # Tunisian Dinar
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار دينار"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون دينار"
        else:
            return f"{value:.3f} دينار"
    
    elif currency == 'LBP':  # Lebanese Pound
        if value >= 1e9:
            return f"{value/1e9:.2f} مليار ليرة"
        elif value >= 1e6:
            return f"{value/1e6:.2f} مليون ليرة"
        else:
            return f"{value:,.0f} ليرة"
    
    else:  # USD par défaut
        if value >= 1e9:
            return f"${value/1e9:.2f} B"
        elif value >= 1e6:
            return f"${value/1e6:.2f} M"
        else:
            return f"${value:.2f}"

def format_large_number_arab(num, currency='USD'):
    """Formate les grands nombres selon le système arabe"""
    if num > 1e12:
        return f"{num/1e12:.2f} تريليون"  # Trillion
    elif num > 1e9:
        return f"{num/1e9:.2f} مليار"  # Billion
    elif num > 1e6:
        return f"{num/1e6:.2f} مليون"  # Million
    else:
        return f"{num:,.0f}"

def send_email_alert(subject, body, to_email):
    """Envoie une notification par email"""
    if not st.session_state.email_config['enabled']:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = st.session_state.email_config['email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(
            st.session_state.email_config['smtp_server'], 
            st.session_state.email_config['smtp_port']
        )
        server.starttls()
        server.login(
            st.session_state.email_config['email'],
            st.session_state.email_config['password']
        )
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur d'envoi: {e}")
        return False

def check_price_alerts(current_price, symbol):
    """Vérifie les alertes de prix"""
    triggered = []
    for alert in st.session_state.price_alerts:
        if alert['symbol'] == symbol:
            if alert['condition'] == 'above' and current_price >= alert['price']:
                triggered.append(alert)
            elif alert['condition'] == 'below' and current_price <= alert['price']:
                triggered.append(alert)
    
    return triggered

def get_market_status(country):
    """Détermine le statut du marché pour un pays arabe"""
    if country not in ARAB_MARKET_HOURS:
        return "Inconnu", "❓"
    
    market_info = ARAB_MARKET_HOURS[country]
    market_tz = pytz.timezone(market_info['tz'])
    now = datetime.now(market_tz)
    
    # Jour de la semaine (dimanche = 0 dans pytz, mais dans les pays arabes dimanche est le premier jour)
    weekday = now.weekday()
    friday = 4  # Vendredi
    saturday = 5  # Samedi
    
    # Weekend dans les pays arabes (vendredi-samedi pour la plupart)
    if weekday in [4, 5]:  # Vendredi ou Samedi
        return f"Fermé (weekend)", "🔴"
    
    # Jours fériés
    date_str = now.strftime('%Y-%m-%d')
    if country in ARAB_HOLIDAYS_2024 and date_str in ARAB_HOLIDAYS_2024[country]:
        return "Fermé (jour férié)", "🔴"
    
    # Horaires de trading
    current_hour = now.hour
    current_minute = now.minute
    
    open_hour = market_info['open']
    close_hour = market_info['close']
    
    if open_hour <= current_hour < close_hour:
        return "Ouvert", "🟢"
    elif current_hour < open_hour:
        return "Fermé (pré-ouverture)", "🟡"
    else:
        return "Fermé", "🔴"

def get_all_markets_status():
    """Récupère le statut de tous les marchés arabes"""
    statuses = {}
    for country in ARAB_MARKET_HOURS.keys():
        status, icon = get_market_status(country)
        statuses[country] = {'status': status, 'icon': icon}
    return statuses

def safe_get_metric(hist, metric, index=-1):
    """Récupère une métrique en toute sécurité"""
    try:
        if hist is not None and not hist.empty and len(hist) > abs(index):
            return hist[metric].iloc[index]
        return 0
    except:
        return 0

# Titre principal
st.markdown("<h1 class='main-header'>🕌 Tracker Bourse Arabe - Marchés du Moyen-Orient en Temps Réel</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: Amiri; font-size: 1.5rem;'>تتبع أسواق الأسهم العربية</p>", unsafe_allow_html=True)

# Bannière de fuseau horaire
current_time_paris = datetime.now(USER_TIMEZONE)
market_statuses = get_all_markets_status()

# Afficher les statuts des principaux marchés
col_status1, col_status2, col_status3, col_status4, col_status5 = st.columns(5)
with col_status1:
    status_sa = market_statuses.get('Saudi Arabia', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇸🇦 Arabie Saoudite: {status_sa['icon']} {status_sa['status']}")
with col_status2:
    status_uae = market_statuses.get('UAE', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇦🇪 UAE: {status_uae['icon']} {status_uae['status']}")
with col_status3:
    status_qa = market_statuses.get('Qatar', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇶🇦 Qatar: {status_qa['icon']} {status_qa['status']}")
with col_status4:
    status_kw = market_statuses.get('Kuwait', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇰🇼 Koweït: {status_kw['icon']} {status_kw['status']}")
with col_status5:
    status_eg = market_statuses.get('Egypt', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇪🇬 Égypte: {status_eg['icon']} {status_eg['status']}")

# Deuxième ligne de statuts
col_status6, col_status7, col_status8, col_status9, col_status10 = st.columns(5)
with col_status6:
    status_ma = market_statuses.get('Morocco', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇲🇦 Maroc: {status_ma['icon']} {status_ma['status']}")
with col_status7:
    status_jo = market_statuses.get('Jordan', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇯🇴 Jordanie: {status_jo['icon']} {status_jo['status']}")
with col_status8:
    status_tn = market_statuses.get('Tunisia', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇹🇳 Tunisie: {status_tn['icon']} {status_tn['status']}")
with col_status9:
    status_om = market_statuses.get('Oman', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇴🇲 Oman: {status_om['icon']} {status_om['status']}")
with col_status10:
    status_bh = market_statuses.get('Bahrain', {'status': 'Inconnu', 'icon': '❓'})
    st.markdown(f"🇧🇭 Bahreïn: {status_bh['icon']} {status_bh['status']}")

st.markdown(f"""
<div class='timezone-badge'>
    <b>🕐 Fuseaux horaires :</b><br>
    🇫🇷 Heure Paris : {current_time_paris.strftime('%H:%M:%S')} (UTC+1/UTC+2)<br>
    🇸🇦 Arabie Saoudite : {datetime.now(ARAB_TIMEZONES['Saudi Arabia']).strftime('%H:%M:%S')} (UTC+3)<br>
    🇦🇪 UAE : {datetime.now(ARAB_TIMEZONES['UAE']).strftime('%H:%M:%S')} (UTC+4)<br>
    🇶🇦 Qatar : {datetime.now(ARAB_TIMEZONES['Qatar']).strftime('%H:%M:%S')} (UTC+3)<br>
    🇪🇬 Égypte : {datetime.now(ARAB_TIMEZONES['Egypt']).strftime('%H:%M:%S')} (UTC+2)<br>
    🇲🇦 Maroc : {datetime.now(ARAB_TIMEZONES['Morocco']).strftime('%H:%M:%S')} (UTC+0/UTC+1)<br>
    📍 Décalages: -1h à -3h selon le pays
</div>
""", unsafe_allow_html=True)

# Note sur les jours de trading
st.markdown("""
<div class='friday-note'>
    📅 Note importante: Les marchés arabes sont généralement fermés le vendredi et le samedi. 
    Les jours de trading sont du dimanche au jeudi (sauf pour le Maroc et la Tunisie qui suivent le calendrier occidental).
</div>
""", unsafe_allow_html=True)

# Mode démo badge
if st.session_state.demo_mode:
    st.markdown("""
    <div style='text-align: center; margin: 10px 0;'>
        <span class='demo-mode-badge'>🎮 MODE DÉMONSTRATION</span>
        <span style='color: #666;'>Données simulées - API temporairement indisponible</span>
    </div>
    """, unsafe_allow_html=True)

# Note sur les marchés arabes
st.markdown("""
<div class='arab-market-note'>
    <span class='tadawul-badge'>تداول - Tadawul</span> 
    <span class='dfm-badge'>DFM - دبي</span>
    <span class='qe-badge'>QSE - قطر</span>
    <span class='egx-badge'>EGX - مصر</span>
    <span class='casa-badge'>Casablanca - الدار البيضاء</span><br>
    🇸🇦🇦🇪🇶🇦🇰🇼🇪🇬🇲🇦🇯🇴🇹🇳🇴🇲🇧🇭 Principales places financières du monde arabe<br>
    - Horaires: Généralement 10h-15h (heure locale), du dimanche au jeudi<br>
    - Vendredi et samedi: marchés fermés (sauf Maroc/Tunisie)<br>
    - Devises: Riyal, Dirham, Dinar, Livre selon le pays<br>
    - Impact des prix du pétrole sur les marchés du Golfe
</div>
""", unsafe_allow_html=True)

# Sidebar pour la navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/ksa.png", width=80)
    st.title("Navigation")
    
    # Boutons pour le mode démo
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("🎮 Mode Démo"):
            st.session_state.demo_mode = True
            st.rerun()
    with col_demo2:
        if st.button("🔄 Mode Réel"):
            st.session_state.demo_mode = False
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    menu = st.radio(
        "Choisir une section / اختر القسم",
        ["📈 Tableau de bord", 
         "💰 Portefeuille virtuel", 
         "🔔 Alertes de prix",
         "📧 Notifications email",
         "📤 Export des données",
         "🤖 Prédictions ML",
         "🇸🇦🇦🇪🇶🇦 Indices arabes"]
    )
    
    st.markdown("---")
    
    # Configuration commune
    st.subheader("⚙️ Configuration")
    st.caption(f"🕐 Fuseau : Heure Paris")
    
    # Sélection du symbole principal
    symbol_options = ["2222.SR (Saudi Aramco)", "1180.SR (Al Rajhi Bank)", "QNBK.QA (QNB)", 
                      "FAB.AD (FAB)", "COMI.CA (CIB)", "ATW.MA (Attijariwafa)", 
                      "ARBK.JO (Arab Bank)", "NBK.KW (NBK)", "Autre..."]
    
    selected_option = st.selectbox(
        "Symbole principal / الرمز الرئيسي",
        options=symbol_options,
        index=0
    )
    
    if selected_option == "Autre...":
        symbol = st.text_input("Entrer un symbole / أدخل الرمز", value="2222.SR").upper()
    else:
        symbol = selected_option.split()[0]
    
    # Afficher des informations sur le symbole
    if symbol:
        exchange, country, currency = get_exchange_info(symbol)
        st.caption(f"📍 {exchange}")
        st.caption(f"🌍 {country} | 💱 {currency}")
    
    st.caption("""
    📍 Suffixes par pays:
    - .SR: Arabie Saoudite (تداول)
    - .DU/.AD: UAE (DFM/ADX)
    - .QA: Qatar (بورصة قطر)
    - .KW: Koweït (بورصة الكويت)
    - .CA: Égypte (EGX)
    - .MA: Maroc (Casablanca)
    - .JO: Jordanie (بورصة عمان)
    - .OM: Oman (MSM)
    - .BH: Bahreïn (BHB)
    - .TN: Tunisie (BVMT)
    """)
    
    # Période et intervalle
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Période / الفترة",
            options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2
        )
    
    with col2:
        interval_map = {
            "1m": "1 minute", "5m": "5 minutes", "15m": "15 minutes",
            "30m": "30 minutes", "1h": "1 heure", "1d": "1 jour",
            "1wk": "1 semaine", "1mo": "1 mois"
        }
        interval = st.selectbox(
            "Intervalle / الفاصل",
            options=list(interval_map.keys()),
            format_func=lambda x: interval_map[x],
            index=4 if period == "1d" else 6
        )
    
    # Auto-refresh
    auto_refresh = st.checkbox("Actualisation automatique", value=False)
    if auto_refresh:
        st.warning("⚠️ L'actualisation automatique peut entraîner des limitations API")
        refresh_rate = st.slider(
            "Fréquence (secondes)",
            min_value=30,
            max_value=300,
            value=60,
            step=10
        )

# Chargement des données
try:
    hist, info = load_stock_data(symbol, period, interval)
except Exception as e:
    st.error(f"Erreur lors du chargement: {e}")
    st.session_state.demo_mode = True
    hist, info = generate_demo_history(symbol, period, interval), DEMO_DATA.get(symbol, {
        'longName': f'{symbol} (Mode démo)',
        'sector': 'N/A',
        'industry': 'N/A'
    })

if hist is None or hist.empty:
    st.warning(f"⚠️ Impossible de charger les données pour {symbol}. Utilisation du mode démo.")
    st.session_state.demo_mode = True
    hist = generate_demo_history(symbol, period, interval)
    info = DEMO_DATA.get(symbol, {
        'longName': f'{symbol} (Mode démo)',
        'sector': 'N/A',
        'industry': 'N/A',
        'marketCap': 10000000000
    })

current_price = safe_get_metric(hist, 'Close')

# Vérification des alertes
triggered_alerts = check_price_alerts(current_price, symbol)
for alert in triggered_alerts:
    st.balloons()
    st.success(f"🎯 Alerte déclenchée pour {symbol} à {format_arab_currency(current_price, symbol)}")
    
    if st.session_state.email_config['enabled']:
        subject = f"🚨 Alerte prix - {symbol}"
        body = f"""
        <h2>Alerte de prix déclenchée</h2>
        <p><b>Symbole:</b> {symbol}</p>
        <p><b>Prix actuel:</b> {format_arab_currency(current_price, symbol)}</p>
        <p><b>Condition:</b> {alert['condition']} {format_arab_currency(alert['price'], symbol)}</p>
        <p><b>Date:</b> {datetime.now(USER_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} (heure Paris)</p>
        """
        send_email_alert(subject, body, st.session_state.email_config['email'])
    
    if alert.get('one_time', False):
        st.session_state.price_alerts.remove(alert)

# ============================================================================
# SECTION 1: TABLEAU DE BORD
# ============================================================================
if menu == "📈 Tableau de bord":
    # Statut du marché spécifique au pays
    exchange, country, currency = get_exchange_info(symbol)
    market_status, market_icon = get_market_status(country)
    st.info(f"{market_icon} {country}: {market_status}")
    
    if hist is not None and not hist.empty:
        company_name = info.get('longName', symbol) if info else symbol
        if st.session_state.demo_mode:
            company_name += " (Mode démo)"
        
        st.subheader(f"📊 Aperçu en temps réel - {company_name}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        previous_close = safe_get_metric(hist, 'Close', -2) if len(hist) > 1 else current_price
        change = current_price - previous_close
        change_pct = (change / previous_close * 100) if previous_close != 0 else 0
        
        with col1:
            st.metric(
                label="Prix actuel",
                value=format_arab_currency(current_price, symbol),
                delta=f"{change:.2f} ({change_pct:.2f}%)"
            )
        
        with col2:
            day_high = safe_get_metric(hist, 'High')
            st.metric("Plus haut", format_arab_currency(day_high, symbol))
        
        with col3:
            day_low = safe_get_metric(hist, 'Low')
            st.metric("Plus bas", format_arab_currency(day_low, symbol))
        
        with col4:
            volume = safe_get_metric(hist, 'Volume')
            volume_formatted = f"{volume/1e6:.1f}M" if volume > 1e6 else f"{volume/1e3:.1f}K"
            st.metric("Volume", volume_formatted)
        
        try:
            local_time = hist.index[-1].tz_convert(ARAB_TIMEZONES.get(country, USER_TIMEZONE))
            st.caption(f"Dernière mise à jour: {hist.index[-1].strftime('%Y-%m-%d %H:%M:%S')} (heure Paris) / {local_time.strftime('%H:%M:%S')} (heure locale {country})")
        except:
            st.caption(f"Dernière mise à jour: {datetime.now(USER_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} (heure Paris)")
        
        # Graphique principal
        st.subheader("📉 Évolution du prix")
        
        fig = go.Figure()
        
        if interval in ["1m", "5m", "15m", "30m", "1h"]:
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Prix',
                increasing_line_color='#00843D',
                decreasing_line_color='#CE1126'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='Prix',
                line=dict(color='#006C35', width=2)
            ))
        
        if len(hist) >= 20:
            ma_20 = hist['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ma_20,
                mode='lines',
                name='MA 20',
                line=dict(color='orange', width=1, dash='dash')
            ))
        
        if len(hist) >= 50:
            ma_50 = hist['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ma_50,
                mode='lines',
                name='MA 50',
                line=dict(color='purple', width=1, dash='dash')
            ))
        
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            yaxis='y2',
            marker=dict(color='lightgray', opacity=0.3)
        ))
        
        fig.update_layout(
            title=f"{symbol} - {period} (heure Paris)",
            yaxis_title=f"Prix ({currency})",
            yaxis2=dict(
                title="Volume",
                overlaying='y',
                side='right',
                showgrid=False
            ),
            xaxis_title="Date (heure Paris)",
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Informations sur l'entreprise
        with st.expander("ℹ️ Informations sur l'entreprise"):
            if info:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Nom :** {info.get('longName', 'N/A')}")
                    st.write(f"**Secteur :** {info.get('sector', 'N/A')}")
                    st.write(f"**Industrie :** {info.get('industry', 'N/A')}")
                    st.write(f"**Site web :** {info.get('website', 'N/A')}")
                    st.write(f"**Bourse :** {exchange}")
                    st.write(f"**Pays :** {country}")
                    st.write(f"**Devise :** {currency}")
                
                with col2:
                    market_cap = info.get('marketCap', 0)
                    if market_cap > 0:
                        st.write(f"**Capitalisation :** {format_arab_currency(market_cap, symbol)} ({format_large_number_arab(market_cap, currency)})")
                    else:
                        st.write("**Capitalisation :** N/A")
                    
                    st.write(f"**P/E :** {info.get('trailingPE', 'N/A')}")
                    st.write(f"**Dividende :** {info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "**Dividende :** N/A")
                    st.write(f"**Beta :** {info.get('beta', 'N/A')}")
            else:
                st.write("Informations non disponibles")
    else:
        st.warning(f"Aucune donnée disponible pour {symbol}")

# ============================================================================
# SECTION 2: PORTEFEUILLE VIRTUEL
# ============================================================================
elif menu == "💰 Portefeuille virtuel":
    st.subheader("💰 Gestion de portefeuille virtuel - Actions Arabes")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### ➕ Ajouter une position")
        with st.form("add_position"):
            symbol_pf = st.text_input("Symbole", value="2222.SR").upper()
            
            exchange, country, currency = get_exchange_info(symbol_pf)
            st.caption(f"📍 {exchange} | {currency}")
            
            shares = st.number_input("Nombre d'actions", min_value=1, step=1, value=100)
            buy_price = st.number_input(f"Prix d'achat ({currency})", min_value=0.01, step=1.0, value=32.5)
            
            if st.form_submit_button("Ajouter au portefeuille"):
                if symbol_pf and shares > 0:
                    if symbol_pf not in st.session_state.portfolio:
                        st.session_state.portfolio[symbol_pf] = []
                    
                    st.session_state.portfolio[symbol_pf].append({
                        'shares': shares,
                        'buy_price': buy_price,
                        'currency': currency,
                        'country': country,
                        'date': datetime.now(USER_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    st.success(f"✅ {shares} actions {symbol_pf} ajoutées")
    
    with col1:
        st.markdown("### 📊 Performance du portefeuille")
        
        if st.session_state.portfolio:
            portfolio_data = []
            total_value_usd = 0
            total_cost_usd = 0
            
            # Taux de change approximatifs vers USD
            exchange_rates = {
                'SAR': 0.27,  # 1 SAR = 0.27 USD
                'AED': 0.27,  # 1 AED = 0.27 USD
                'QAR': 0.27,  # 1 QAR = 0.27 USD
                'KWD': 3.30,  # 1 KWD = 3.30 USD
                'EGP': 0.032, # 1 EGP = 0.032 USD
                'MAD': 0.10,  # 1 MAD = 0.10 USD
                'JOD': 1.41,  # 1 JOD = 1.41 USD
                'OMR': 2.60,  # 1 OMR = 2.60 USD
                'BHD': 2.65,  # 1 BHD = 2.65 USD
                'TND': 0.32,  # 1 TND = 0.32 USD
                'LBP': 0.00066, # 1 LBP = 0.00066 USD
                'USD': 1.00,
            }
            
            for symbol_pf, positions in st.session_state.portfolio.items():
                try:
                    if st.session_state.demo_mode and symbol_pf in DEMO_DATA:
                        current = DEMO_DATA[symbol_pf]['current_price']
                    else:
                        ticker = yf.Ticker(symbol_pf)
                        hist = ticker.history(period='1d')
                        current = hist['Close'].iloc[-1] if not hist.empty else 0
                    
                    exchange, country, currency = get_exchange_info(symbol_pf)
                    
                    for pos in positions:
                        shares = pos['shares']
                        buy_price = pos['buy_price']
                        cost = shares * buy_price
                        value = shares * current
                        profit = value - cost
                        profit_pct = (profit / cost * 100) if cost > 0 else 0
                        
                        # Conversion en USD pour le total
                        rate = exchange_rates.get(currency, 1.0)
                        total_cost_usd += cost * rate
                        total_value_usd += value * rate
                        
                        portfolio_data.append({
                            'Symbole': symbol_pf,
                            'Pays': country,
                            'Devise': currency,
                            'Actions': shares,
                            "Prix d'achat": f"{buy_price:,.2f} {currency}",
                            'Prix actuel': f"{current:,.2f} {currency}",
                            'Valeur': f"{value:,.2f} {currency}",
                            'Profit': f"{profit:,.2f} {currency}",
                            'Profit %': f"{profit_pct:.1f}%"
                        })
                except Exception as e:
                    st.warning(f"Impossible de charger {symbol_pf}")
            
            if portfolio_data:
                total_profit_usd = total_value_usd - total_cost_usd
                total_profit_pct_usd = (total_profit_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0
                
                st.markdown("#### Total en Dollars USD")
                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.metric("Valeur totale", f"${total_value_usd:,.2f}")
                col_i2.metric("Coût total", f"${total_cost_usd:,.2f}")
                col_i3.metric(
                    "Profit total",
                    f"${total_profit_usd:,.2f}",
                    delta=f"{total_profit_pct_usd:.1f}%"
                )
                
                st.markdown("### 📋 Positions détaillées")
                df_portfolio = pd.DataFrame(portfolio_data)
                st.dataframe(df_portfolio, use_container_width=True)
                
                try:
                    fig_pie = px.pie(
                        names=[p['Symbole'] for p in portfolio_data],
                        values=[float(p['Valeur'].split()[0].replace(',', '')) for p in portfolio_data],
                        title="Répartition du portefeuille"
                    )
                    st.plotly_chart(fig_pie)
                except:
                    st.warning("Impossible de générer le graphique")
                
                if st.button("🗑️ Vider le portefeuille"):
                    st.session_state.portfolio = {}
                    st.rerun()
            else:
                st.info("Aucune donnée de performance disponible")
        else:
            st.info("Aucune position dans le portefeuille. Ajoutez des actions arabes pour commencer !")

# ============================================================================
# SECTION 3: ALERTES DE PRIX
# ============================================================================
elif menu == "🔔 Alertes de prix":
    st.subheader("🔔 Gestion des alertes de prix")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ➕ Créer une nouvelle alerte")
        with st.form("new_alert"):
            alert_symbol = st.text_input("Symbole", value=symbol if symbol else "2222.SR").upper()
            exchange, country, currency = get_exchange_info(alert_symbol)
            st.caption(f"📍 {exchange} | {currency}")
            
            default_price = float(current_price * 1.05) if current_price > 0 else 32.5
            alert_price = st.number_input(
                f"Prix cible ({currency})", 
                min_value=0.01, 
                step=1.0, 
                value=default_price
            )
            
            col_cond, col_type = st.columns(2)
            with col_cond:
                condition = st.selectbox("Condition", ["above (au-dessus)", "below (en-dessous)"])
                condition = condition.split()[0]
            with col_type:
                alert_type = st.selectbox("Type", ["Permanent", "Une fois"])
            
            one_time = alert_type == "Une fois"
            
            if st.form_submit_button("Créer l'alerte"):
                st.session_state.price_alerts.append({
                    'symbol': alert_symbol,
                    'price': alert_price,
                    'condition': condition,
                    'one_time': one_time,
                    'currency': currency,
                    'country': country,
                    'created': datetime.now(USER_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success(f"✅ Alerte créée pour {alert_symbol} à {alert_price} {currency}")
    
    with col2:
        st.markdown("### 📋 Alertes actives")
        if st.session_state.price_alerts:
            for i, alert in enumerate(st.session_state.price_alerts):
                with st.container():
                    currency = alert.get('currency', get_currency(alert['symbol']))
                    st.markdown(f"""
                    <div class='alert-box alert-warning'>
                        <b>{alert['symbol']}</b> - {alert['condition']} {alert['price']:.2f} {currency}<br>
                        <small>{alert.get('country', '')} | Créée: {alert['created']} | {('Usage unique' if alert['one_time'] else 'Permanent')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Supprimer", key=f"del_alert_{i}"):
                        st.session_state.price_alerts.pop(i)
                        st.rerun()
        else:
            st.info("Aucune alerte active")

# ============================================================================
# SECTION 4: NOTIFICATIONS EMAIL
# ============================================================================
elif menu == "📧 Notifications email":
    st.subheader("📧 Configuration des notifications email")
    
    with st.form("email_config"):
        enabled = st.checkbox("Activer les notifications email", value=st.session_state.email_config['enabled'])
        
        col1, col2 = st.columns(2)
        with col1:
            smtp_server = st.text_input("Serveur SMTP", value=st.session_state.email_config['smtp_server'])
            smtp_port = st.number_input("Port SMTP", value=st.session_state.email_config['smtp_port'])
        
        with col2:
            email = st.text_input("Adresse email", value=st.session_state.email_config['email'])
            password = st.text_input("Mot de passe", type="password", value=st.session_state.email_config['password'])
        
        test_email = st.text_input("Email de test (optionnel)")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("💾 Sauvegarder"):
                st.session_state.email_config = {
                    'enabled': enabled,
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port,
                    'email': email,
                    'password': password
                }
                st.success("Configuration sauvegardée !")
        
        with col_btn2:
            if st.form_submit_button("📨 Tester"):
                if test_email:
                    if send_email_alert(
                        "Test de notification",
                        f"<h2>Test réussi !</h2><p>Votre configuration email fonctionne correctement !</p><p>Heure d'envoi: {datetime.now(USER_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} (heure Paris)</p>",
                        test_email
                    ):
                        st.success("Email de test envoyé !")
                    else:
                        st.error("Échec de l'envoi")
    
    with st.expander("📋 Aperçu de la configuration"):
        st.json(st.session_state.email_config)

# ============================================================================
# SECTION 5: EXPORT DES DONNÉES
# ============================================================================
elif menu == "📤 Export des données":
    st.subheader("📤 Export des données")
    
    if hist is not None and not hist.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Données historiques")
            display_hist = hist.copy()
            display_hist.index = display_hist.index.strftime('%Y-%m-%d %H:%M:%S (heure Paris)')
            st.dataframe(display_hist.tail(20))
            
            csv = hist.to_csv()
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"{symbol}_data_{datetime.now(USER_TIMEZONE).strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown("### 📈 Rapport PDF")
            st.info("Génération de rapport PDF (simulée)")
            
            st.markdown("**Statistiques:**")
            stats = {
                'Moyenne': hist['Close'].mean(),
                'Écart-type': hist['Close'].std(),
                'Min': hist['Close'].min(),
                'Max': hist['Close'].max(),
                'Variation totale': f"{(hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100:.2f}%" if len(hist) > 1 else "N/A"
            }
            
            for key, value in stats.items():
                if isinstance(value, float):
                    st.write(f"{key}: {format_arab_currency(value, symbol)}")
                else:
                    st.write(f"{key}: {value}")
            
            exchange, country, currency = get_exchange_info(symbol)
            json_data = {
                'symbol': symbol,
                'exchange': exchange,
                'country': country,
                'currency': currency,
                'last_update': datetime.now(USER_TIMEZONE).isoformat(),
                'timezone': 'Europe/Paris',
                'current_price': float(current_price) if current_price else 0,
                'statistics': {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in stats.items()},
                'data': hist.reset_index().to_dict(orient='records')
            }
            
            st.download_button(
                label="📥 Télécharger en JSON",
                data=json.dumps(json_data, indent=2, default=str),
                file_name=f"{symbol}_data_{datetime.now(USER_TIMEZONE).strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.warning(f"Aucune donnée à exporter pour {symbol}")

# ============================================================================
# SECTION 6: PRÉDICTIONS ML
# ============================================================================
elif menu == "🤖 Prédictions ML":
    st.subheader("🤖 Prédictions avec Machine Learning - Marchés Arabes")
    
    if hist is not None and not hist.empty and len(hist) > 30:
        st.markdown("### Modèle de prédiction (Régression polynomiale)")
        
        exchange, country, currency = get_exchange_info(symbol)
        
        st.info(f"""
        ⚠️ Facteurs influençant les marchés arabes ({country}):
        - Prix du pétrole (facteur clé pour les pays du Golfe)
        - Décisions de l'OPEP+ sur la production pétrolière
        - Taux d'intérêt et politique monétaire locales
        - Taux de change (USD/{currency})
        - Stabilité géopolitique de la région
        - Investissements étrangers et fonds souverains
        - Développement économique (Vision 2030, etc.)
        - Indices PMI et croissance économique
        - Inflation locale
        - Relations commerciales internationales
        - Tourisme et pèlerinage (selon les pays)
        - Météo et agriculture (pour certains pays)
        - Réformes économiques et diversification
        """)
        
        df_pred = hist[['Close']].reset_index()
        df_pred['Days'] = (df_pred['Date'] - df_pred['Date'].min()).dt.days
        
        X = df_pred['Days'].values.reshape(-1, 1)
        y = df_pred['Close'].values
        
        col1, col2 = st.columns(2)
        
        with col1:
            days_to_predict = st.slider("Jours à prédire", min_value=1, max_value=30, value=7)
            degree = st.slider("Degré du polynôme", min_value=1, max_value=5, value=2)
        
        with col2:
            show_confidence = st.checkbox("Afficher l'intervalle de confiance", value=True)
        
        model = make_pipeline(
            PolynomialFeatures(degree=degree),
            LinearRegression()
        )
        model.fit(X, y)
        
        last_day = X[-1][0]
        future_days = np.arange(last_day + 1, last_day + days_to_predict + 1).reshape(-1, 1)
        predictions = model.predict(future_days)
        
        last_date = df_pred['Date'].iloc[-1]
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_to_predict)]
        
        fig_pred = go.Figure()
        
        fig_pred.add_trace(go.Scatter(
            x=df_pred['Date'],
            y=y,
            mode='lines',
            name='Historique',
            line=dict(color='blue')
        ))
        
        fig_pred.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name='Prédictions',
            line=dict(color='red', dash='dash'),
            marker=dict(size=8)
        ))
        
        if show_confidence:
            residuals = y - model.predict(X)
            std_residuals = np.std(residuals)
            
            upper_bound = predictions + 2 * std_residuals
            lower_bound = predictions - 2 * std_residuals
            
            fig_pred.add_trace(go.Scatter(
                x=future_dates + future_dates[::-1],
                y=np.concatenate([upper_bound, lower_bound[::-1]]),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,0,0,0)'),
                name='Intervalle confiance 95%'
            ))
        
        fig_pred.update_layout(
            title=f"Prédictions pour {symbol} ({country}) - {days_to_predict} jours",
            xaxis_title="Date (heure Paris)",
            yaxis_title=f"Prix ({currency})",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_pred, use_container_width=True)
        
        st.markdown("### 📋 Prédictions détaillées")
        pred_df = pd.DataFrame({
            'Date': [d.strftime('%Y-%m-%d') for d in future_dates],
            'Prix prédit': [f"{p:.2f} {currency}" for p in predictions],
            'Variation %': [f"{(p/current_price - 1)*100:.2f}%" for p in predictions]
        })
        st.dataframe(pred_df, use_container_width=True)
        
        st.markdown("### 📊 Performance du modèle")
        residuals = y - model.predict(X)
        mse = np.mean(residuals**2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(residuals))
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("RMSE", f"{rmse:.2f} {currency}")
        col_m2.metric("MAE", f"{mae:.2f} {currency}")
        col_m3.metric("R²", f"{model.score(X, y):.3f}")
        
        st.markdown("### 📈 Analyse des tendances")
        last_price = current_price
        last_pred = predictions[-1]
        trend = "HAUSSIÈRE 📈" if last_pred > last_price else "BAISSIÈRE 📉" if last_pred < last_price else "NEUTRE ➡️"
        
        if last_pred > last_price * 1.05:
            strength = "Forte tendance haussière 🚀"
        elif last_pred > last_price:
            strength = "Légère tendance haussière 📈"
        elif last_pred < last_price * 0.95:
            strength = "Forte tendance baissière 🔻"
        elif last_pred < last_price:
            strength = "Légère tendance baissière 📉"
        else:
            strength = "Tendance latérale ⏸️"
        
        st.info(f"**Tendance prévue:** {trend} - {strength}")
        
        with st.expander(f"🇸🇦🇦🇪🇶🇦 Facteurs influençant les marchés arabes"):
            st.markdown("""
            **Indicateurs économiques clés par région:**
            
            **Conseil de Coopération du Golfe (CCG):**
            - **Prix du pétrole** (Brent, WTI)
            - **Production OPEP+** et quotas
            - **Taux de change** (ancrage au dollar)
            - **Investissements étrangers** (FDI)
            - **Fonds souverains** (PIF, ADIA, QIA, KIA)
            - **Développement des infrastructures**
            - **Tourisme et aviation**
            - **Vision 2030** (Arabie Saoudite)
            - **Expo 2020 Dubai** (impact)
            - **Mondial 2022 Qatar** (héritage)
            
            **Afrique du Nord (Égypte, Maroc, Tunisie):**
            - **Agriculture** (saisonnière)
            - **Tourisme** (revenus)
            - **Envois de fonds** (diaspora)
            - **Réformes économiques** (FMI)
            - **Inflation et taux d'intérêt**
            - **Dette publique**
            - **Investissements du Golfe**
            
            **Levant (Jordanie, Liban, Palestine):**
            - **Stabilité politique**
            - **Aide internationale**
            - **Envois de fonds** (diaspora)
            - **Secteur bancaire**
            - **Reconstruction** (selon pays)
            
            **Secteurs clés:**
            - **Énergie**: Pétrole, gaz, pétrochimie
            - **Finance**: Banques islamiques et conventionnelles
            - **Immobilier**: Développement et construction
            - **Télécoms**: Mobile, internet, data
            - **Industrie**: Ciment, métaux, transformation
            - **Tourisme**: Hôtellerie, aviation, loisirs
            - **Agriculture**: Agroalimentaire
            - **Commerce**: Distribution, retail
            
            **Banques islamiques:**
            - Principes de la Charia
            - Interdiction de l'intérêt (Riba)
            - Partage des profits et pertes
            - Sukuk (obligations islamiques)
            - Actifs tangibles
            
            **Calendrier économique:**
            - **Décisions OPEP+**: Mensuelles
            - **Réunions banques centrales**: Selon pays
            - **Résultats semestriels**: Mars et Septembre
            - **Résultats annuels**: Décembre-Janvier
            - **Dividendes**: Généralement annuels
            - **Ramadan**: Horaires réduits, volatilité plus faible
            - **Eid al-Fitr/Eid al-Adha**: Fermeture des marchés
            
            **Particularités:**
            - Marchés fermés le vendredi
            - Influence des prix du pétrole
            - Forte corrélation avec les marchés US
            - Liquidité parfois plus faible
            - Rôle des family offices
            - Préférence pour les dividendes
            """)
        
    else:
        st.warning(f"Pas assez de données historiques pour {symbol} (minimum 30 points)")

# ============================================================================
# SECTION 7: INDICES ARABES
# ============================================================================
elif menu == "🇸🇦🇦🇪🇶🇦 Indices arabes":
    st.subheader("🇸🇦🇦🇪🇶🇦 Indices boursiers arabes")
    
    arab_indices = {
        # Saudi Arabia
        '^TASI.SR': 'Tadawul All Share Index (TASI) - السعودية',
        
        # UAE
        '^DFMGI.DU': 'Dubai Financial Market General Index (DFMGI) - دبي',
        '^ADI.AD': 'Abu Dhabi Securities Exchange Index (ADI) - أبوظبي',
        
        # Qatar
        '^QSI.QA': 'Qatar Stock Exchange Index - قطر',
        
        # Kuwait
        '^BKP.KW': 'Boursa Kuwait Premier Market Index - الكويت',
        
        # Egypt
        '^EGX30.CA': 'EGX 30 Index - مصر',
        '^EGX70.CA': 'EGX 70 Index - مصر',
        '^EGX100.CA': 'EGX 100 Index - مصر',
        
        # Morocco
        '^MASI.MA': 'Moroccan All Shares Index (MASI) - المغرب',
        '^MSI20.MA': 'MSI 20 Index - المغرب',
        
        # Jordan
        '^AMGNRLX.JO': 'Amman Stock Exchange General Index - الأردن',
        
        # Oman
        '^MSX30.OM': 'Muscat Stock Exchange Index - عمان',
        
        # Bahrain
        '^BAX.BH': 'Bahrain All Share Index - البحرين',
        
        # Tunisia
        '^TUNINDEX.TN': 'TUNINDEX - تونس',
        
        # Palestine
        '^PEX.PS': 'Palestine Exchange Index - فلسطين',
        
        # Lebanon
        '^BLOM.LB': 'Blom Stock Index - لبنان',
        
        # Pan-Arab
        '^S&P Pan Arab': 'S&P Pan Arab Composite Index',
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 🌍 Sélection d'indice")
        selected_index = st.selectbox(
            "Choisir un indice",
            options=list(arab_indices.keys()),
            format_func=lambda x: arab_indices[x],
            index=0
        )
        
        st.markdown("### 📊 Performance des indices")
        perf_period = st.selectbox(
            "Période de comparaison",
            options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"],
            index=0
        )
    
    with col1:
        try:
            if st.session_state.demo_mode:
                # Données simulées pour la démo
                st.markdown(f"### {arab_indices[selected_index]} (Mode démo)")
                
                if 'TASI' in selected_index:
                    current_index = random.uniform(11000, 12000)
                elif 'DFMGI' in selected_index:
                    current_index = random.uniform(3000, 3500)
                elif 'ADI' in selected_index:
                    current_index = random.uniform(9000, 9500)
                elif 'QSI' in selected_index:
                    current_index = random.uniform(10000, 10500)
                elif 'EGX30' in selected_index:
                    current_index = random.uniform(25000, 30000)
                elif 'MASI' in selected_index:
                    current_index = random.uniform(12000, 13000)
                else:
                    current_index = random.uniform(1000, 5000)
                
                prev_index = current_index * random.uniform(0.97, 1.03)
                index_change = current_index - prev_index
                index_change_pct = (index_change / prev_index * 100)
                
                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.metric("Valeur", f"{current_index:,.2f}")
                col_i2.metric("Variation", f"{index_change:,.2f}")
                col_i3.metric("Variation %", f"{index_change_pct:.2f}%", delta=f"{index_change_pct:.2f}%")
                
                # Générer un graphique simulé
                dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
                values = current_index * (1 + np.random.normal(0, 0.01, 100).cumsum() / 100)
                
                fig_index = go.Figure()
                fig_index.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines',
                    name=arab_indices[selected_index],
                    line=dict(color='#006C35', width=2)
                ))
                
                fig_index.update_layout(
                    title=f"Évolution simulée - {perf_period}",
                    xaxis_title="Date",
                    yaxis_title="Points",
                    height=500,
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_index, use_container_width=True)
                
            else:
                # Essayer de charger les données réelles
                index_ticker = selected_index
                if selected_index.startswith('^'):
                    index_ticker = selected_index[1:]  # Enlever le ^ pour yfinance
                
                ticker = yf.Ticker(index_ticker)
                index_hist = ticker.history(period=perf_period)
                
                if not index_hist.empty:
                    if index_hist.index.tz is None:
                        index_hist.index = index_hist.index.tz_localize('UTC').tz_convert(USER_TIMEZONE)
                    else:
                        index_hist.index = index_hist.index.tz_convert(USER_TIMEZONE)
                    
                    current_index = index_hist['Close'].iloc[-1]
                    prev_index = index_hist['Close'].iloc[-2] if len(index_hist) > 1 else current_index
                    index_change = current_index - prev_index
                    index_change_pct = (index_change / prev_index * 100) if prev_index != 0 else 0
                    
                    st.markdown(f"### {arab_indices[selected_index]}")
                    
                    col_i1, col_i2, col_i3 = st.columns(3)
                    col_i1.metric("Valeur", f"{current_index:,.2f}")
                    col_i2.metric("Variation", f"{index_change:,.2f}")
                    col_i3.metric("Variation %", f"{index_change_pct:.2f}%", delta=f"{index_change_pct:.2f}%")
                    
                    # Déterminer le pays pour le fuseau horaire
                    country_map = {
                        'TASI': 'Saudi Arabia',
                        'DFMGI': 'UAE',
                        'ADI': 'UAE',
                        'QSI': 'Qatar',
                        'BKP': 'Kuwait',
                        'EGX30': 'Egypt',
                        'MASI': 'Morocco',
                        'AMGNRLX': 'Jordan',
                        'MSX30': 'Oman',
                        'BAX': 'Bahrain',
                        'TUNINDEX': 'Tunisia',
                        'PEX': 'Palestine',
                        'BLOM': 'Lebanon',
                    }
                    
                    country = 'Saudi Arabia'
                    for key in country_map:
                        if key in selected_index:
                            country = country_map[key]
                            break
                    
                    if country in ARAB_TIMEZONES:
                        local_time = index_hist.index[-1].tz_convert(ARAB_TIMEZONES[country])
                        st.caption(f"Dernière mise à jour: {index_hist.index[-1].strftime('%Y-%m-%d %H:%M:%S')} (heure Paris) / {local_time.strftime('%H:%M:%S')} (heure locale {country})")
                    else:
                        st.caption(f"Dernière mise à jour: {index_hist.index[-1].strftime('%Y-%m-%d %H:%M:%S')} (heure Paris)")
                    
                    fig_index = go.Figure()
                    fig_index.add_trace(go.Scatter(
                        x=index_hist.index,
                        y=index_hist['Close'],
                        mode='lines',
                        name=arab_indices[selected_index],
                        line=dict(color='#006C35', width=2)
                    ))
                    
                    if len(index_hist) > 20:
                        ma_20 = index_hist['Close'].rolling(window=20).mean()
                        ma_50 = index_hist['Close'].rolling(window=50).mean()
                        
                        fig_index.add_trace(go.Scatter(
                            x=index_hist.index,
                            y=ma_20,
                            mode='lines',
                            name='MA 20',
                            line=dict(color='orange', width=1, dash='dash')
                        ))
                        
                        fig_index.add_trace(go.Scatter(
                            x=index_hist.index,
                            y=ma_50,
                            mode='lines',
                            name='MA 50',
                            line=dict(color='purple', width=1, dash='dash')
                        ))
                    
                    fig_index.update_layout(
                        title=f"Évolution - {perf_period}",
                        xaxis_title="Date",
                        yaxis_title="Points",
                        height=500,
                        hovermode='x unified',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_index, use_container_width=True)
                    
                    st.markdown("### 📈 Statistiques")
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    col_s1.metric("Plus haut", f"{index_hist['High'].max():,.2f}")
                    col_s2.metric("Plus bas", f"{index_hist['Low'].min():,.2f}")
                    col_s3.metric("Moyenne", f"{index_hist['Close'].mean():,.2f}")
                    col_s4.metric("Volatilité", f"{index_hist['Close'].pct_change().std()*100:.2f}%")
                else:
                    st.warning("Données non disponibles - Utilisation du mode démo")
                    st.session_state.demo_mode = True
        except Exception as e:
            st.error(f"Erreur lors du chargement: {e}")
            st.info("Utilisation du mode démonstration")
    
    # Tableau de comparaison des indices
    st.markdown("### 📊 Comparaison des principaux indices")
    
    comparison_data = []
    for idx, name in list(arab_indices.items())[:15]:  # Limiter à 15 pour la clarté
        try:
            if st.session_state.demo_mode:
                if 'TASI' in idx:
                    current = random.uniform(11000, 12000)
                elif 'DFMGI' in idx:
                    current = random.uniform(3000, 3500)
                elif 'ADI' in idx:
                    current = random.uniform(9000, 9500)
                elif 'QSI' in idx:
                    current = random.uniform(10000, 10500)
                elif 'EGX30' in idx:
                    current = random.uniform(25000, 30000)
                elif 'MASI' in idx:
                    current = random.uniform(12000, 13000)
                else:
                    current = random.uniform(1000, 5000)
                    
                prev = current * random.uniform(0.95, 1.05)
                change_pct = ((current - prev) / prev * 100)
                
                comparison_data.append({
                    'Indice': name.split(' - ')[0],
                    'Pays': name.split(' - ')[1] if ' - ' in name else 'N/A',
                    'Valeur': f"{current:,.0f}",
                    'Variation 5j': f"{change_pct:.2f}%",
                    'Direction': '📈' if change_pct > 0 else '📉' if change_pct < 0 else '➡️'
                })
            else:
                # Essayer de charger les données réelles
                index_ticker = idx
                if idx.startswith('^'):
                    index_ticker = idx[1:]
                
                ticker = yf.Ticker(index_ticker)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[0]
                    change_pct = ((current - prev) / prev * 100) if prev != 0 else 0
                    
                    comparison_data.append({
                        'Indice': name.split(' - ')[0],
                        'Pays': name.split(' - ')[1] if ' - ' in name else 'N/A',
                        'Valeur': f"{current:,.0f}",
                        'Variation 5j': f"{change_pct:.2f}%",
                        'Direction': '📈' if change_pct > 0 else '📉' if change_pct < 0 else '➡️'
                    })
        except:
            pass
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
    
    with st.expander("ℹ️ À propos des marchés arabes"):
        st.markdown("""
        ### Principales places financières du monde arabe
        
        **Conseil de Coopération du Golfe (CCG):**
        
        **🇸🇦 Arabie Saoudite - Tadawul:**
        - Plus grande bourse du monde arabe
        - Capitalisation: ~3 000 milliards $
        - Saudi Aramco: plus grande capitalisation mondiale
        - Réformes Vision 2030
        - Ouverture aux investisseurs étrangers depuis 2015
        - Indice TASI: 200+ sociétés
        - Nomad: marché pour les PME
        
        **🇦🇪 Émirats Arabes Unis:**
        - **DFM (Dubai):** 60+ sociétés, capitalisation ~100 milliards $
        - **ADX (Abu Dhabi):** 70+ sociétés, capitalisation ~500 milliards $
        - Fusion potentielle DFM-ADX en discussion
        - Secteurs clés: immobilier, finance, énergie
        
        **🇶🇦 Qatar - QSE:**
        - 45+ sociétés
        - Capitalisation: ~150 milliards $
        - QNB: plus grande banque du Moyen-Orient
        - Impact du Mondial 2022
        
        **🇰🇼 Koweït - Boursa Kuwait:**
        - 150+ sociétés
        - Marché Premier, Principal, Auction
        - Intégration aux indices MSCI Emerging Markets
        
        **Afrique du Nord:**
        
        **🇪🇬 Égypte - EGX:**
        - 200+ sociétés
        - Capitalisation: ~40 milliards $
        - EGX30: principales capitalisations
        - Réformes économiques et programme FMI
        
        **🇲🇦 Maroc - Casablanca Stock Exchange:**
        - 75+ sociétés
        - Capitalisation: ~60 milliards $
        - 2e bourse d'Afrique
                - MASI, MSI20, FTSE Morocco All-Liquid
        - Attijariwafa Bank: plus grande capitalisation
        
        **🇹🇳 Tunisie - BVMT:**
        - 80+ sociétés
        - Capitalisation: ~8 milliards $
        - TUNINDEX: indice principal
        - Secteurs: finance, industrie, services
        
        **Levant:**
        
        **🇯🇴 Jordanie - ASE:**
        - 150+ sociétés
        - Capitalisation: ~20 milliards $
        - Arab Bank: plus grande capitalisation
        - Secteurs: finance, industrie, services
        
        **🇱🇧 Liban - BSE:**
        - 30+ sociétés (avant crise)
        - Capitalisation: ~10 milliards $ (avant crise)
        - Blom Bank, Bank Audi, Solidere
        - Impact de la crise économique depuis 2019
        
        **🇵🇸 Palestine - PEX:**
        - 45+ sociétés
        - Capitalisation: ~4 milliards $
        - Bank of Palestine: plus grande capitalisation
        - Secteurs: finance, télécoms, immobilier
        
        **Caractéristiques communes:**
        - **Jours de trading:** Dimanche - Jeudi (sauf Maroc/Tunisie: Lundi - Vendredi)
        - **Horaires:** Généralement 10h-14h/15h (heure locale)
        - **Devises:** Ancrage au dollar pour la plupart des pays du Golfe
        - **Ramadan:** Horaires réduits (généralement 10h-13h)
        - **Dividendes:** Souvent annuels, parfois semestriels
        - **Liquidité:** Variable selon les marchés et les secteurs
        
        **Spécificités des marchés arabes:**
        - **Finance islamique:** Banques conformes à la Charia
        - **Sukuk:** Obligations islamiques
        - **Family offices:** Influence des grandes familles
        - **Fonds souverains:** PIF (SA), ADIA (UAE), QIA (Qatar), KIA (Koweït)
        - **Investisseurs étrangers:** Participation croissante
        - **Volatilité:** Liée aux prix du pétrole et géopolitique
        
        **Calendrier hebdomadaire typique:**
        - **Dimanche:** Ouverture des marchés du Golfe
        - **Lundi:** Ouverture des marchés nord-africains
        - **Jeudi:** Clôture des marchés du Golfe
        - **Vendredi:** Tous les marchés fermés (jour de prière)
        - **Samedi:** Marchés du Golfe fermés, Maroc/Tunisie ouverts
        
        **Périodes de fermeture:**
        - **Eid al-Fitr:** 3-5 jours (fin du Ramadan)
        - **Eid al-Adha:** 3-5 jours (Fête du Sacrifice)
        - **Journée nationale:** Variable selon les pays
        - **Nouvel an islamique:** 1 jour
        - **Mawlid:** Naissance du Prophète (variable)
        """)

# ============================================================================
# WATCHLIST ET DERNIÈRE MISE À JOUR
# ============================================================================
st.markdown("---")
col_w1, col_w2 = st.columns([3, 1])

with col_w1:
    st.subheader("📋 Watchlist Marchés Arabes")
    
    # Regrouper les actions par pays
    saudi_stocks = [s for s in st.session_state.watchlist if s.endswith('.SR')]
    uae_stocks = [s for s in st.session_state.watchlist if s.endswith('.DU') or s.endswith('.AD')]
    qatar_stocks = [s for s in st.session_state.watchlist if s.endswith('.QA')]
    kuwait_stocks = [s for s in st.session_state.watchlist if s.endswith('.KW')]
    egypt_stocks = [s for s in st.session_state.watchlist if s.endswith('.CA')]
    morocco_stocks = [s for s in st.session_state.watchlist if s.endswith('.MA')]
    other_arab_stocks = [s for s in st.session_state.watchlist if any(s.endswith(suf) for suf in ['.JO', '.OM', '.BH', '.TN', '.PS', '.LB'])]
    
    tabs = st.tabs(["🇸🇦 Saudi", "🇦🇪 UAE", "🇶🇦 Qatar", "🇰🇼 Kuwait", "🇪🇬 Egypt", "🇲🇦 Morocco", "🇯🇴🇴🇲🇧🇭 Autres"])
    
    with tabs[0]:  # Saudi Arabia
        if saudi_stocks:
            cols_per_row = 3
            for i in range(0, len(saudi_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(saudi_stocks) - i))
                for j, sym in enumerate(saudi_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode and sym in DEMO_DATA:
                                price = DEMO_DATA[sym]['current_price']
                                prev_close = DEMO_DATA[sym]['previous_close']
                                change = ((price - prev_close) / prev_close * 100)
                                st.metric(sym, f"{price:.2f} SAR", delta=f"{change:.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.2f} SAR", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(20, 100)
                            st.metric(sym, f"{price:.2f} SAR*", delta=f"{random.uniform(-2, 2):.1f}%")
        else:
            st.info("Aucune action saoudienne")
    
    with tabs[1]:  # UAE
        if uae_stocks:
            cols_per_row = 3
            for i in range(0, len(uae_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(uae_stocks) - i))
                for j, sym in enumerate(uae_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode:
                                price = random.uniform(5, 50)
                                st.metric(sym, f"{price:.2f} AED", delta=f"{random.uniform(-2, 2):.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.2f} AED", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(5, 50)
                            st.metric(sym, f"{price:.2f} AED*", delta=f"{random.uniform(-2, 2):.1f}%")
        else:
            st.info("Aucune action émiratie")
    
    with tabs[2]:  # Qatar
        if qatar_stocks:
            cols_per_row = 3
            for i in range(0, len(qatar_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(qatar_stocks) - i))
                for j, sym in enumerate(qatar_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode and sym in DEMO_DATA:
                                price = DEMO_DATA[sym]['current_price']
                                prev_close = DEMO_DATA[sym]['previous_close']
                                change = ((price - prev_close) / prev_close * 100)
                                st.metric(sym, f"{price:.2f} QAR", delta=f"{change:.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.2f} QAR", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(10, 30)
                            st.metric(sym, f"{price:.2f} QAR*", delta=f"{random.uniform(-2, 2):.1f}%")
        else:
            st.info("Aucune action qatarie")
    
    with tabs[3]:  # Kuwait
        if kuwait_stocks:
            cols_per_row = 3
            for i in range(0, len(kuwait_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(kuwait_stocks) - i))
                for j, sym in enumerate(kuwait_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode:
                                price = random.uniform(0.5, 2)
                                st.metric(sym, f"{price:.3f} KWD", delta=f"{random.uniform(-2, 2):.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.3f} KWD", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(0.5, 2)
                            st.metric(sym, f"{price:.3f} KWD*", delta=f"{random.uniform(-2, 2):.1f}%")
        else:
            st.info("Aucune action koweïtienne")
    
    with tabs[4]:  # Egypt
        if egypt_stocks:
            cols_per_row = 3
            for i in range(0, len(egypt_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(egypt_stocks) - i))
                for j, sym in enumerate(egypt_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode and sym in DEMO_DATA:
                                price = DEMO_DATA[sym]['current_price']
                                prev_close = DEMO_DATA[sym]['previous_close']
                                change = ((price - prev_close) / prev_close * 100)
                                st.metric(sym, f"{price:.2f} EGP", delta=f"{change:.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.2f} EGP", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(20, 100)
                            st.metric(sym, f"{price:.2f} EGP*", delta=f"{random.uniform(-3, 3):.1f}%")
        else:
            st.info("Aucune action égyptienne")
    
    with tabs[5]:  # Morocco
        if morocco_stocks:
            cols_per_row = 3
            for i in range(0, len(morocco_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(morocco_stocks) - i))
                for j, sym in enumerate(morocco_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode and sym in DEMO_DATA:
                                price = DEMO_DATA[sym]['current_price']
                                prev_close = DEMO_DATA[sym]['previous_close']
                                change = ((price - prev_close) / prev_close * 100)
                                st.metric(sym, f"{price:.2f} MAD", delta=f"{change:.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    st.metric(sym, f"{price:.2f} MAD", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            price = random.uniform(200, 1000)
                            st.metric(sym, f"{price:.2f} MAD*", delta=f"{random.uniform(-2, 2):.1f}%")
        else:
            st.info("Aucune action marocaine")
    
    with tabs[6]:  # Other Arab countries
        if other_arab_stocks:
            cols_per_row = 3
            for i in range(0, len(other_arab_stocks), cols_per_row):
                cols = st.columns(min(cols_per_row, len(other_arab_stocks) - i))
                for j, sym in enumerate(other_arab_stocks[i:i+cols_per_row]):
                    with cols[j]:
                        try:
                            if st.session_state.demo_mode:
                                price = random.uniform(1, 10)
                                if sym.endswith('.JO'):
                                    st.metric(sym, f"{price:.3f} JOD", delta=f"{random.uniform(-2, 2):.1f}%")
                                elif sym.endswith('.OM'):
                                    st.metric(sym, f"{price:.3f} OMR", delta=f"{random.uniform(-2, 2):.1f}%")
                                elif sym.endswith('.BH'):
                                    st.metric(sym, f"{price:.3f} BHD", delta=f"{random.uniform(-2, 2):.1f}%")
                                elif sym.endswith('.TN'):
                                    st.metric(sym, f"{price:.3f} TND", delta=f"{random.uniform(-2, 2):.1f}%")
                                elif sym.endswith('.PS'):
                                    st.metric(sym, f"{price:.3f} JOD", delta=f"{random.uniform(-2, 2):.1f}%")
                                elif sym.endswith('.LB'):
                                    st.metric(sym, f"{price:,.0f} LBP", delta=f"{random.uniform(-5, 5):.1f}%")
                                else:
                                    st.metric(sym, f"{price:.2f}", delta=f"{random.uniform(-2, 2):.1f}%")
                            else:
                                ticker = yf.Ticker(sym)
                                hist = ticker.history(period='1d')
                                if not hist.empty:
                                    price = hist['Close'].iloc[-1]
                                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else price
                                    change = ((price - prev_close) / prev_close * 100)
                                    _, _, currency = get_exchange_info(sym)
                                    st.metric(sym, f"{price:.2f} {currency}", delta=f"{change:.1f}%")
                                else:
                                    st.metric(sym, "N/A")
                        except:
                            st.metric(sym, "N/A*", delta="0%")
        else:
            st.info("Aucune action des autres pays arabes")

with col_w2:
    # Horaires actuels dans différents pays
    paris_time = datetime.now(USER_TIMEZONE)
    riyadh_time = datetime.now(ARAB_TIMEZONES['Saudi Arabia'])
    dubai_time = datetime.now(ARAB_TIMEZONES['UAE'])
    doha_time = datetime.now(ARAB_TIMEZONES['Qatar'])
    cairo_time = datetime.now(ARAB_TIMEZONES['Egypt'])
    casablanca_time = datetime.now(ARAB_TIMEZONES['Morocco'])
    
    st.markdown("### 🕐 Heures locales")
    st.caption(f"🇫🇷 Paris: {paris_time.strftime('%H:%M:%S')}")
    st.caption(f"🇸🇦 Riyad: {riyadh_time.strftime('%H:%M:%S')}")
    st.caption(f"🇦🇪 Dubaï: {dubai_time.strftime('%H:%M:%S')}")
    st.caption(f"🇶🇦 Doha: {doha_time.strftime('%H:%M:%S')}")
    st.caption(f"🇪🇬 Le Caire: {cairo_time.strftime('%H:%M:%S')}")
    st.caption(f"🇲🇦 Casablanca: {casablanca_time.strftime('%H:%M:%S')}")
    
    st.markdown("### 📊 Statuts des marchés")
    market_statuses = get_all_markets_status()
    for country, status_info in list(market_statuses.items())[:8]:  # Afficher les 8 premiers
        flag = {
            'Saudi Arabia': '🇸🇦',
            'UAE': '🇦🇪',
            'Qatar': '🇶🇦',
            'Kuwait': '🇰🇼',
            'Egypt': '🇪🇬',
            'Morocco': '🇲🇦',
            'Jordan': '🇯🇴',
            'Tunisia': '🇹🇳',
            'Oman': '🇴🇲',
            'Bahrain': '🇧🇭',
        }.get(country, '🌍')
        st.caption(f"{flag} {country}: {status_info['icon']} {status_info['status']}")
    
    if st.session_state.demo_mode:
        st.caption("🎮 Mode démonstration")
    else:
        st.caption(f"Dernière MAJ: {paris_time.strftime('%H:%M:%S')}")
    
    if auto_refresh and hist is not None and not hist.empty:
        time.sleep(refresh_rate)
        st.rerun()

# Note sur le Ramadan
current_date = datetime.now()
ramadan_2024_start = datetime(2024, 3, 10)  # Approximatif
ramadan_2024_end = datetime(2024, 4, 9)  # Approximatif

if ramadan_2024_start <= current_date <= ramadan_2024_end:
    st.markdown("""
    <div style='background-color: #fef3c7; border-left: 4px solid #d97706; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;'>
        <b>🌙 Ramadan Mubarak</b> - Horaires réduits sur les marchés arabes (généralement 10h-13h heure locale).
        La liquidité peut être plus faible que d'habitude.
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "🕌 Tracker Bourse Arabe - Marchés du Moyen-Orient et d'Afrique du Nord | "
    "🇸🇦 Tadawul | 🇦🇪 DFM/ADX | 🇶🇦 QSE | 🇰🇼 Boursa Kuwait | 🇪🇬 EGX | 🇲🇦 Casablanca | 🇯🇴 ASE | 🇹🇳 BVMT<br>"
    "📅 Horaires: Dimanche-Jeudi (Golfe) | Lundi-Vendredi (Maroc/Tunisie) | Fermé le vendredi<br>"
    "⚠️ Données avec délai possible | 🕐 Heure Paris | 🌙 Calendrier Hijri disponible"
    "</p>",
    unsafe_allow_html=True
)

# Pied de page avec les informations sur le calendrier islamique
with st.expander("📅 Calendrier islamique et jours fériés 2024 (approximatif)"):
    st.markdown("""
    | Date | Événement | Pays concernés |
    |------|-----------|----------------|
    | 10-12 avril 2024 | Eid al-Fitr (fin du Ramadan) | Tous les pays arabes |
    | 15-17 juin 2024 | Eid al-Adha (Fête du Sacrifice) | Tous les pays arabes |
    | 7 juillet 2024 | Nouvel an islamique (1446 AH) | Tous les pays arabes |
    | 15 septembre 2024 | Mawlid (Naissance du Prophète) | Variable selon les pays |
    | 23 septembre 2024 | Fête nationale | Arabie Saoudite |
    | 2-3 décembre 2024 | Fête nationale | Émirats Arabes Unis |
    | 18 décembre 2024 | Fête nationale | Qatar |
    | 25-26 février 2024 | Fête nationale | Koweït |
    | 25 janvier 2024 | Révolution | Égypte |
    | 30 juillet 2024 | Fête du Trône | Maroc |
    | 25 mai 2024 | Indépendance | Jordanie |
    | 20 mars 2024 | Indépendance | Tunisie |
    | 18 novembre 2024 | Fête nationale | Oman |
    | 16-17 décembre 2024 | Fête nationale | Bahreïn |
    | 15 novembre 2024 | Indépendance | Palestine |
    | 22 novembre 2024 | Indépendance | Liban |
    
    *Note: Les dates des fêtes religieuses sont approximatives et dépendent de l'observation de la lune.*
    """)

# Message de bienvenue en arabe
st.markdown("""
<div style='text-align: center; font-family: Amiri; font-size: 1.2rem; margin-top: 1rem;'>
    <p>بورصة العرب - تتبع الأسواق المالية العربية في الوقت الفعلي</p>
    <p>استثمر بذكاء في أسواق المنطقة</p>
</div>
""", unsafe_allow_html=True)
