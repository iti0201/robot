# PiBot dokumentatsioon

## Roboti objekti loomine

Iga programmi alguses tuleb import-ida roboti klass ja luua selle objekt:

```python
from PiBot import PiBot
robot = PiBot()
```

Kõik funktsioonid tuleb välja kutsuda selle objekti kaudu.

## Roboti juhtimise funktsioonid

Järgmised 3 funktsiooni panevad vastavalt kas vasaku või parema või mõlema ratta kiiruseks argumendina kaasa antud protsendi maksimaalsest kiirusest. Protsendid, mis sobivad, on vahemikus -99 kuni 99. Kui tahetakse tagurpidi liikuda, peab protsent olema negatiivne. Robot hakkab liikuma alates kiiruse protsendist 8 (ligikaudne).

```python
set_left_wheel_speed(percentage)
set_right_wheel_speed(percentage)
set_wheels_speed(percentage)
```

**Näide.** Teeme roboti objekti ja paneme ta paariks sekundiks otse sõitma

```python
from PiBot import PiBot

robot = PiBot()

robot.set_wheels_speed(30)
robot.sleep(2)
robot.set_wheels_speed(0)
```

## Koodrid

Järgmised kaks funktsiooni tagastavad vastavalt kas parema või vasaku ratta koodri väärtuse ehk mitu kraadi on ratas pöörelnud programmi algusest peale. Kooder tagastab väärtuse täisarvuna. Kui sõita edaspidi, suureneb väärtus, kui sõita tagurpidi, väheneb väärtus.

```python
get_right_wheel_encoder()
get_left_wheel_encoder()
```

## Roboti sensorite uuendamine
Roboti sensoreid uuendatakse automaatselt iga 5 millisekundi tagant. Uuendamise ajale saab ligi läbi klassimuutuja `UPDATE_TIME`.

## Roboti eespoolsed lasersensorid
Roboti eespoolsed (see pool, kus on käpp) lasersensorid mõõdavad kaugust vahemikus 10 – 200 cm. Järgmised 3 funktsiooni tagastavad vastavalt vasaku, keskmise ja parema lasersensori väärtuse meetrites. Viimane funktsioon tagastab järjendi kõigist eespoolsetest infrapunasensorite väärtustest samas järjekorras nagu enne loetleti.

```python
get_front_left_laser()
get_front_middle_laser()
get_front_right_laser()

get_front_lasers()
```

## Roboti tagumised infrapunasensorid
Tagumised infrapunasensorid mõõdavad kaugust vahemikus 2 kuni 16 cm. Mida lähemal on takistus või sein, seda suurem on anduri lugem. Kui anduri lugem muutub ajas väiksemaks, siis robot liigub takistusest kaugemale.
Järgmised 3 funktsiooni tagastavad vastavalt tagumise (see pool, kus pole käppa) vasakpoolse otsevaatava, diagonaalselt vaatava ja küljele vaatava infrapunasensori väärtused infrapunaandurite mõõtühikutes, millel puudub otsene ja alati kehtiv teisendus meetriteks. 

```python
get_rear_left_straight_ir()
get_rear_left_diagonal_ir()
get_rear_left_side_ir()
```

Järgmised 3 funktsiooni tagastavad vastavalt tagumise parempoolse otsevaatava, diagonaalselt vaatava ja küljele vaatava infrapunasensori väärtused.

```python
get_rear_right_straight_ir()
get_rear_right_diagonal_ir()
get_rear_right_side_ir()
```

**NB! See tähendab, et te ei saa neid väärtusi otse kasutada vaid peate anduri väärtust ajas võrdlema. Näiteks, kui parempoolne andur annab väärtuse `x` ja mingi aja pärast on see väärtus `1.5 * x`, siis võib järeldada, et robot liigub seinale lähemale. Selle info põhjal võib roboti asendit korrigeerida rohkem vasakule, et püsida seinast esialgsel kaugusel.**

Olemas on ka n-ö mugavusfunktsioonid. Alljärgnevatest funktsioonidest esimene tagastab kõikide tagumiste infrapunasensorite väärtused järjendis juba loetletud järjekorras. Teine funktsioon tagastab kõikide kaugussensorite väärtused järjendis eespoolt alustades loetletud järjekorras.

```python
get_rear_irs()
get_distance_sensors()
```

## Roboti joonejärgimise sensorid
Roboti joonejärgimissensorid asuvad roboti all eespool (käpa all). Need tagastavad väärtusi vahemikus 0 kuni 1024, kus 1024 on kõige intensiivsem ehk valgem värv ja 0 kõige vähem intensiivsem ehk kõige mustem värv. Praktikas tagastavad sensorid musta värvi korral umbes 100 ja valge värvi korral umbes 900.
Järgmised 3 funktsiooni tagastavad vastavalt kõige vasakpoolsema, vasakult teise ja vasakult kolmanda ehk vasakpoolse keskmise sensori väärtused.

```python
get_leftmost_line_sensor()
get_second_line_sensor_from_left()
get_third_line_sensor_from_left()
```

Järgmised 3 funktsiooni tagastavad vastavalt kõige parempoolsema, paremalt teise ja paremalt kolmanda ehk parempoolse keskmise sensori väärtused.

```python
get_rightmost_line_sensor()
get_second_line_sensor_from_right()
get_third_line_sensor_from_right()
```

Vastavalt eeltoodud järjekorrale saab ka küsida joonejärgimissensorite väärtusi grupiti järgmiste käskudega:
```python
get_left_line_sensors()
get_right_line_sensors()
get_line_sensors()
```

## Roboti suund
Robotilt saab küsida järgmise funktsiooniga, mitu kraadi on ta pööranud algseisundi suhtes.
```python
get_rotation()
```

## Roboti käpa juhtimine
Käppa saab liigutada üles ja alla ning lahti ja kinni.
Järgmine funktsioon liigutab käppa üles ja alla. Argumendiks sobib arv vahemikus 0 kuni 100, kus 0 on kõige madalam käpa kõrgus ja 100 on kõige kõrgem.

```python
set_grabber_height(height_percentage)
```

Järgmine funktsioon liigutab käppa lahti ja kinni. Argumendiks sobib jälle arv vahemikus 0 kuni 100, kus 0 on käpa kõige lahtisem olek ja 100 on käpa kõige kinnisem olek.

```python
close_grabber(percentage)
```
## Roboti kaamera
Roboti kaameral põhineva robotnägemisalgoritmi väljundit on võimalik lugeda meetodiga:

```
get_camera_objects()
```

Antud meetod tagastab järjendi tuvastatud objektidega (algoritm tuvastab ainult sfääre) järgmisel kujul: `[(objekti tüüp, (keskkoha x koordinaat, keskkoha y koordinaat), objekti raadius), ...]`. Kaamera teljestik algab vasakult ülevalt ning x-telg on paremale ja y-telg on alla.

## Konstandid
PiBoti klassis on defineeritud arvutuste jaoks vajalikud konstandid. Roboti ratta diameeter meetrites on kirjas klassimuutujas `WHEEL_DIAMETER` ja roboti telje pikkus meetrites on klassimuutujas `AXIS_LENGTH`. Kaamera pisklite arvud on kirjas klassimuutujas `CAMERA_RESOLUTION` (laius, pikkus). Kaamera vaatevälja laiused on kirjas klassimuutujas `CAMERA_FIELD_OF_VIEW` (horisontaalne laius kraadides, vertikaalne laius kraadides).

## Ootele jäämine - sleep(duration)

Programmi tööd saab "pausile" panna, kasutades `sleep(duration)` käsku. Argument on aeg sekundites.

### Näide

```
from PiBot import PiBot

# Create a robot instance
robot = PiBot()

print("Good news...")
robot.sleep(2)
print("everyone!")
```

## Kas oled simulatsioonis
Robotilt saab küsida ka, kas kood jookseb simulatsioonis või mitte meetodiga `is_simulation()`.

### Näide

```
from PiBot import PiBot

# Create a robot instance
robot = PiBot()

if robot.is_simulation():
    # Running in simulation
    speed = 15
else:
    # Running in real life
    speed = 20
```

## Ajatempli lugemine - get_time()

Ajaga tegevuste (nt taimeri) jaoks on võimalik kasutada `get_time()` funktsiooni. Funktsioon tagastab simulaatoris mitu sekundit on möödunud simulatsiooni algusest. Päris robotil tagastab funktsioon mitu sekundit on möödunud 1970. aasta 1. jaanuari keskööst.

### Näide

```
from PiBot import PiBot

# Create a robot instance
robot = PiBot()

start_time = robot.get_time()
print("Time at start is {}".format(start_time))
while start_time + 5.0 > robot.get_time():
    print("Well, I'm doing something...")
    robot.sleep(1)
print("I did something for 5 seconds!")
print("Time at end is {}".format(robot.get_time()))
```
```
Time at start is 9.859
Well, I'm doing something...
Well, I'm doing something...
Well, I'm doing something...
Well, I'm doing something...
Well, I'm doing something...
I did something for 5 seconds!
Time at end is 14.859
```

# Roboti programmi näide
```python
from PiBot import PiBot

# Create a robot instance
robot = PiBot()

# Get distance from object using the front middle IR sensor
distance_from_object = robot.get_front_middle_laser()

# Drive towards object
robot.set_wheels_speed(30)
while distance_from_object > 0.2:
    distance_from_object = robot.get_front_middle_laser()
    robot.sleep(0.05)
    
# Stop the robot when done
robot.set_wheels_speed(0)
```
