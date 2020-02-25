""" This script sends mail notifications about last earthquakes"""
import configparser
import re
import smtplib
import ssl
from datetime import datetime

import requests
from bs4 import BeautifulSoup

CONFIG = configparser.ConfigParser()
CONFIG.read('./alearthquake1.ini')

REQ = requests.get('http://www.koeri.boun.edu.tr/scripts/lst0.asp')

CON = REQ.content

SOUP = BeautifulSoup(CON, 'html.parser')
MAIN_CONTENT = SOUP.pre.get_text()
LINES = MAIN_CONTENT.splitlines()


def ktimestamp():
    """check new earthquake time from KOERI and compare last checked timestamp(tracker file)."""
    for nr1, i in enumerate(LINES):
        if nr1 == 7:
            amma = i.split()
            date_string = '%sT%s' % ((amma[0]), (amma[1]))
            format_date = datetime.strptime(date_string, '%Y.%m.%dT%H:%M:%S')
            lastquake = format_date.timestamp()

    with open(CONFIG['tracker']['tracker_file'], 'r+') as file:
        last = float(file.readline())
        if last != lastquake:
            file.seek(0)
            file.write('%s' % lastquake)
            file.truncate()
            print(last)


def lastquake_line(lastquake):
    """find previously checked last line"""
    dt_convert = datetime.fromtimestamp(lastquake)
    dt_format = datetime.strftime(dt_convert, '%Y.%m.%d %H:%M:%S', )
    dt_pattern = re.compile('^%s.*' % dt_format)
    for nr2, i in enumerate(LINES):
        if dt_pattern.search(i):
            return nr2
        return None


def bycoordinates(latitude, longitude, magnitude, lastline=506):
    """find last earthquakes by coordinates"""
    la_pattern = re.compile(r'^(%s.*)\s(%s)' % (latitude, longitude))
    for nr3, i in enumerate(LINES):
        if 7 <= nr3 <= lastline:
            i_split = i.split()
            new_line = i_split[2] + ' ' + i_split[3]
            if la_pattern.search(new_line) and float(i_split[6]) >= magnitude:
                print(i)


def byregion(region, magnitude, lastline=506):
    """find last earthquakes by region"""
    rg_pattern = re.compile('.*(%s).*' % region)
    for nr4, i in enumerate(LINES):
        if 7 <= nr4 <= lastline:
            i_split = i.split()
            new_line = i_split[8] + ' ' + i_split[9]
            if rg_pattern.search(new_line) and float(i_split[6]) >= magnitude:
                print(i)


def send_notification():
    """mail notification function"""
    message = """\
Subject: Hi there

This message is sent from Python."""
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(CONFIG['mail']['smtp_server'], CONFIG['mail']['port']) as server:
            server.starttls(context=context)
            server.login(CONFIG['mail']['username'], CONFIG['mail']['password'])
            server.sendmail(CONFIG['notification']['sender_mail'], CONFIG['notification']['receiver_mail'], message)
            print('Success')
    except Exception as exp:
        print(exp)
    finally:
        server.quit()
