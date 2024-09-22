from turtle import *
import turtle
from tkinter import *

setup(1000,1000)
setworldcoordinates(-500,-500,500,500)
tracer(0,0)

# Inititiate turtle screen
wn = turtle.Screen()

# Inititate turd
turd = turtle.Turtle()
turd.speed(0)
turd.penup()

# Instantiations
_BACKGROUND_COLOR = 'powder blue'
_FILL_COLOR = 'orange'
_SUN_RADIUS = '80'
_SUN_COLOR = 'orange'
_LAWN_COLOR = 'green'
_HOUSE_COLOR = 'Peru'
_ROOF_COLOR = 'firebrick'
_PEN_COLOR = 'black'
_SML_MT_COLOR = 'grey'
_LG_MT_COLOR = 'light grey'
_DOOR_COLOR = 'saddle brown'
_DOORKNOB_COLOR = 'orange'
# Set screen background color
wn.bgcolor(_BACKGROUND_COLOR)

# Define rectangle function
def rectangle(width, height, color):
    turd.pendown()
    turd.color(color)
    turd.begin_fill()
    for i in range (2):
        turd.forward(width)
        turd.right(90)
        turd.forward(height)
        turd.right(90)
    turd.end_fill()
    turd.penup()
    return None

# Define isosceles triangle 
def IsoscelesTriangle(x,y,width,height,direction,c):
    up()
    goto(x,y)
    seth(direction-90)
    fd(width/2)
    p1x, p1y = xcor(), ycor() # first point: bottom right
    back(width)
    p2x, p2y = xcor(), ycor() # second point: bottom left
    goto(x,y)
    seth(direction)
    fd(height)
    p3x, p3y = xcor(), ycor() # third point: top
    goto(p1x,p1y)
    down()
    fillcolor(c)
    begin_fill()
    goto(p2x,p2y)
    goto(p3x,p3y)
    goto(p1x,p1y)
    end_fill()

# Define circle function
def circle(radius, extent, color): 
    turd.pendown()
    turd.color(_PEN_COLOR, _FILL_COLOR)
    turd.begin_fill()
    turd.circle(radius)
    turd.end_fill()
    turd.penup()
    return None

# Draw the sun
turd.goto(-400, 300)
circle(80, None, _SUN_COLOR)

# Draw lawn
turd.goto(-700, -530)
turd.pendown()
rectangle(1400, -300, _LAWN_COLOR)

# Draw mountains
IsoscelesTriangle(200, -300, 900, 500, 90, _LG_MT_COLOR)
IsoscelesTriangle(-200, -300, 900, 400, 90, _SML_MT_COLOR)

# Draw house
turd.goto(490, -300)
turd.seth(180)
rectangle(350, 250, _HOUSE_COLOR)

#Draw roof onto house
IsoscelesTriangle(320, -50, 400, 90, 90, _ROOF_COLOR)

# Draw door & doorknob
turd.goto(230, -300)
rectangle(75, 150, _DOOR_COLOR) # door
turd.goto(170, -230)
circle(7, None, _DOORKNOB_COLOR) # doorknob

# Draw window
turd.goto(340, -230)
rectangle(80, 80, 'cyan')   # Window glass
turd.goto(302, -230)
rectangle(3, 80, 'black')   # Vertical window frame
turd.goto(340, -193)
rectangle(80, 3, 'black')   # Hrz window frame

# Sign posts
turd.goto(-300,-400)        # left
rectangle(20,180, '#763b10')
turd.goto(-158, -400)       # right
rectangle(20,180, '#763b10') 


# House light polygon
turd.goto(122.5, -147.5)
turd.fillcolor("gold")
turd.begin_fill()
for i in range(6):
  turd.forward(12)
  turd.right(60)
turd.end_fill() # Draws septagonal bulb
turd.goto(155, -120)
rectangle(40, 5, 'dim gray') 
IsoscelesTriangle(118,-130,30,12,90,'dim gray') #Light fixture



################################################################################

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

def fire_danger_image_path(str_danger):
    danger_words = str_danger.upper().split()
    if 'EXTREME' in danger_words:
        return 'EXTREME.gif'
    elif all(word in danger_words for word in ('VERY', 'HIGH')):
        return 'VERY_HIGH.gif'
    elif 'HIGH' in danger_words:
        return 'HIGH.gif'
    elif 'MODERATE' in danger_words:
        return 'MODERATE.gif'
    elif 'LOW' in danger_words:
        return 'LOW.gif'
    else:
        return 'QUESTION_MARK.jpg'

sbc_danger_path = fire_danger_image_path(sbc_fire_danger)
# print(f'Filename for danger image: {sbc_danger_path}')

from turtle import Screen, Shape

wn.register_shape(sbc_danger_path)
fire_turtle = Turtle(sbc_danger_path)
fire_turtle.penup()
fire_turtle.goto(-240,-200)
fire_turtle.stamp()


