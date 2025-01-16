# This Python program uses the turtle graphics library to draw a whimsical cabin scene. It uses the BeautifulSoup library to scrape the National Interagency Fire Center (NIFC) and the Santa Barbara County Fire Department websites for the latest fire danger information. This draws our silly little scene with the fire danger level prented based on the information scraped from the NIFC and SBCFD.

# Setup imports
from turtle import *
import turtle
from tkinter import *

# Set up the screen
setup(1000,1000)
setworldcoordinates(-500,-500,500,500)
tracer(0,0)

# Inititiate turtle screen
wn = turtle.Screen()

# Initialize turtle
fyre_turtle = turtle.Turtle()
fyre_turtle.speed(0)
fyre_turtle.penup()

# Instantiations for colors and shapes
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
# @param width: width of rectangle
# @param height: height of rectangle
# @param color: color of rectangle
# @return None
def rectangle(width, height, color):
    fyre_turtle.pendown()
    fyre_turtle.color(color)
    fyre_turtle.begin_fill()
    for i in range (2):   # Draw rectangle
        fyre_turtle.forward(width)
        fyre_turtle.right(90)
        fyre_turtle.forward(height)
        fyre_turtle.right(90)
    fyre_turtle.end_fill()
    fyre_turtle.penup()
    return None

# Define isosceles triangle 
# @param x: x-coordinate of triangle
# @param y: y-coordinate of triangle
# @param width: width of triangle
# @param height: height of triangle
# @param direction: direction of triangle
# @param c: color of triangle
# @return None
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
# @param radius: radius of circle
# @param extent: extent of circle
# @param color: color of circle
# @return None
def circle(radius, extent, color): 
    fyre_turtle.pendown()
    fyre_turtle.color(_PEN_COLOR, _FILL_COLOR)
    fyre_turtle.begin_fill()
    fyre_turtle.circle(radius)
    fyre_turtle.end_fill()
    fyre_turtle.penup()
    return None

# Draw the sun
fyre_turtle.goto(-400, 300)
circle(80, None, _SUN_COLOR)

# Draw lawn
fyre_turtle.goto(-700, -530)
fyre_turtle.pendown()
rectangle(1400, -300, _LAWN_COLOR)

# Draw mountains
IsoscelesTriangle(200, -300, 900, 500, 90, _LG_MT_COLOR)
IsoscelesTriangle(-200, -300, 900, 400, 90, _SML_MT_COLOR)

# Draw house
fyre_turtle.goto(490, -300)
fyre_turtle.seth(180)
rectangle(350, 250, _HOUSE_COLOR)

#Draw roof onto house
IsoscelesTriangle(320, -50, 400, 90, 90, _ROOF_COLOR)

# Draw door & doorknob
fyre_turtle.goto(230, -300)
rectangle(75, 150, _DOOR_COLOR) # door
fyre_turtle.goto(170, -230)
circle(7, None, _DOORKNOB_COLOR) # doorknob

# Draw window
fyre_turtle.goto(340, -230)
rectangle(80, 80, 'cyan')   # Window glass
fyre_turtle.goto(302, -230)
rectangle(3, 80, 'black')   # Vertical window frame
fyre_turtle.goto(340, -193)
rectangle(80, 3, 'black')   # Hrz window frame

# Sign posts
fyre_turtle.goto(-300,-400)        # left
rectangle(20,180, '#763b10')
fyre_turtle.goto(-158, -400)       # right
rectangle(20,180, '#763b10') 


# House light polygon
fyre_turtle.goto(122.5, -147.5)
fyre_turtle.fillcolor("gold")
fyre_turtle.begin_fill()
for i in range(6):
  fyre_turtle.forward(12)
  fyre_turtle.right(60)
fyre_turtle.end_fill() # Draws septagonal bulb
fyre_turtle.goto(155, -120)
rectangle(40, 5, 'dim gray') 
IsoscelesTriangle(118,-130,30,12,90,'dim gray') #Light fixture



################################################################################

# Fire Risk Assessment Script

from bs4 import BeautifulSoup
import datetime, json, re, requests

_DEBUG_OUTPUT = True   # Set to False to disable debug output

# NIFC 
_NIFC_URL = 'https://fsapps.nwcg.gov/psp/npsg/forecast/api/gaccs/8/latest-forecast'


_IGNORE_LIKE = ('For more information about',)   # Ignore these lines

# Required fields constants & substitutions for NIFC data 
_REQUIRED__FIELDS = ('forecastId',
                   'forecastPublished',
                   'startDate',
                   'forecastResources',
                   'forecastFuels',
                   'forecastWeather')
_FORECAST_SUBSTITUTIONS = {'·         ': ''}

# Regex for NIFC data
# Extracts the preparedness level for a region
_RE_PREPAREDNESS = r'(.+)\s+[pP]reparedness\s[lL]evel\s+(.+)'
# Extracts the forecast date and time
_RE_F_Z = r'(\d+)(.[\d]+)'   

# SBC Fire 
_SBC_FIRE_URL = 'https://sbcfire.com'
# Regex for SBC Fire data - Extracts fire danger level
_RE_FIRE_DANGER = r'.+[fF]ire\s+[dD]anger\s?\:\s?(.+)' 

# Dictionary to store preparedness levels for each region
preparedness = dict()
response = requests.get(_NIFC_URL)   # Get NIFC data
if response:
    try:
        nifc = json.loads(response.text)   # Load JSON data
        if all(field in nifc for field in _REQUIRED__FIELDS):   # Check if all required fields are present  
            elements_pub = nifc['forecastPublished'].split('.')    # Extract forecast date and time
            f_z = elements_pub[-1]   # Extract the time zone
            f, z = 0, 0   # Initialize forecast date and time
            match = re.match(_RE_F_Z, f_z)   # Match the time zone
            if match and len(match.groups()) == 2:   # Check if match is found
                f, z = match.groups()   # Extract forecast date and time
                f = int(f) if f.isdigit() else f   # Convert to integer if it is a digit
                z = int(z) if z[1:].isdigit() else z   
            if z >= 0:  # Check if time zone is positive
                raw_published = f'{elements_pub[0]}+{z:04}'   # Format the date and time
            else:
                _z = abs(z)   
                raw_published = f'{elements_pub[0]}-{_z:04}' 
            published = datetime.datetime.strptime(raw_published, '%Y%m%dT%H%M%S%z')   # Convert to datetime object
            str_published = str(published)   # Convert datetime object to string
            soup = BeautifulSoup(nifc['forecastResources'], 'html.parser')   # Parse NIFC HTML data
            for p in soup.findAll('p'):   # Extract preparedness level for each region
                p_text = p.text   # Extract text
                p_text = p_text.strip()   # Strip whitespaces
                if p_text and not any(p_text.startswith(_) for _ in _IGNORE_LIKE):   # Check if text is not empty
                    match = re.match(_RE_PREPAREDNESS, p_text)   # Match preparedness level
                    if match and len(match.groups()) == 2:   # Check if match is found
                        region, level = match.groups()   # Extract region and preparedness level
                        preparedness[region] = int(level)   # Store preparedness level
        
        # Print preparedness table and weather forecast
        if _DEBUG_OUTPUT: 
            if preparedness:
                print('Preparedness Table:')
                for region in preparedness:
                    # Print preparedness level for each region
                    print(f' ·  {region}: {preparedness[region]}')
                print()
                # Print weather forecast
            print(f"-- Weather forecast for {nifc['startDate']}\n")
            soup = BeautifulSoup(nifc['forecastWeather'], 'html.parser')
            soup_text = soup.text.strip()
            for key in _FORECAST_SUBSTITUTIONS:
                soup_text = soup_text.replace(key, _FORECAST_SUBSTITUTIONS[key])
            print(soup_text)
            # Print forecast date and time
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

# Draw the fire danger image
from turtle import Screen, Shape

# Set up the screen
wn.register_shape(sbc_danger_path)
fire_turtle = Turtle(sbc_danger_path)
fire_turtle.penup()
fire_turtle.goto(-240,-200)
fire_turtle.stamp() # Stamp the fire danger image


