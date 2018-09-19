# PiBot dokumentatsioon

## Roboti objekti loomine

Iga programmi alguses tuleb import-ida roboti klass ja luua selle instants:

from PiBot import PiBot
robot = PiBot()

Kõik funktsioonid tuleb välja kutsuda selle instantsi kaudu.

## Roboti juhtimise funktsioonid

Järgmised 3 funktsiooni panevad vastavalt kas vasaku või parema või mõlema ratta kiiruseks argumendina kaasa antud protsendi maksimaalsest kiirusest. Protsendid, mis sobivad, on vahemikus -99 kuni 99. Kui tahetakse tagurpidi liikuda, peab protsent olema negatiivne. Robot hakkab liikuma alates kiiruse protsendist 15.

set_left_wheel_speed(percentage):
set_right_wheel_speed(percentage):
set_wheels_speed(percentage):

Järgmised kaks funktsiooni tagastavad vastavalt kas parema või vasaku ratta enkoodri väärtuse ehk mitu kraadi on ratas keerelnud programmi algusest peale. Enkoodrite täpsus on 1 kraad. Kui sõita ederpidi, suureneb väärtus, kui sõita tagurpidi, väheneb väärtus.

get_right_wheel_encoder():
get_left_wheel_encoder():

Näide. Teeme roboti objekti ja paneme ta paariks sekundiks otse sõitma
from PiBot import PiBot
import rospy

robot = PiBot()

robot.set_wheels_speed(30)
rospy.sleep(2)
robot.set_wheels_speed(0)

## Roboti sensorite uuendamine
Roboti sensoreid uuendatakse automaatselt iga 5 millisekundi tagant. Funktsiooniga
set_update_time(update_time)
saab muuta seda aega, mille tagant sensoreid uuendataks. Sisendiks on uuendamise ajavahemik sekundites. Uuendamise ajale saab ligi läbi instantsi muutuja UPDATE_TIME.

## Roboti eespoolsed infrapuna sensorid
Roboti eespoolsed (see pool, kus on käpp) infrapuna sensorid mõõdavad kaugust vahemikus 15 – 90 cm. Järgmised 3 funktsiooni tagastavad vastavalt vasaku, keskmise ja parema infrapuna sensori väärtuse meetrites. Viimane funktsioon tagastab list-i kõigist eespoolsetest infrapunasensorite väärtustest samas järjekorras nagu enne loetleti.
get_front_left_ir()
get_front_middle_ir()
get_front_right_ir()

get_front_irs()

## Roboti tagumised infrapuna sensorid
Tagumised infrapuna sensorid mõõdavad kaugust vahemikus 2 kuni 16 cm.
Järgmised 3 funktsiooni tagastavad vastavalt tagumise (see pool, kus pole käppa) vasakpoolse otsevaatava, diagonaalselt vaatava ja küljele vaatava infrapuna sensori väärtused meetrites.
get_rear_left_straight_ir()
get_rear_left_diagonal_ir()
get_rear_left_side_ir()

Järgmised 3 funktsiooni tagastavad vastavalt tagumise parempoolse otsevaatava, diagonaalselt vaatava ja küljele vaatava infrapuna sensori väärtused meetrites.
get_rear_right_straight_ir()
get_rear_right_diagonal_ir()
get_rear_right_side_ir()

Järgmistest funktsioonidest esimene tagastab kõikide tagumiste infrapunasensorite väärtused list-is juba loetletud järjekorras. Teine funktsioon tagastab kõikide infrapunasensorite väärtused list-is eespoolt alustades loetletud järjekorras.
get_rear_irs()
get_irs()

## Roboti joonejärgimise sensorid
Roboti joonejärgimissensorid asuvad roboti all tagapool. Need tagastavad väärtusi vahemikus 0 kuni 1024, kus 1024 on kõige intensiivsem ehk valgem värv ja 0 kõige vähem intensiivsem ehk kõige mustem värv. Praktikas tagastavad sensorid musta värvi korral umbes 100 ja valge värvi korral umbes 900.
Funktsioonide pooled on määratud nii, et vaadatakse ettepoole, kuigi sensorid asuvad tagapool.
Järgmised 3 funktsiooni tagastavad vastavalt kõige vasakpoolsema, vasakult teise ja vasakult kolmanda ehk vasakpoolse keskmise sensori väärtused.
get_leftmost_line_sensor()
get_second_line_sensor_from_left()
get_third_line_sensor_from_left()

Järgmised 3 funktsiooni tagastavad vastavalt kõige parempoolsema, paremalt teise ja paremalt kolmanda ehk parempoolse keskmise sensori väärtused.
get_rightmost_line_sensor()
get_second_line_sensor_from_right()
get_third_line_sensor_from_right()


## Roboti käpa juhtimine
Käppa saab liigutada üles ja alla ning lahti ja kinni.
Järgmine funktsioon liigutab käppa üles ja alla. Argumendiks sobib arv vahemikus 0 kuni 100, kus 0 on kõige madalam käpa kõrgus ja 100 on kõige kõrgem.
set_grabber_height(height_percentage)

Järgmine funktsioon liigutab käppa lahti ja kinni. Argumendiks sobib jälle arv vahemikus 0 kuni 100, kus 0 on käpa kõige lahtisem olek ja 100 on käpa kõige kinnisem olek.
close_grabber(percentage)

## Näide
from PiBot import PiBot
import rospy

\# Teeme roboti instantsi
robot = PiBot()

\# Küsime väärtust eespoolsest keskmisest infrapuna sensorist ja salvestame selle muutujasse
distance_from_object = robot.get_front_middle_ir()

\# Sõidame objektile lähedamale kuni oleme sellest 20 cm kaugusel
robot.set_wheels_speed(30)
while distance_from_object > 0.2:
  distance_from_object = robot.get_front_middle_ir()
    rospy.sleep(0.005)
    
    \# Peatame roboti, kui oleme kohale jõudnud 20 cm kaugusele objektist
    robot.set_wheels_speed(0)
