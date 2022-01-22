#coding=utf-8
import pigpio
import time
import calendar
from datetime import datetime, timedelta
from threading import Timer
import pickle
import os
import sys


from guizero import App, Text, TextBox, PushButton, Slider, Picture, Box, CheckBox

# Default application settings
array_saved_data = ["0","0",30,255,0,0,0,"none"]

# Check for saved settings
try:
    settings_data = pickle.load(open("data/settings.dat","rb"))
except(OSError, IOError) as e:
    pickle.dump(array_saved_data, open("data/settings.dat","wb"))
    settings_data = array_saved_data



# Updates the clock outside the application
def update_watch():
    ts = calendar.timegm(time.gmtime())
    hodiny = int(ts) + 1

    ts_date_time = datetime.fromtimestamp(hodiny)
    hodiny_write = ts_date_time.strftime("%H:%M:%S")
    title_fill.value = hodiny_write
    actual_seconds_count = ts_date_time.strftime("%S"); 

# Run window app
app = App(height=400, width=630, title="Aquarium", bg="#333333")

# Run LED control software
pi = pigpio.pi()

# Set current time
now_time = datetime.now()


# Set max brightness
max_brightness = settings_data[3]

# Set time for dimming / lighting up
fade_seconds = settings_data[2]
fade_time = float(fade_seconds / max_brightness)

# Set time for lighting up (hours + minutes)
start_light1 = settings_data[4]
start_light2 = settings_data[5]



###### App functions ######
# Changes the brightness of the LED light
def update_brightness(power):
    pi.set_PWM_dutycycle(21,power)

# Gradual dimming of light
def fade_down():
    count2 = int(max_brightness)
    while count2 >= 0:
        update_brightness(count2)
        count2 -= 1
        time.sleep(fade_time)
    set_timer_up()

# Immediate power off of the light
def timer_light_down():
    update_brightness(0)
    set_timer_up()

# Activates automatic light off
def timer_down():
    if settings_data[1] == 0:
        typ_roznuti = timer_light_down
    else:
        typ_roznuti = fade_down
         
    new_time = datetime.now()    
    end_time_hour = settings_data[6] + settings_data[4]
        
    if end_time_hour >= 24:
        
        end_next_day = end_time_hour - 24
        
        new_timer2 = new_time.replace(day=new_time.day,hour=end_time_hour,minute=settings_data[5],second=0,microsecond=0) + timedelta(days=1)
        delta_t2 = new_timer2 - new_time;
        secs2 = delta_t2.total_seconds()
        timer_f2 = Timer(secs2, typ_roznuti)
        timer_f2.start()
        print("Light off - next day")
            
    else:
        new_timer2 = new_time.replace(day=new_time.day,hour=end_time_hour,minute=settings_data[5],second=0,microsecond=0)
        delta_t2 = new_timer2 - new_time;
        secs2 = delta_t2.total_seconds()
        timer_f2 = Timer(secs2, typ_roznuti)
        timer_f2.start()
        print("Light off")

# Gradual light on
def fade_up():
    count = int(0)
    while count < max_brightness + 1:
        update_brightness(count)
        count += 1
        time.sleep(fade_time)
    timer_down()
    

# Immediate switching on of the light to the set value
def basic_light_up():
    update_brightness(max_brightness)
    light_up_image_set.value = "img/light_down.png"
    light_up_image_set.when_mouse_leaves = light_down
def timer_basic_light_up():
    update_brightness(max_brightness)
    timer_down()
    
# Immediate switching on of the light on maximum value
def max_light_up():
    update_brightness(255)
    light_up_image.value = "img/light_down.png"
    light_up_image.when_mouse_leaves = light_down

# Power off LED lights   
def light_down():
    update_brightness(0)
    light_up_image.value = "img/light_up.png"
    light_up_image.when_mouse_enters = max_light_up
    
    light_up_image_set.value = "img/set_light.png"
    light_up_image_set.when_mouse_enters = basic_light_up  

# Activation of timed light on
def timer_up():
    if settings_data[1] == 0:
        typ_roznuti = timer_basic_light_up
    else:
        typ_roznuti = fade_up
     
    new_time = datetime.now() 
    new_timer = new_time.replace(day=new_time.day,hour=start_light1,minute=start_light2,second=0,microsecond=0)
    delta_t = new_timer - new_time;
    secs = delta_t.total_seconds()
    timer_f = Timer(secs, typ_roznuti)
    timer_f.start()
    print("Light on")

# Check when the lights go on
def set_timer_up():
    new_time = datetime.now()
    start_time = new_time.replace(hour=settings_data[4], minute=settings_data[5], second=0, microsecond=0)
    
    if start_time >= new_time:
        
        timer_up()
        
    elif start_time < new_time:
        start_plus_doba = settings_data[6] + settings_data[4]
        
        if start_plus_doba >= 24:
            timer_up()
            
        else:
            end_time = new_time.replace(hour=start_plus_doba, minute=settings_data[5], second=0, microsecond=0)
            if new_time < end_time:
                timer_up()
            else:
                if settings_data[1] == 0:
                    typ_roznuti = timer_basic_light_up
                else:
                    typ_roznuti = fade_up
        
                new_timer = new_time.replace(day=new_time.day,hour=start_light1,minute=start_light2,second=0,microsecond=0) + timedelta(days=1)
                delta_t = new_timer - new_time;
                secs = delta_t.total_seconds()
                timer_f = Timer(secs, typ_roznuti)
                timer_f.start()
                print("Light on - next day")

            
# Save date when water was changed        
def save_water_change():
    actual_time_water_change = datetime.now()
    
    date_to_save = actual_time_water_change.strftime("%d.%m.%Y")
    settings_data[7] = date_to_save
    last_water_text.value = date_to_save
    pickle.dump(settings_data, open("data/settings.dat","wb"))



###### User interface visible settings ######
# Default view
def normal_screen():
    display_box.visible = True
    water_box.visible = True
    mezera_mezi_uvod.visible = True
    light_up_image.visible = True
    light_up_image_set.visible = True
    white_space_water_change.visible = True
    water_changed_img.visible = True
    settings_image.visible = True
    home_image.visible = False
    settings_box.visible = False
    ok_button.visible = False
    cancle_button.visible = False
    rozklik_box.visible = False

# Settings
def settings_screen():
    display_box.visible = False
    water_box.visible = False
    mezera_mezi_uvod.visible = False
    light_up_image.visible = False
    light_up_image_set.visible = False
    white_space_water_change.visible = False
    water_changed_img.visible = False
    settings_image.visible = False
    home_image.visible = True
    settings_box.visible = True
    ok_button.visible = False
    cancle_button.visible = False
    rozklik_box.visible = False

# Light brightness setting
def set_light_power():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Light brightness"
    rozklik_slider_power.visible = True   

# Automatic light on setting
def set_auto_light():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Automatic light"
    rozklik_auto_checkbox.visible = True
    nadpis_auto1.visible = True
    rozklik_auto_power.visible = True
    rozklik_auto_power2.visible = True
    rozklik_auto_power3.visible = True
    nadpis_auto2.visible = True
    nadpis_auto3.visible = True

# Fade effect setting    
def set_fade():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Fade effect"
    rozklik_stmivani_checkbox.visible = True
    nadpis_stmivani.visible = True
    rozklik_stmivani_power.visible = True
    
    
# Cancle button    
def cancle_set():
    settings_screen()
    # Light brightness
    rozklik_slider_power.value=settings_data[3]
    rozklik_slider_power.visible = False
    # Automatic light
    rozklik_auto_checkbox.visible = False
    nadpis_auto1.visible = False
    rozklik_auto_power.value=settings_data[4]
    rozklik_auto_power.visible = False
    rozklik_auto_checkbox.value = settings_data[0]
    rozklik_auto_power2.value=settings_data[5]
    rozklik_auto_power2.visible = False
    rozklik_auto_power3.value=settings_data[6]
    rozklik_auto_power3.visible = False
    nadpis_auto2.visible = False
    nadpis_auto3.visible = False
    #Fade effect   
    rozklik_stmivani_checkbox.value = settings_data[1]
    rozklik_stmivani_checkbox.visible = False
    nadpis_stmivani.visible = False
    rozklik_stmivani_power.value=settings_data[2]
    rozklik_stmivani_power.visible = False
 
# Save settings 
def save_set():
    settings_screen()
    # Light brightness
    settings_data[3] = rozklik_slider_power.value
    # Automatic light
    settings_data[0] = rozklik_auto_checkbox.value
    settings_data[4] = rozklik_auto_power.value
    settings_data[5] = rozklik_auto_power2.value
    settings_data[6] = rozklik_auto_power3.value
    # Fade effect 
    settings_data[1] = rozklik_stmivani_checkbox.value
    settings_data[2] = rozklik_stmivani_power.value

    
    # Save the settings to a file
    pickle.dump(settings_data, open("data/settings.dat","wb"))
    
    # Restart program
    os.execl(sys.executable, sys.executable,* sys.argv)
 

###### User interface ###### 
# Top row
title_box = Box(app, width="fill", align="top")
title_fill = Text(title_box, text="", color="white", align='right')

hodiny = now_time.strftime("%H:%M:%S")
title_fill.value = hodiny
title_fill.repeat(1000,update_watch)

home_image = Picture(title_box, image="img/home.png", width=20, height=20, align="left")
home_image.when_mouse_enters = normal_screen
home_image.visible = False


# Content
content_box = Box(app, align="top", width="fill")

# Settings box
rozklik_box = Box(content_box, align="top", width="fill")
rozklik_box.visible = False
title_set = Text(rozklik_box, text="", color="white", size=15)
Text(rozklik_box,text=" ",size=10,color="black")

# Light brightness setting      
rozklik_slider_power = Slider(rozklik_box, start=0, end=255,width="fill")
rozklik_slider_power.value=settings_data[3]
rozklik_slider_power.bg = "white"
rozklik_slider_power.visible = False

# Automatic light setting
rozklik_auto_checkbox = CheckBox(rozklik_box, text="Light setting")
rozklik_auto_checkbox.bg="white"
rozklik_auto_checkbox.value = settings_data[0]
rozklik_auto_checkbox.visible = False

nadpis_auto1 = Text(rozklik_box,text="Start of lighting up (h)",size=12,color="white")
nadpis_auto1.visible = False
rozklik_auto_power = Slider(rozklik_box, start=0, end=23,width="fill")
rozklik_auto_power.value=settings_data[4]
rozklik_auto_power.bg = "white"
rozklik_auto_power.visible = False

nadpis_auto2 = Text(rozklik_box,text="Start of lighting up (m)",size=12,color="white")
nadpis_auto2.visible = False
rozklik_auto_power2 = Slider(rozklik_box, start=0, end=59,width="fill")
rozklik_auto_power2.value=settings_data[5]
rozklik_auto_power2.bg = "white"
rozklik_auto_power2.visible = False

nadpis_auto3 = Text(rozklik_box,text="Lighting length (h)",size=12,color="white")
nadpis_auto3.visible = False
rozklik_auto_power3 = Slider(rozklik_box, start=1, end=23,width="fill")
rozklik_auto_power3.value=settings_data[6]
rozklik_auto_power3.bg = "white"
rozklik_auto_power3.visible = False

# Fade effect setting
rozklik_stmivani_checkbox = CheckBox(rozklik_box, text="Stmívání")
rozklik_stmivani_checkbox.bg="white"
rozklik_stmivani_checkbox.value = settings_data[1]
rozklik_stmivani_checkbox.visible = False

nadpis_stmivani = Text(rozklik_box,text="Dimming effect time (s)",size=12,color="white")
nadpis_stmivani.visible = False
rozklik_stmivani_power = Slider(rozklik_box, start=3, end=3600,width="fill")
rozklik_stmivani_power.value=settings_data[2]
rozklik_stmivani_power.bg = "white"
rozklik_stmivani_power.visible = False


# Setting buttons
settings_box = Box(content_box,align="top",width="150")
settings_box.visible = False
Text(settings_box,text="Nastavení",size=15,color="white")
Text(settings_box,text=" ",size=5,color="black")
auto_light_button = PushButton(settings_box,text="Automatic light", command=set_auto_light, width="fill")
auto_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")
power_light_button = PushButton(settings_box,text="Light brightness", command=set_light_power, width="fill")
power_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")
fade_light_button = PushButton(settings_box,text="Fade effect", command=set_fade, width="fill")
fade_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")

button_box = Box(app, width="fill", align="bottom")
ok_button = PushButton(button_box,text="Save", command=save_set, align='right')
ok_button.bg = "white"
ok_button.visible = False
cancle_button = PushButton(button_box,text="Cancle", command=cancle_set, align='right')
cancle_button.bg = "white"
cancle_button.visible = False

# Default view box
display_box = Box(content_box, layout='grid', width="100", align="top")

if settings_data[0] == 1:
    set_timer_up() # Activate light function
    content_left1a = Picture(display_box, grid=[0,0], image="img/sun.png", width=20, height=20)
    if settings_data[5] < 10:
        minuty_ukaz = "0" + str(settings_data[5])
    else:
        minuty_ukaz = str(settings_data[5])
    
    time_light_up = str(settings_data[4]) + ":" + minuty_ukaz
    content_left1b = Text(display_box, grid=[0,1], text=time_light_up, color="white")
    content_left1c = Text(display_box, grid=[0,2], text=str(settings_data[6])+"h", color="white")
else:
    content_left1a = Picture(display_box, grid=[0,0], image="img/moon.png", width=20, height=20)
    content_left1b = Text(display_box, grid=[0,1], text="Off", color="white")
    content_left1c = Text(display_box, grid=[0,2], text="", color="white")
 
Text(display_box, grid=[1,0], text=" ")
Text(display_box, grid=[1,1], text=" ")
Text(display_box, grid=[1,2], text=" ")

if settings_data[1] == 1:
    content_left2a = Picture(display_box, grid=[2,0], image="img/fade_up.png", width=20, height=20)
    fade_second = str(settings_data[2]) + "s"
    content_left2b = Text(display_box, grid=[2,1], text=fade_second, color="white")
    if settings_data[2] > 59:
        vypocet_minut = round(float(settings_data[2] / 60),1)
        content_left2c = Text(display_box, grid=[2,2], text="(" + str(vypocet_minut) + " m)", color="white")
else:
    content_left2a = Picture(display_box, grid=[2,0], image="img/fade_down.png", width=20, height=20)
    content_left2b = Text(display_box, grid=[2,1], text="Off", color="white")
    content_left2c = Text(display_box, grid=[2,2], text="", color="white")
    
Text(display_box, grid=[3,0], text=" ")
Text(display_box, grid=[3,1], text=" ")
Text(display_box, grid=[3,2], text=" ")    

content_left3a = Picture(display_box, grid=[4,0], image="img/set_light.png", width=20, height=20)
content_left3b = Text(display_box, grid=[4,1], text=settings_data[3], color="white")

mezera_mezi_uvod = Text(content_box,width="fill",text=" ",size=10)


# Water change date
water_box = Box(content_box, layout='grid', width="100", align="top")
last_water_img = Picture(water_box, grid=[0,0], image="img/water_changed.png", width=15, height=15)
if settings_data[7] == "none":
    voda_vymenena = " The water has not yet been changed"
else:
    voda_vymenena = settings_data[7]
    
last_water_text = Text(water_box, grid=[1,0], text=voda_vymenena, color="white", align="left")


# Bottom buttons
light_up_image = Picture(button_box, image="img/light_up.png", width=30, height=30, align="right")
light_up_image.when_mouse_enters = max_light_up

light_up_image_set = Picture(button_box, image="img/set_light.png", width=30, height=30, align="right")
light_up_image_set.when_mouse_enters = basic_light_up

white_space_water_change = Text(button_box, text="                         ", align="right")
water_changed_img = Picture(button_box, image="img/water_changed.png", width=30, height=30, align="right")
water_changed_img.when_mouse_enters = save_water_change

settings_image = Picture(button_box, image="img/settings.png", width=30, height=30, align="left")
settings_image.when_mouse_enters = settings_screen
    

app.display()