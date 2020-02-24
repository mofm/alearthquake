import configparser
import re
import smtplib
import ssl
from datetime import datetime

import requests
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('./alearthquake1.ini')

r = requests.get('http://www.koeri.boun.edu.tr/scripts/lst0.asp')

c = r.content

soup = BeautifulSoup(c, 'html.parser')
main_content = soup.pre.get_text()
lines = main_content.splitlines()


def ktimestamp():
    for nr, i in enumerate(lines):
        if nr == 7:
            amma = i.split()
            date_string = '%sT%s' % ((amma[0]), (amma[1]))
            format_date = datetime.strptime(date_string, '%Y.%m.%dT%H:%M:%S')
            lastquake = format_date.timestamp()

    with open(config['tracker']['tracker_file'], 'r+') as f:
        last = float(f.readline())
        if last == lastquake:
            exit()
        else:
            f.seek(0)
            f.write('%s' % lastquake)
            f.truncate()
            return last


def lastquake_line(lastquake):
    dt_convert = datetime.fromtimestamp(lastquake)
    dt_format = datetime.strftime(dt_convert, '%Y.%m.%d %H:%M:%S', )
    dt_pattern = re.compile('^%s.*' % dt_format)
    for nr, i in enumerate(lines):
        if dt_pattern.search(i):
            return nr


def bycoordinates(latitude, longitude, magnitude, lastline=506):
    la_pattern = re.compile('^(%s.*)\s(%s)' % (latitude, longitude))
    for nr, i in enumerate(lines):
        if 7 <= nr <= lastline:
            i_split = i.split()
            new_line = i_split[2] + ' ' + i_split[3]
            if la_pattern.search(new_line) and float(i_split[6]) >= magnitude:
                print(i)


def byregion(region, magnitude, lastline=506):
    rg_pattern = re.compile('.*(%s).*' % region)
    for nr, i in enumerate(lines):
        if 7 <= nr <= lastline:
            i_split = i.split()
            new_line = i_split[8] + ' ' + i_split[9]
            if rg_pattern.search(new_line) and float(i_split[6]) >= magnitude:
                print(i)


def send_notification():
    message = """\
Subject: Hi there

This message is sent from Python."""
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config['mail']['smtp_server'], config['mail']['port']) as server:
            server.starttls(context=context)
            server.login(config['mail']['username'], config['mail']['password'])
            server.sendmail(config['notification']['sender_mail'], config['notification']['receiver_mail'], message)
            print('Success')
    except Exception as e:
        print(e)
    finally:
        server.quit()


a = ktimestamp()
lastquake_line(a)