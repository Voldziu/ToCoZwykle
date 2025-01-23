dobra bede tu pisal co mialem na mysli tworzac to gowno:

1. Database.py
  Klasa MongoDB sluzy do komuniukacji z bazą.
  Komunikacja z bazą będzie na **kuchni**, wiec trzeba bedzie to jakos przeniesctam
  W kontekscie bazy danych, trzeba będzie stworzyc komunikację między Kiosk.py a Kuchnia.py (na kuchni bedzie komunikacja z bazą, moze tam postawimy flaska i Kiosk.py bedzie jebac po endpointach?)
2. seeder.py
   To jest do seedowania danych do bazy, to też leci do kuchni

3. receiver.py
   To do komunikacji z brokerem, prawdopodobnie to mamy już, ale trzeba będzie to sprawdzić w sali jak to działa z moim frontem

4. legacy_kiosk
   zapomnialem usunac xD, ale jest to co mielismy na labach, to co wyplul bot


5. Kiosk.py

  Jest tu front kiosku, prawie skonczony (todo: usuniecie zestawu z karty, zmiana nazwy, utworzenie nowego zestawu we wszystkich zaplanowanych wczesnie przypadkach uzycia tzn. przy zamowieniu, i w widoku koszyka)
  Jest tu symulacja czytania rfid na terminalu
  
