# Fire Risk Assessment Script

from bs4 import BeautifulSoup
import datetime, json, re, requests

_DEBUG_OUTPUT = False

# NIFC
_NIFC_URL = 'https://fsapps.nwcg.gov/psp/npsg/forecast/api/gaccs/8/latest-forecast'

_IGNORE_LIKE = ('For more information about',)
_REQUIRED__FIELDS = ('forecastId',
                   'forecastPublished',
                   'startDate',
                   'forecastResources',
                   'forecastFuels',
                   'forecastWeather')
_FORECAST_SUBSTITUTIONS = {'·         ': ''}
_RE_PREPAREDNESS = r'(.+)\s+[pP]reparedness\s[lL]evel\s+(.+)'
_RE_F_Z = r'(\d+)(.[\d]+)'

# SBC Fire
_SBC_FIRE_URL = 'https://sbcfire.com'
_RE_FIRE_DANGER = r'.+[fF]ire\s+[dD]anger\s?\:\s?(.+)'


preparedness = dict()
response = requests.get(_NIFC_URL)
if response:
    try:
        nifc = json.loads(response.text)
        if all(field in nifc for field in _REQUIRED__FIELDS):
            elements_pub = nifc['forecastPublished'].split('.')
            f_z = elements_pub[-1]
            f, z = 0, 0
            match = re.match(_RE_F_Z, f_z)
            if match and len(match.groups()) == 2:
                f, z = match.groups()
                f = int(f) if f.isdigit() else f
                z = int(z) if z[1:].isdigit() else z
            if z >= 0:
                raw_published = f'{elements_pub[0]}+{z:04}'
            else:
                _z = abs(z)
                raw_published = f'{elements_pub[0]}-{_z:04}'
            published = datetime.datetime.strptime(raw_published, '%Y%m%dT%H%M%S%z')
            str_published = str(published)
            soup = BeautifulSoup(nifc['forecastResources'], 'html.parser')
            for p in soup.findAll('p'):
                p_text = p.text
                p_text = p_text.strip()
                if p_text and not any(p_text.startswith(_) for _ in _IGNORE_LIKE):
                    match = re.match(_RE_PREPAREDNESS, p_text)
                    if match and len(match.groups()) == 2:
                        region, level = match.groups()
                        preparedness[region] = int(level)
        if _DEBUG_OUTPUT: 
            if preparedness:
                print('Preparedness Table:')
                for region in preparedness:
                    print(f' ·  {region}: {preparedness[region]}')
                print()
            print(f"-- Weather forecast for {nifc['startDate']}\n")
            soup = BeautifulSoup(nifc['forecastWeather'], 'html.parser')
            soup_text = soup.text.strip()
            for key in _FORECAST_SUBSTITUTIONS:
                soup_text = soup_text.replace(key, _FORECAST_SUBSTITUTIONS[key])
            print(soup_text)
            print(f'\n-- Published: {str_published}\n')
    except:
        pass

south_ops = preparedness['SouthOps'] if 'SouthOps' in preparedness else -1
print(f'The latest forecast shows the SouthOps Preparedness Level is {south_ops}.')

sbc_fire_danger = 'Unknown'
response = requests.get(_SBC_FIRE_URL)
if response:
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = soup.findAll('div', id='current-fire-information')
    if matches:
        for match in matches:
            match_text = match.text.replace('\n', '').replace('\r', '').strip()
            match_danger = re.match(_RE_FIRE_DANGER, match_text.strip())
            if match_danger and match_danger.groups():
                sbc_fire_danger = match_danger.groups()[0].title()

print(f"SBC Fire assesses the fire danger as {sbc_fire_danger}.")

_DANGER_IMAGE_PATHS = ('FireDangerStatusInformation-LOW-1.gif',
                       'FireDangerStatusInformation-MODERATE-1.gif',
                       'FireDangerStatusInformation-HIGH-1.gif',
                       'FireDangerStatusInformation-VERY-HIGH-1.gif',
                       )
def fire_danger_image_path(str_danger):
    danger_words = str_danger.upper().split()
    if 'EXTREME' in danger_words:
        return 'FireDangerStatusInformation-EXTREME-1.gif'
    elif all(word in danger_words for word in ('VERY', 'HIGH')):
        return 'FireDangerStatusInformation-EXTREME-1.gif'
    elif 'HIGH' in danger_words:
        return 'FireDangerStatusInformation-HIGH-1.gif'
    elif 'MODERATE' in danger_words:
        return 'FireDangerStatusInformation-MODERATE-1.gif'
    elif 'LOW' in danger_words:
        return 'FireDangerStatusInformation-LOW-1.gif'
    else:
        return 'Question_mark.jpg'

sbc_danger_path = fire_danger_image_path(sbc_fire_danger)
print(f'Filename for danger image: {sbc_danger_path}')
    
    
    
