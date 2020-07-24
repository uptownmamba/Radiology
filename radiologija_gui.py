from radiologija import *
from tkinter import * 
from snimanje_gui import *
from PIL import ImageTk,Image
from tkinter import messagebox
import os



class ProzorRadiologija(Tk):

    def komanda_podaci_o_pacijentima(self):

        prozor_pacijenti = ProzorPacijenti(self, self.__podaci)

    def komanda_podaci_o_snimanjima(self):

        prozor_snimanja = SnimanjaProzor(self, self.__podaci, None)

    def komanda_izlaz(self):
        odgovor = messagebox.askokcancel('Izlaz', 'Da li zelite da napustite aplikaciju? ')
        if odgovor:
            self.destroy()

    def __init__(self, podaci):

        super().__init__()

        self.__podaci = podaci

        self.iconbitmap('radiologija_ico.ico')
        self.title('Radiologija-Novi Sad')

        img = ImageTk.PhotoImage(Image.open('radiologija.jpg'))
        self.__panel = Label(self, image = img)
        self.__panel.photo = img
        self.__panel.grid(column=2,row=2)


        meni_bar = Menu(self)
        datoteka_meni = Menu(meni_bar,tearoff=0)
        meni_bar.add_cascade(label= 'Datoteka', menu=datoteka_meni)
        datoteka_meni.add_command(label='Izlaz', command= self.komanda_izlaz)

        podaci_meni = Menu(meni_bar,tearoff=0)
        meni_bar.add_cascade(label= 'Podaci', menu=podaci_meni)
        podaci_meni.add_command(label='Prozor sa pacijentima', command= self.komanda_podaci_o_pacijentima)
        podaci_meni.add_command(label='Prozor sa snimanjima', command= self.komanda_podaci_o_snimanjima)



        self.config(menu= meni_bar)

        self.protocol('WM_DELETE_WINDOW',self.komanda_izlaz)
        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(visina,sirina)
        self.maxsize(visina,sirina)
        

        self.focus_force()


class ProzorPacijenti(Toplevel):
    def povratak(self):
        if messagebox.askokcancel('Povratak', "Da li ste sigurni da zelite da izadjete?"):
            self.destroy()

    def komanda_ocisti(self):
        self.__pacijenti_listbox.selection_clear(0, END) 
        self.promena_u_listboxu()



    def popuni_labele(self, pacijent):

        self.__labela_lbo['text'] = pacijent.lbo
        self.__labela_ime['text'] = pacijent.ime
        self.__labela_prezime['text'] = pacijent.prezime
        self.__labela_datum_rodjenja['text'] = pacijent.datum_rodjenja
        

    def promena_u_listboxu(self, event= None):
        if self.__pretraga.get() == '':
            if not self.__pacijenti_listbox.curselection():
                self.ocisti_labele()

                self.__button_izmeni['state'] = DISABLED
                self.__button_obrisi['state'] = DISABLED
                self.__button_prikazi_snimanja['state'] = DISABLED

                return

            index = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[index]
            self.popuni_labele(pacijent)
            self.__button_izmeni['state'] = NORMAL
            self.__button_obrisi['state'] = NORMAL
            self.__button_prikazi_snimanja['state'] = NORMAL
        else:
            if not self.__pacijenti_listbox.curselection():
                self.ocisti_labele()

                self.__button_izmeni['state'] = DISABLED
                self.__button_obrisi['state'] = DISABLED
                self.__button_prikazi_snimanja['state'] = DISABLED

                return

            index = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.pretrazi_pacijente(self.__pretraga.get()), key=lambda pacijent: pacijent.prezime)[index]
            self.popuni_labele(pacijent)
            self.__button_izmeni['state'] = NORMAL
            self.__button_obrisi['state'] = NORMAL
            self.__button_prikazi_snimanja['state'] = NORMAL



    def ocisti_labele(self):

        self.__labela_lbo['text'] = ' '
        self.__labela_ime['text'] = ' '
        self.__labela_prezime['text'] = ' '
        self.__labela_datum_rodjenja['text'] = ' '
        

    def dodaj_pacijenta(self):

        self.__pretraga.set('')
        prozor_dodavanje = DodavanjeProzor(self, self.__podaci)
        self.wait_window(prozor_dodavanje)

        if prozor_dodavanje.otkazan:
            return

        pacijent = self.__podaci.pacijenti[-1]
        indeks = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime).index(pacijent)
        self.__pacijenti_listbox.insert(indeks, '{} {}'.format(pacijent.prezime,pacijent.ime))
        self.__pacijenti_listbox.selection_set(indeks)
        self.promena_u_listboxu()

    def obrisi_pacijenta(self):

        odgovor = messagebox.askquestion('Upozorenje!', "Da li ste sigurni, brisanjem pacijenta brisu se i sva njegova snimanja?", icon= 'warning')
        if odgovor == 'no':
            return

        
        indeks = self.__pacijenti_listbox.curselection()[0]
        pacijent_za_brisanje = sorted(self.pretrazi_pacijente(self.__pretraga.get()), key=lambda pacijent: pacijent.prezime)[indeks]
        Podaci.brisanje_pacijenta(self.__podaci,pacijent_za_brisanje)
        self.__pretraga.set('')
        

        self.config(cursor= 'wait')
        Podaci.snimanje(self.__podaci)
        self.config(cursor= '')

        self.popupni_pacijenti_listbox('')
        self.__pacijenti_listbox.delete(indeks)
        self.popupni_pacijenti_listbox('')
        self.__pacijenti_listbox.selection_set(indeks-1)
        self.promena_u_listboxu()
    
    def prikazi_snimanja(self):

        if self.__pretraga.get() == '':
            indeks = self.__pacijenti_listbox.curselection()[0] + 1
            prozor_snimanja = SnimanjaProzor(self,self.__podaci,indeks)
        else:
            pacijenti_pretrazeni = sorted(self.pretrazi_pacijente(self.__pretraga.get()), key=lambda pacijent: pacijent.prezime)
            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = pacijenti_pretrazeni.pop(indeks)
            index =  sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime).index(pacijent) + 1
            prozor_snimanja = SnimanjaProzor(self,self.__podaci,index)

    def izmeni_pacijenta(self):
        if self.__pretraga.get() == '':
            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[indeks] 

            prozor_za_izmenu = IzmeniProzor(self, self.__podaci,pacijent)
            self.wait_window(prozor_za_izmenu)

            if prozor_za_izmenu.otkazan:
                return

            self.__pretraga.set('')
            self.__pacijenti_listbox.delete(indeks)
            self.__pacijenti_listbox.insert(indeks,'{} {}'.format(pacijent.prezime,pacijent.ime))
            self.__pacijenti_listbox.selection_set(indeks)
            self.promena_u_listboxu()
        else:
            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.pretrazi_pacijente(self.__pretraga.get()), key=lambda pacijent: pacijent.prezime)[indeks]

            prozor_za_izmenu = IzmeniProzor(self, self.__podaci, pacijent)
            self.wait_window(prozor_za_izmenu)

            if prozor_za_izmenu.otkazan:
                return

            self.__pacijenti_listbox.delete(indeks)
            self.__pacijenti_listbox.insert(indeks,'{} {}'.format(pacijent.prezime,pacijent.ime))
            self.__pacijenti_listbox.selection_set(indeks)
            self.promena_u_listboxu()

    def pretrazi_pacijente(self, pretraga):
        pacijenti = []
        for pacijent in self.__podaci.pacijenti:
            if pretraga.lower() in pacijent.ime.lower() or pretraga.lower() in pacijent.prezime.lower():
                pacijenti.append(pacijent)
        return pacijenti


        

    def popupni_pacijenti_listbox(self, pretraga):
        if pretraga == '':
            self.__pacijenti_listbox.delete(0, END)
            sortirani_pacijenti = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)
            for pacijent in sortirani_pacijenti:
                self.__pacijenti_listbox.insert(END, '{} {}'.format(pacijent.prezime,pacijent.ime))
        else:
            pacijenti = self.pretrazi_pacijente(pretraga)
            self.__pacijenti_listbox.delete(0, END)
            sortirani_pacijenti = sorted(pacijenti, key=lambda pacijent: pacijent.prezime)
            for pacijent in sortirani_pacijenti:
                self.__pacijenti_listbox.insert(END, '{} {}'.format(pacijent.prezime,pacijent.ime))
            
        
        
            

    def __init__(self,master,podaci):

        super().__init__(master)

        self.iconbitmap('radiologija_ico.ico')
        self.title('Pacijenti')

        self.__pretraga = StringVar(master)
        self.__pretraga.trace('w',lambda name, index, mode, pretraga= self.__pretraga: self.popupni_pacijenti_listbox(pretraga.get()))
        self.__pretraga.trace('w',lambda name, index, mode, pretraga= self.__pretraga: self.promena_u_listboxu())
        self.__pretraga.trace('w',lambda name, index, mode, pretraga= self.__pretraga: self.komanda_ocisti())

        self.__podaci = podaci

        self.__pacijenti_listbox = Listbox(self, activestyle="none", exportselection=False)
        self.__pacijenti_listbox.pack(side= LEFT, fill=BOTH, expand=1)
        self.__pacijenti_listbox.bind("<<ListboxSelect>>", self.promena_u_listboxu)
        

        self.__pacijenti_panel = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__pacijenti_panel.pack(side= RIGHT, fill= BOTH, expand=1)

        self.__labela_lbo = Label(self.__pacijenti_panel)
        self.__labela_ime = Label(self.__pacijenti_panel)
        self.__labela_prezime = Label(self.__pacijenti_panel)
        self.__labela_datum_rodjenja = Label(self.__pacijenti_panel)
        
        Label(self.__pacijenti_panel, text='Pretraga pacijenata:').grid(row=0, sticky= E)
        self.__entry_pretraga = Entry(self.__pacijenti_panel, textvariable= self.__pretraga)
        self.__entry_pretraga.grid(row=0, column=1,sticky=W)
        

        red = 1
        Label(self.__pacijenti_panel, text= 'LBO:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Ime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Prezime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Datum rodjenja:').grid(row=red, sticky=E)
        


        red = 1
        self.__labela_lbo.grid(row=red,column=1, sticky=W)
        red += 1
        self.__labela_ime.grid(row=red,column=1, sticky=W)
        red += 1
        self.__labela_prezime.grid(row=red,column=1, sticky=W)
        red += 1
        self.__labela_datum_rodjenja.grid(row=red,column=1, sticky=W)
        

        self.popupni_pacijenti_listbox('')
        

        self.__button_ocisti = Button(self.__pacijenti_panel, text= 'Ocisti', command=self.komanda_ocisti)
        self.__button_ocisti.grid(row= red+1,column= 1, sticky= S)
        self.__button_obrisi = Button(self.__pacijenti_panel, text= 'Obrisi', command=self.obrisi_pacijenta, state=DISABLED)
        self.__button_obrisi.grid(row= red+1,column= 2, sticky= S)
        self.__button_dodaj = Button(self.__pacijenti_panel, text= 'Dodaj', command=self.dodaj_pacijenta)
        self.__button_dodaj.grid(row= red+1,column= 3, sticky= S)
        self.__button_prikazi_snimanja = Button(self.__pacijenti_panel, text= 'Prikazi snimanja', command=self.prikazi_snimanja)
        self.__button_prikazi_snimanja.grid(row= red+1,column= 4, sticky= S)
        self.__button_izmeni = Button(self.__pacijenti_panel, text= 'Izmeni', command=self.izmeni_pacijenta, state=DISABLED)
        self.__button_izmeni.grid(row= red+1,column= 5, sticky= S)
        self.__button_povratak = Button(self.__pacijenti_panel, text= 'Povratak', command=self.povratak)
        self.__button_povratak.grid(row= red+1, column= 6, sticky= S)

        
        

        self.transient(master)
        self.focus_force()
        self.grab_set()
        





        self.iconbitmap('radiologija_ico.ico')

    @property
    def podaci(self):
        return self.__podaci

class DodavanjeProzor(Toplevel):

    def povratak(self):
       if messagebox.askokcancel('Povratak.', "Da li zelite da se vratite?"):
           self.destroy()

    def ime_validacija(self):
        ime = self.__ime.get()
        if len(ime) < 2:
            messagebox.showerror('Greska', 'Ime mora da sadrzi dva ili vise karaktera!')
            return None
        return ime

    def prezime_validacija(self):
        prezime = self.__prezime.get()
        if len(prezime) < 2:
            messagebox.showerror('Greska', 'Prezime mora da sadrzi dva ili vise karaktera!')
        return prezime

    def datum_rodjenja_validacija(self):
        try:
            datum = datetime.date(self.__godina_rodjenja.get(), self.__mesec_rodjenja.get(), self.__dan_rodjenja.get())
            if not datetime.date.today()>=datum:
                messagebox.showerror('Greska', 'Uneli ste datum koji nije validan, format datuma je godina/mesec/dan!')
            return datum
        except:
            messagebox.showerror('Greska', 'Uneli ste datum koji nije validan, format datuma je godina/mesec/dan!')
            return None
    

    def komanda_ok(self):
        ime = self.ime_validacija()
        if not ime:
            return
        prezime = self.prezime_validacija()
        if not prezime:
            return
        datum_rodjenja = self.datum_rodjenja_validacija()
        if not datum_rodjenja:
            return
        pacijent = Pacijent(ime, prezime, datum_rodjenja)
        self.__podaci.dodaj_pacijenta(pacijent)

        self.__otkazan = False
        self.config(cursor='wait')
        Podaci.snimanje(self.__podaci)
        self.config(cursor= '')
        self.destroy()

    def __init__(self, master, podaci):

        super().__init__(master)

        self.__otkazan = True

        self.__podaci = podaci 

        self.__ime = StringVar(master)
        self.__prezime = StringVar(master)
        self.__godina_rodjenja = IntVar(master)
        self.__mesec_rodjenja = IntVar(master)
        self.__dan_rodjenja = IntVar(master)

        self.iconbitmap('radiologija_ico.ico')
        self.title('Dodavanje pacijenta')


        self.__pacijenti_panel = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__pacijenti_panel.pack(fill=BOTH, expand=1)

        red = 0
        Label(self.__pacijenti_panel, text= 'Ime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Prezime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Datum rodjenja(Godina/Mesec/Dan):').grid(row=red, sticky=E)

        red = 0
        kolona = 1
        self.__ime_entry = Entry(self.__pacijenti_panel, textvariable= self.__ime)
        self.__ime_entry.grid(row=red,column=kolona, sticky=W)
        red += 1
        self.__prezime_entry = Entry(self.__pacijenti_panel, textvariable= self.__prezime)
        self.__prezime_entry.grid(row=red,column=kolona, sticky=W)
        red += 1
        self.__spinbox_godina = Spinbox(self.__pacijenti_panel, width=20,increment=1,from_=1900, to=2100,textvariable= self.__godina_rodjenja )
        self.__spinbox_godina.grid(row= red, column= kolona,sticky=W)
        kolona += 1
        self.__spinbox_mesec = Spinbox(self.__pacijenti_panel, width=5,increment=1,from_=1, to=12,textvariable= self.__mesec_rodjenja)
        self.__spinbox_mesec.grid(row=red, column= kolona, sticky=W)
        kolona +=1
        self.__spinbox_dan = Spinbox(self.__pacijenti_panel, width=5, increment=1, from_=1, to=31,textvariable= self.__dan_rodjenja)
        self.__spinbox_dan.grid(row=red, column= kolona, sticky=W)

        red +=1
        self.__dodaj_button = Button(self.__pacijenti_panel, text= 'Dodaj',command=self.komanda_ok)
        self.__dodaj_button.grid(row=red, column=1, sticky= S)
        red +=1
        self.__dodaj_button = Button(self.__pacijenti_panel, text= 'Povratak', command=self.povratak)
        self.__dodaj_button.grid(row=red, column= 2, sticky=S)

        self.transient(master)
        self.focus_force()
        self.grab_set()

    @property
    def otkazan(self):
        return self.__otkazan
            
class IzmeniProzor(Toplevel):
    def ime_validacija(self):
        ime = self.__ime.get()
        if len(ime) < 2:
            messagebox.showerror('Greska', 'Ime mora da sadrzi dva ili vise karaktera!')
            return None
        return ime

    def prezime_validacija(self):
        prezime = self.__prezime.get()
        if len(prezime) < 2:
            messagebox.showerror('Greska', 'Prezime mora da sadrzi dva ili vise karaktera!')
        return prezime

    def datum_rodjenja_validacija(self):
        try:
            datum = datetime.date(self.__godina_rodjenja.get(), self.__mesec_rodjenja.get(), self.__dan_rodjenja.get())
            if not datetime.date.today()>=datum:
                messagebox.showerror('Greska', 'Uneli ste datum koji nije validan, format datuma je godina/mesec/dan!')
            return datum
        except:
            messagebox.showerror('Greska', 'Uneli ste datum koji nije validan, format datuma je godina/mesec/dan!')
            return None

    def povratak(self):
       if messagebox.askokcancel('Povratak.', "Da li zelite da se vratite?"):
           self.destroy()

    def komanda_ok(self):
        ime = self.ime_validacija()
        if not ime:
            return
        prezime = self.prezime_validacija()
        if not prezime:
            return
        datum_rodjenja = self.datum_rodjenja_validacija()
        if not datum_rodjenja:
            return

        self.__pacijent.ime = ime
        self.__pacijent.prezime = prezime
        self.__pacijent.datum_rodjenja = datum_rodjenja

        self.config(cursor="wait")
        Podaci.snimanje(self.__podaci)
        self.config(cursor="")

        self.__otkazan = False
        self.destroy()

    def __init__(self, master, podaci, pacijent):

        super().__init__(master)

        self.__otkazan = True

        self.__podaci = podaci 

        self.__pacijent = pacijent

        self.__ime = StringVar(master)
        self.__prezime = StringVar(master)
        self.__godina_rodjenja = IntVar(master)
        self.__mesec_rodjenja = IntVar(master)
        self.__dan_rodjenja = IntVar(master)
        self.__lbo = StringVar(master)

        self.__ime.set(pacijent.ime)
        self.__prezime.set(pacijent.prezime)
        self.__godina_rodjenja.set(pacijent.datum_rodjenja.year)
        self.__mesec_rodjenja.set(pacijent.datum_rodjenja.month)
        self.__dan_rodjenja.set(pacijent.datum_rodjenja.day)
        self.__lbo.set(pacijent.lbo)


        self.iconbitmap('radiologija_ico.ico')
        self.title('Izmena pacijenta')


        self.__pacijenti_panel = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__pacijenti_panel.pack(fill=BOTH, expand=1)

        red = 0
        Label(self.__pacijenti_panel, text= 'LBO:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Ime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Prezime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_panel, text= 'Datum rodjenja(Godina/Mesec/Dan):').grid(row=red, sticky=E)

        red = 0
        kolona = 1
        self.__lbo_entry = Entry(self.__pacijenti_panel, textvariable= self.__lbo)
        self.__lbo_entry.grid(row=red,column=kolona, sticky=W)
        red += 1
        self.__ime_entry = Entry(self.__pacijenti_panel, textvariable= self.__ime)
        self.__ime_entry.grid(row=red,column=kolona, sticky=W)
        red += 1
        self.__prezime_entry = Entry(self.__pacijenti_panel, textvariable= self.__prezime)
        self.__prezime_entry.grid(row=red,column=kolona, sticky=W)
        red += 1
        self.__spinbox_godina = Spinbox(self.__pacijenti_panel, width=20,increment=1,from_=1900, to=2100,textvariable= self.__godina_rodjenja )
        self.__spinbox_godina.grid(row= red, column= kolona,sticky=W)
        kolona += 1
        self.__spinbox_mesec = Spinbox(self.__pacijenti_panel, width=20,increment=1,from_=1, to=12,textvariable= self.__mesec_rodjenja)
        self.__spinbox_mesec.grid(row=red, column= kolona, sticky=W)
        kolona +=1
        self.__spinbox_dan = Spinbox(self.__pacijenti_panel, width=20, increment=1, from_=1, to=31,textvariable= self.__dan_rodjenja)
        self.__spinbox_dan.grid(row=red, column= kolona, sticky=W)

        red +=1
        self.__dodaj_button = Button(self.__pacijenti_panel, text= 'Izmeni',command=self.komanda_ok)
        self.__dodaj_button.grid(row=red, column=1, sticky= S)
        red +=1
        self.__dodaj_button = Button(self.__pacijenti_panel, text= 'Povratak', command=self.povratak)
        self.__dodaj_button.grid(row=red, column= 2, sticky=S)


        self.__lbo_entry['state'] = DISABLED

        self.transient(master)
        self.focus_force()
        self.grab_set()


    @property
    def otkazan(self):
        return self.__otkazan


def main():


    path = os.path.abspath(__file__).replace('\\radiologija_gui.py','')
    os.chdir(path)
    podaci = Podaci.ucitavanje()
    radiologija_prozor = ProzorRadiologija(podaci)
    radiologija_prozor.mainloop()


main()