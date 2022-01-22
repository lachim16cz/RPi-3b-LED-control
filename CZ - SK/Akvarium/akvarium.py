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

# Výchozí nastavení aplikace
array_saved_data = ["0","0",30,255,0,0,0,"none"]

# Kontrola uložených dat
try:
    settings_data = pickle.load(open("data/settings.dat","rb"))
except(OSError, IOError) as e:
    pickle.dump(array_saved_data, open("data/settings.dat","wb"))
    settings_data = array_saved_data



# Aktualizuje hodiny mimo hlavní aplikaci
def update_watch():
    ts = calendar.timegm(time.gmtime())
    hodiny = int(ts) + 1

    ts_date_time = datetime.fromtimestamp(hodiny)
    hodiny_write = ts_date_time.strftime("%H:%M:%S")
    title_fill.value = hodiny_write
    actual_seconds_count = ts_date_time.strftime("%S"); 

# Spustí okno aplikace
app = App(height=400, width=630, title="Akvárium", bg="#333333")

# Spustí software pro kontrolu LED
pi = pigpio.pi()

# Nastaví současný čas
now_time = datetime.now()


# Nastaví maximální jas
max_brightness = settings_data[3]

# Nastaví čas pro rožnutí / zhasnutí
fade_seconds = settings_data[2]
fade_time = float(fade_seconds / max_brightness)

# Definuje čas rožnutí (hodiny + minuty)
start_light1 = settings_data[4]
start_light2 = settings_data[5]



###### Funkce aplikace ######
# Mění jas LED osvětlení
def update_brightness(power):
    pi.set_PWM_dutycycle(21,power)

# Postupné stmívání LED
def fade_down():
    count2 = int(max_brightness)
    while count2 >= 0:
        update_brightness(count2)
        count2 -= 1
        time.sleep(fade_time)
    set_timer_up()

# Okamžité zhasnutí LED
def timer_light_down():
    update_brightness(0)
    set_timer_up()

# Aktivuje automatické smtmívání LED
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
        print("Zhasnuti dalsi den")
            
    else:
        new_timer2 = new_time.replace(day=new_time.day,hour=end_time_hour,minute=settings_data[5],second=0,microsecond=0)
        delta_t2 = new_timer2 - new_time;
        secs2 = delta_t2.total_seconds()
        timer_f2 = Timer(secs2, typ_roznuti)
        timer_f2.start()
        print("Zhasnuti")

# Postupné rožnutí LED
def fade_up():
    count = int(0)
    while count < max_brightness + 1:
        update_brightness(count)
        count += 1
        time.sleep(fade_time)
    timer_down()
    

# Okamžité rožnutí LED na nastavenou hodnotu
def basic_light_up():
    update_brightness(max_brightness)
    light_up_image_set.value = "img/light_down.png"
    light_up_image_set.when_mouse_leaves = light_down
def timer_basic_light_up():
    update_brightness(max_brightness)
    timer_down()
    
# Okamžité rožnutí na maximální hodnotu
def max_light_up():
    update_brightness(255)
    light_up_image.value = "img/light_down.png"
    light_up_image.when_mouse_leaves = light_down

# Zhasnutí LED
def light_down():
    update_brightness(0)
    light_up_image.value = "img/light_up.png"
    light_up_image.when_mouse_enters = max_light_up
    
    light_up_image_set.value = "img/set_light.png"
    light_up_image_set.when_mouse_enters = basic_light_up  

# Aktivace časového rožnutí LED
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
    print("Roznuti")

# Kontroluje a nastavuje kdy se mají LED rožnout
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
                print("Roznuti dalsi den")

            
# Uložení data výměny vody     
def save_water_change():
    actual_time_water_change = datetime.now()
    
    date_to_save = actual_time_water_change.strftime("%d.%m.%Y")
    settings_data[7] = date_to_save
    last_water_text.value = date_to_save
    pickle.dump(settings_data, open("data/settings.dat","wb"))



###### Nastavení viditelností uživatelského rozhraní ######
# Výchozí obrazovka
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

# Nastavení
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

# Intenzita osvětlení
def set_light_power():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Intenzita osvětlení"
    rozklik_slider_power.visible = True   

# Automatické světlo
def set_auto_light():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Automatické světlo"
    rozklik_auto_checkbox.visible = True
    nadpis_auto1.visible = True
    rozklik_auto_power.visible = True
    rozklik_auto_power2.visible = True
    rozklik_auto_power3.visible = True
    nadpis_auto2.visible = True
    nadpis_auto3.visible = True

# Efekt stmívání 
def set_fade():
    settings_box.visible = False
    ok_button.visible = True
    cancle_button.visible = True
    rozklik_box.visible = True
    home_image.visible = False
    
    title_set.value = "Efekt stmívání"
    rozklik_stmivani_checkbox.visible = True
    nadpis_stmivani.visible = True
    rozklik_stmivani_power.visible = True
    
    
# Tlačítko zrušit  
def cancle_set():
    settings_screen()
    # Intenzita osvětlení
    rozklik_slider_power.value=settings_data[3]
    rozklik_slider_power.visible = False
    # Automatické světlo
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
    # Efekt stmívání  
    rozklik_stmivani_checkbox.value = settings_data[1]
    rozklik_stmivani_checkbox.visible = False
    nadpis_stmivani.visible = False
    rozklik_stmivani_power.value=settings_data[2]
    rozklik_stmivani_power.visible = False
 
# Uložit nastavení
def save_set():
    settings_screen()
    # Intenzita osvětlení
    settings_data[3] = rozklik_slider_power.value
    # Automatické světlo
    settings_data[0] = rozklik_auto_checkbox.value
    settings_data[4] = rozklik_auto_power.value
    settings_data[5] = rozklik_auto_power2.value
    settings_data[6] = rozklik_auto_power3.value
    # Efekt stmívání  
    settings_data[1] = rozklik_stmivani_checkbox.value
    settings_data[2] = rozklik_stmivani_power.value

    
    # Uloží nastavení do souboru
    pickle.dump(settings_data, open("data/settings.dat","wb"))
    
    # Restartuje program
    os.execl(sys.executable, sys.executable,* sys.argv)
 

###### Uživatelské rozhraní ###### 
# Horní řádek
title_box = Box(app, width="fill", align="top")
title_fill = Text(title_box, text="", color="white", align='right')

hodiny = now_time.strftime("%H:%M:%S")
title_fill.value = hodiny
title_fill.repeat(1000,update_watch)

home_image = Picture(title_box, image="img/home.png", width=20, height=20, align="left")
home_image.when_mouse_enters = normal_screen
home_image.visible = False


# Obsah
content_box = Box(app, align="top", width="fill")

# Box nastavení
rozklik_box = Box(content_box, align="top", width="fill")
rozklik_box.visible = False
title_set = Text(rozklik_box, text="", color="white", size=15)
Text(rozklik_box,text=" ",size=10,color="black")

# Nastavení intenzity osvětlení     
rozklik_slider_power = Slider(rozklik_box, start=0, end=255,width="fill")
rozklik_slider_power.value=settings_data[3]
rozklik_slider_power.bg = "white"
rozklik_slider_power.visible = False

# Nastavení automatického svícení
rozklik_auto_checkbox = CheckBox(rozklik_box, text="Světlo")
rozklik_auto_checkbox.bg="white"
rozklik_auto_checkbox.value = settings_data[0]
rozklik_auto_checkbox.visible = False

nadpis_auto1 = Text(rozklik_box,text="Začátek svícení (h)",size=12,color="white")
nadpis_auto1.visible = False
rozklik_auto_power = Slider(rozklik_box, start=0, end=23,width="fill")
rozklik_auto_power.value=settings_data[4]
rozklik_auto_power.bg = "white"
rozklik_auto_power.visible = False

nadpis_auto2 = Text(rozklik_box,text="Začátek svícení (m)",size=12,color="white")
nadpis_auto2.visible = False
rozklik_auto_power2 = Slider(rozklik_box, start=0, end=59,width="fill")
rozklik_auto_power2.value=settings_data[5]
rozklik_auto_power2.bg = "white"
rozklik_auto_power2.visible = False

nadpis_auto3 = Text(rozklik_box,text="Délka svícení (h)",size=12,color="white")
nadpis_auto3.visible = False
rozklik_auto_power3 = Slider(rozklik_box, start=1, end=23,width="fill")
rozklik_auto_power3.value=settings_data[6]
rozklik_auto_power3.bg = "white"
rozklik_auto_power3.visible = False

# Nastavení efektu stmívání
rozklik_stmivani_checkbox = CheckBox(rozklik_box, text="Stmívání")
rozklik_stmivani_checkbox.bg="white"
rozklik_stmivani_checkbox.value = settings_data[1]
rozklik_stmivani_checkbox.visible = False

nadpis_stmivani = Text(rozklik_box,text="Doba efektu stmívání (s)",size=12,color="white")
nadpis_stmivani.visible = False
rozklik_stmivani_power = Slider(rozklik_box, start=3, end=3600,width="fill")
rozklik_stmivani_power.value=settings_data[2]
rozklik_stmivani_power.bg = "white"
rozklik_stmivani_power.visible = False


# Tlačítka v nastavení
settings_box = Box(content_box,align="top",width="150")
settings_box.visible = False
Text(settings_box,text="Nastavení",size=15,color="white")
Text(settings_box,text=" ",size=5,color="black")
auto_light_button = PushButton(settings_box,text="Automatické světlo", command=set_auto_light, width="fill")
auto_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")
power_light_button = PushButton(settings_box,text="Intenzita osvětlení", command=set_light_power, width="fill")
power_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")
fade_light_button = PushButton(settings_box,text="Efekt stmívání", command=set_fade, width="fill")
fade_light_button.bg = "white"
Text(settings_box,text=" ",size=2,color="black")

button_box = Box(app, width="fill", align="bottom")
ok_button = PushButton(button_box,text="Uložit", command=save_set, align='right')
ok_button.bg = "white"
ok_button.visible = False
cancle_button = PushButton(button_box,text="Zrušit", command=cancle_set, align='right')
cancle_button.bg = "white"
cancle_button.visible = False

# Výchozí rozhraní
display_box = Box(content_box, layout='grid', width="100", align="top")

if settings_data[0] == 1:
    set_timer_up() # Aktivace světla
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


# Datum výměny vody
water_box = Box(content_box, layout='grid', width="100", align="top")
last_water_img = Picture(water_box, grid=[0,0], image="img/water_changed.png", width=15, height=15)
if settings_data[7] == "none":
    voda_vymenena = " Voda ještě nebyla vyměněna"
else:
    voda_vymenena = settings_data[7]
    
last_water_text = Text(water_box, grid=[1,0], text=voda_vymenena, color="white", align="left")


# Dolní tlačítka
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