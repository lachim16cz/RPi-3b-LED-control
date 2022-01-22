Před úplně prvním spuštěním nastav souboru chmod:
chmod a+x akvarium.py

Nastav v nastavení:
Preference -> Rpi configuration -> interfaces -> 1-Wire Enabled



Po každém restartování Rpi napiš příkaz do terminálu:
sudo pigpiod



saved_data [
automatické světlo 	| 1 / 0
stmívání		| 1 / 0
délka stmívání		| 3 - 3600 (sekundy)
síla světla		| 0 - 255
start světla		| 0 - 24 (hodiny)
start světla		| 0 - 59 (minuty)
délka svícení		| 0 - 23 (hodiny)
voda vyměněna		| datum
]
