import datetime
from uuid import uuid4
import pickle


class Lekar():

    @property
    def ime(self):
        return self.__ime

    @property
    def prezime(self):
        return self.__prezime

    @property
    def specijalizacija(self):
        return self.__specijalizacija

    def __init__(self, ime, prezime, specijalizacija):

        self.__ime = ime
        self.__prezime = prezime
        self.__specijalizacija = specijalizacija

    


class Pacijent(): 

    
    @property
    def lbo(self):
        return self.__lbo

    @property
    def ime(self):
        return self.__ime
    @ime.setter
    def ime(self,ime):
        if len(ime) >= 2:
            self.__ime = ime
        else:
            print('Uneto ime je prekratko!')

    @property
    def prezime(self):
        return self.__prezime
    @prezime.setter
    def prezime(self,prezime):
        if len(prezime) >= 2:
            self.__prezime = prezime
        else:
            print('Uneto prezime je prekratko!')

    @property
    def datum_rodjenja(self):
        return self.__datum_rodjenja
    @datum_rodjenja.setter
    def datum_rodjenja(self,datum_rodjenja):
        self.__datum_rodjenja = datum_rodjenja


    def dodaj_snimanje(self,snimanje):
        self.__snimanja.append(snimanje)


    def __init__(self,ime,prezime,datum_rodjenja):
        
        if len(ime) >= 2 and len(prezime) >=2 and datetime.date.today()>=datum_rodjenja:
            self.__lbo = uuid4().hex[:11].upper()
            self.__ime = ime 
            self.__prezime = prezime
            self.__datum_rodjenja = datum_rodjenja
            self.__snimanja = []
        else:
            None

    def __str__(self):
        try:
            format_linija = '{:<12}: {}'
            return '\n'.join([
                format_linija.format('LBO', self.__lbo),
                format_linija.format('Ime', self.__ime),
                format_linija.format('Prezime', self.__prezime),
                format_linija.format('Datum rodjenja', self.__datum_rodjenja),
                Snimanje.tabela(self.__snimanja)
            ])
        except:
            return 'Uneli ste pogresno unete podatke!'

class Snimanje():
    @property
    def pacijent(self):
        return self.__pacijent
    @pacijent.setter
    def pacijent(self,pacijent):
        self.__pacijent = pacijent

    @property
    def datum_i_vreme(self):
        return self.__datum_i_vreme
    @datum_i_vreme.setter
    def datum_i_vreme(self,datum_i_vreme):
        self.__datum_i_vreme = datum_i_vreme

    @property
    def tip(self):
        return self.__tip
    @tip.setter
    def tip(self,tip):
        self.__tip = tip

    @property
    def izvestaj(self):
        return self.__izvestaj
    @izvestaj.setter
    def izvestaj(self,izvestaj):
        self.__izvestaj = izvestaj

    @property
    def lekar(self):
        return self.__lekar
    @lekar.setter
    def lekar(self,lekar):
        self.__lekar = lekar

    @property
    def snimak(self):
        return self.__snimak
    @snimak.setter
    def snimak(self,snimak):
        self.__snimak = snimak

    @classmethod
    def tabela(cls, snimanja):
        format_linije = "{:20} {:15} {:40}"

        prikaz = [
            "",
            format_linije.format("Datum i vreme", "Lekar", "Izveštaj"),
            format_linije.format("-"*20, "-"*15, "-"*40)
        ]
        for snimanje in snimanja:
            prikaz.append(format_linije.format(
                snimanje.__datum_i_vreme.strftime("%d.%m.%Y. %H:%M:%S"),
                "Dr {} {}".format(snimanje.__lekar.ime, snimanje.__lekar.prezime),
                snimanje.__izvestaj
            ))

        return "\n".join(prikaz)

    def __init__(self,pacijent,datum_i_vreme,tip,izvestaj,lekar,snimak):

        if pacijent.datum_rodjenja < datum_i_vreme.date() < datetime.date.today():

            self.__pacijent = pacijent
            self.__datum_i_vreme = datum_i_vreme
            self.__tip = tip
            self.__izvestaj = izvestaj
            self.__lekar = lekar
            self.__snimak = snimak
        else:
            None

    def __str__(self):
        try:
            format_linija = '{:<12}:{}'

            return '\n'.join([
                format_linija.format('Pacijent', self.__pacijent.ime + ' '+ self.__pacijent.prezime),
                format_linija.format('Datum i vreme', self.__datum_i_vreme),
                format_linija.format('Tip', self.__tip),
                format_linija.format('Izvestaj', self.__izvestaj),
                format_linija.format('Lekar', self.__lekar.ime + ' ' + self.__lekar.prezime),
                format_linija.format('Snimak', self.__snimak)

            ])
        except:
            return 'Pogresno uneto vreme!'



class Podaci:
    def dodaj_snimak(self, snimak):
        self.__snimci.append(snimak)

    def dodaj_snimanje(self, snimanje):
        self.__snimanja.append(snimanje)

    def dodaj_pacijenta(self, pacijent):
        self.__pacijenti.append(pacijent)

    def brisanje_snimanja(self, snimanje):
        if snimanje in self.__snimanja:
            self.__snimanja.remove(snimanje)
            self.__snimci.remove(snimanje.snimak)

    
    def brisanje_pacijenta(self, pacijent):
        if pacijent in self.__pacijenti:
            self.__pacijenti.remove(pacijent)

        snimanja_za_brisanje = []

        for snimanje in self.__snimanja:
            if pacijent.lbo == snimanje.pacijent.lbo:
                snimanja_za_brisanje.append(snimanje)

        for snimanje in snimanja_za_brisanje:
            self.__snimanja.remove(snimanje)
            self.__snimci.remove(snimanje.snimak)


    __naziv_datoteke = r'C:\Users\HP\Desktop\Projekat\radiologija_podaci'

    @property
    def pacijenti(self):
        return self.__pacijenti

    @property
    def snimanja(self):
        return self.__snimanja

    @property
    def snimci(self):
        return self.__snimci
        
    def __init__(self):

        self.__pacijenti = []
        self.__snimanja = []
        self.__snimci = []

    @classmethod
    def snimanje(cls, podaci):
        datoteka = open(cls.__naziv_datoteke, "wb")
        pickle.dump(podaci, datoteka)
        datoteka.close()

    @classmethod
    def ucitavanje(cls):
        datoteka = open(cls.__naziv_datoteke, 'rb')
        podaci = pickle.load(datoteka)
        datoteka.close()
        return podaci




    







