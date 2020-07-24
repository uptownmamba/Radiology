from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pydicom
from PIL import Image, ImageTk
import pydicom_PIL


from radiologija import *




class SnimanjaProzor(Toplevel):

    def otvori_dicom_snimak(self):
        staza_do_datoteke = self.__labela_path.cget('text')
        if staza_do_datoteke != '':
            dataset = pydicom.dcmread(staza_do_datoteke, force= True)
            print(dataset)
        else:
            messagebox.showerror('Greska pri ucitavanju', 'Niste uneli stazu do datoteke')
        DICOMProzor(self, dataset)



    def komanda_izmena(self):


        indeks = self.__listbox_snimanja.curselection()[0]
        snimanje = sorted(self.pretraga_snimanja(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()), key=lambda snimanje: snimanje.datum_i_vreme)[indeks]
        prozor_izmena = ProzorIzmena(self,self.__podaci,snimanje)
        self.wait_window(prozor_izmena)

        if prozor_izmena.otkazan:
            return

        self.__listbox_snimanja.delete(indeks)
        self.__listbox_snimanja.insert(indeks, snimanje.datum_i_vreme)
        self.__listbox_snimanja.selection_set(indeks)
        self.promena_u_listboxu()
    def komanda_dodaj(self):

        try:
            indeks_tip_snimka = self.__vrste_snimaka_za_dodavanje.index(self.__tip_snimka.get())
        except:
            indeks_tip_snimka = 0
        try:
            pacijenti_combox = self.pacijenti_combox()
            indeks_pacijenta = pacijenti_combox.index(self.__pacijent_combox.get())
        except:
            indeks_pacijenta = 0


        self.komanda_ocisti()
        prozor_dodavanje = DodajSnimanje(self,self.__podaci,indeks_pacijenta,indeks_tip_snimka)
        self.wait_window(prozor_dodavanje)

        if prozor_dodavanje.otkazan:
            return

        snimanje = self.__podaci.snimanja[-1]
        indeks = sorted(self.__podaci.snimanja, key=lambda snimanje: snimanje.datum_i_vreme).index(snimanje)
        self.komanda_ocisti()
        self.__listbox_snimanja.insert(indeks,snimanje.datum_i_vreme)
        self.komanda_ocisti()
        self.__listbox_snimanja.selection_set(indeks)
        self.promena_u_listboxu()

    def brisanje(self):
        odgovor = messagebox.askquestion('Upozorenje!', 'Da li ste sigurni da zelite da obrisete snimanje!', icon='warning')
        if odgovor == 'no':
            return

        indeks = self.__listbox_snimanja.curselection()[0]
        snimak_za_brisanje = sorted(self.pretraga_snimanja(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()), key=lambda snimanje: snimanje.datum_i_vreme)[indeks]
        Podaci.brisanje_snimanja(self.__podaci,snimak_za_brisanje)

        self.config(cursor= 'wait')
        Podaci.snimanje(self.__podaci)
        self.config(cursor= '')

        self.komanda_ocisti()
        self.__listbox_snimanja.delete(indeks)
        self.komanda_ocisti()
        self.__listbox_snimanja.selection_set(indeks-1)
        self.promena_u_listboxu()

    def komanda_povratak(self):
        self.destroy()

    def promena_u_listboxu(self, event=None):
        if not self.__listbox_snimanja.curselection():
                self.ocisti_labele()

                self.__button_izmena['state'] = DISABLED
                self.__button_brisanje['state'] = DISABLED
                self.__button_otvori['state'] = DISABLED

                return

        index = self.__listbox_snimanja.curselection()[0]
        snimanje = sorted(self.pretraga_snimanja(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()), key=lambda snimanje: snimanje.datum_i_vreme)[index]
        self.popuni_labele(snimanje)
        self.__button_izmena['state'] = NORMAL
        self.__button_brisanje['state'] = NORMAL
        self.__button_otvori['state'] = NORMAL

    def komanda_ocisti(self):
        self.__listbox_snimanja.selection_clear(0,END)
        self.promena_u_listboxu()
        self.__dropbox_vrsta_snimanja.current(0)
        self.__dropbox_pacijenata.current(0)
        self.__dropbox_pacijenata.selection_clear()
        self.__dropbox_vrsta_snimanja.selection_clear()
        self.popuni_listbox(0,0)
        
        



    def ocisti_labele(self):

        self.__labela_pacijent['text'] = ''
        self.__labela_lekar['text'] = ''
        self.__labela_datum_i_vreme['text'] = ''
        self.__labela_tip['text'] = ''
        self.__labela_path['text'] = ''

    def popuni_labele(self, snimanje):
        self.__labela_pacijent['text'] = snimanje.pacijent.ime + ' ' + snimanje.pacijent.prezime
        self.__labela_lekar['text'] = snimanje.lekar.ime + ' ' + snimanje.lekar.prezime
        self.__labela_datum_i_vreme['text'] = snimanje.datum_i_vreme
        self.__labela_tip['text'] = snimanje.tip
        self.__labela_path['text'] = snimanje.snimak




    def pacijenti_combox(self):
        pacijenti = sorted(self.__podaci.pacijenti, key= lambda pacijent: pacijent.prezime)
        pacijenti_combox = ['Odaberite pacijenta']
        for pacijent in pacijenti:
            pacijent_za_dodati = "{} {}".format(pacijent.prezime, pacijent.ime)
            pacijenti_combox.append(pacijent_za_dodati)
        return pacijenti_combox

    def popuni_listbox(self, indeks_pacijent, indeks_tip_snimanja):
        self.__listbox_snimanja.delete(0, END)
        sortirana_snimanja = sorted(self.pretraga_snimanja(indeks_pacijent,indeks_tip_snimanja), key= lambda snimanje: snimanje.datum_i_vreme)
        for snimanje in sortirana_snimanja:
            self.__listbox_snimanja.insert(END, snimanje.datum_i_vreme)

    def pretraga_snimanja(self, indeks_pacijent,indeks_tip_snimka):
        pretrazena_snimanja = []
        if indeks_pacijent == 0 and indeks_tip_snimka == 0:
            return self.__podaci.snimanja

        elif indeks_pacijent != 0 and indeks_tip_snimka != 0:
            pacijent = sorted(self.__podaci.pacijenti, key= lambda pacijent: pacijent.prezime)[indeks_pacijent-1]
            tip_snimka = self.__vrste_snimaka[indeks_tip_snimka]
            for snimanje in self.__podaci.snimanja:
                if pacijent == snimanje.pacijent and tip_snimka == snimanje.tip:
                    pretrazena_snimanja.append(snimanje)
            return pretrazena_snimanja

        elif indeks_pacijent == 0:
            tip_snimka = self.__vrste_snimaka[indeks_tip_snimka]
            for snimanje in self.__podaci.snimanja:
                if tip_snimka == snimanje.tip:
                    pretrazena_snimanja.append(snimanje)
            return pretrazena_snimanja

        elif indeks_tip_snimka ==0:
            pacijent = sorted(self.__podaci.pacijenti, key= lambda pacijent: pacijent.prezime)[indeks_pacijent-1]
            for snimanje in self.__podaci.snimanja:
                if pacijent == snimanje.pacijent:
                    pretrazena_snimanja.append(snimanje)
            return pretrazena_snimanja
            



    @property
    def podaci(self):
        return self.__podaci

    


    def __init__(self, master, podaci, indeks):

        super().__init__(master)




        self.iconbitmap('radiologija_ico.ico')
        self.title('Snimanja pacijenata')

        self.__vrste_snimaka = ['Prikaz snimaka svih tipova',
                                'Computed tomography (CT)',
                                'Fluoroscopy',
                                'Magnetic resonance imaging (MRI)',
                                'Magnetic resonance angiography (MRA)',
                                'Mammography',
                                'X-rays (XR)',
                                'Positron emission tomography (PET)',
                                'Ultrasound']

        self.__vrste_snimaka_za_dodavanje =  ['Computed tomography (CT)',
                                                        'Fluoroscopy',
                                    'Magnetic resonance imaging (MRI)',
                                'Magnetic resonance angiography (MRA)',
                                                        'Mammography',
                                                        'X-rays (XR)',
                                'Positron emission tomography (PET)',
                                                        'Ultrasound']

        self.__podaci = podaci
        
        
        self.__indeks = indeks

        self.__listbox_snimanja = Listbox(self, activestyle="none", exportselection=False)
        self.__listbox_snimanja.pack(side= LEFT, fill=BOTH, expand=1)
        self.__listbox_snimanja.bind("<<ListboxSelect>>", self.promena_u_listboxu)
        
        
        self.__frame_snimanja = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__frame_snimanja.pack(side= RIGHT, fill=BOTH, expand = 1)


        self.__tip_snimka = StringVar(master)
        self.__pacijent_combox = StringVar(master)
        

        

        self.__dropbox_pacijenata = ttk.Combobox(self.__frame_snimanja, values= self.pacijenti_combox(), textvariable= self.__pacijent_combox)
        self.__dropbox_pacijenata.current(0)
        if isinstance(self.__indeks,int):
            self.__dropbox_pacijenata.current(self.__indeks)
        self.__dropbox_pacijenata.grid(sticky= N, row= 0)
        self.__dropbox_pacijenata.bind("<<ComboboxSelected>>", lambda _ :self.popuni_listbox(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()))


        self.__dropbox_vrsta_snimanja = ttk.Combobox(self.__frame_snimanja, value=self.__vrste_snimaka,width= 50, textvariable= self.__tip_snimka)
        self.__dropbox_vrsta_snimanja.grid(sticky=N , row = 0, column= 1)
        self.__dropbox_vrsta_snimanja.current(0)
        self.__dropbox_vrsta_snimanja.bind("<<ComboboxSelected>>", lambda _ :self.popuni_listbox(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()))

        self.__dropbox_pacijenata.bind("<<ComboboxSelected>>", self.popuni_listbox(self.__dropbox_pacijenata.current(), self.__dropbox_vrsta_snimanja.current()))
        



        self.__button_ocisti = Button(self.__frame_snimanja, text='Ocisti', command=self.komanda_ocisti)
        self.__button_dodaj = Button(self.__frame_snimanja, text='Dodavanje', command=self.komanda_dodaj)
        self.__button_izmena = Button(self.__frame_snimanja, text='Izmena', command=self.komanda_izmena)
        self.__button_otvori = Button(self.__frame_snimanja, text= 'Otvori DICOM', command=self.otvori_dicom_snimak)
        self.__button_brisanje = Button(self.__frame_snimanja, text='Brisanje', command=self.brisanje)
        self.__button_povratak = Button(self.__frame_snimanja, text= 'Povratak', command= self.komanda_povratak)

        red = 1
        Label(self.__frame_snimanja, text='Pacijent:').grid(row=red, sticky=E)
        red = red + 1
        Label(self.__frame_snimanja, text='Datum i vreme:').grid(row=red, sticky=E)
        red = red + 1 
        Label(self.__frame_snimanja, text='Vrsta snimka:').grid(row=red, sticky=E)
        red = red + 1 
        Label(self.__frame_snimanja, text='Lekar:').grid(row=red, sticky=E)
        red = red + 1
        Label(self.__frame_snimanja, text= 'Putanja do snimka: ').grid(row=red, sticky=E)
        red = red + 1
        self.__button_ocisti.grid(row= red, sticky=S)
        self.__button_dodaj.grid(row = red, column= 1, sticky= S)
        self.__button_izmena.grid(row = red, column= 2, sticky= S)
        self.__button_otvori.grid(row= red , column = 3 , sticky= S)
        self.__button_brisanje.grid(row = red, column= 4, sticky= S)
        self.__button_povratak.grid(row = red, column= 5, sticky= S)
        

        self.__labela_pacijent = Label(self.__frame_snimanja)
        self.__labela_datum_i_vreme = Label(self.__frame_snimanja)
        self.__labela_lekar = Label(self.__frame_snimanja)
        self.__labela_tip = Label(self.__frame_snimanja)
        self.__labela_path = Label(self.__frame_snimanja)


        red = 1
        self.__labela_pacijent.grid(row= red, column=1)
        red = red  +1
        self.__labela_datum_i_vreme.grid(row= red, column=1)
        red =red +1
        self.__labela_lekar.grid(row= red, column=1)
        red =red +1
        self.__labela_tip.grid(row= red, column=1)
        red = red  +1
        self.__labela_path.grid(row=red, column= 1)

        self.__button_izmena['state'] = DISABLED
        self.__button_brisanje['state'] = DISABLED
        self.__button_otvori['state'] = DISABLED

        self.transient(master)
        self.focus_force()
        self.grab_set()



        


class DodajSnimanje(Toplevel):
    @property
    def otkazan(self):
        return self.__otkazan

    def dicom_izmena(self):
        self.__staza_do_datoteke = self.__path.get().split('/')[-1]
        pacijent = self.validacija_pacijent()
        lekar = self.validacija_lekar()
        self.__dataset = pydicom.dcmread(self.__staza_do_datoteke, force= True)
        self.__dataset.PatientID = pacijent.lbo
        self.__dataset.PatientName = pacijent.ime + ' ' + pacijent.prezime
        self.__dataset.DateTime = self.validacija_datum_i_vreme()
        self.__dataset.ReferringPhysicianName = lekar.ime + ' ' + lekar.prezime
        self.__dataset.PatientBirthDate = pacijent.datum_rodjenja
        self.__dataset.Modality = self.__tip_snimka.get()
        self.__dataset.StudyDescription = self.__izvestaj.get()
        self.__dataset.save_as(self.__staza_do_datoteke)
        

    def otvori_dicom_snimak(self):
        staza_do_datoteke = self.__path.get()
        if staza_do_datoteke != '':
            dataset = pydicom.dcmread(staza_do_datoteke, force= True)   
            print(dataset)
        else:
            messagebox.showerror('Greska pri ucitavanju', 'Niste uneli stazu do datoteke')
        DICOMSlika(self, dataset)
        
        

    def pronadji_path(self):

        staza_do_datoteke = filedialog.askopenfilename(
                title="Otvaranje",
                filetypes=[("All files", "*.*"), ("DICOM files", "*.dcm")])
        if staza_do_datoteke:
            self.__button_snimak['state'] = NORMAL
            self.__path.set(staza_do_datoteke)


    def pacijenti_combox(self):
        pacijenti = sorted(self.__podaci.pacijenti, key= lambda pacijent: pacijent.prezime)
        pacijenti_combox = []
        for pacijent in pacijenti:
            pacijent_za_dodati = "{} {}".format(pacijent.prezime, pacijent.ime)
            pacijenti_combox.append(pacijent_za_dodati)
        return pacijenti_combox

    def validacija_pacijent(self):
        pacijent_ime_i_prezime = self.__pacijent.get()
        pacijenti_u_dropboxu = self.pacijenti_combox()
        indeks = pacijenti_u_dropboxu.index(pacijent_ime_i_prezime)
        pacijent = sorted(self.__podaci.pacijenti, key= lambda pacijent: pacijent.prezime)[indeks]

        return pacijent

    def validacija_lekar(self):
        ime = self.__lekar_ime.get()
        prezime = self.__lekar_prezime.get()
        lekar = Lekar(ime, prezime,'Opsta praksa')
        return lekar

    def validacija_datum_i_vreme(self):
        godina = self.__godina.get()
        mesec = self.__mesec.get()
        dan = self.__dan.get()
        sat = self.__sat.get()
        minut = self.__minut.get()
        sekund = self.__sekund.get()
        try:
            datum_i_vreme = datetime.datetime(godina,mesec,dan,sat,minut,sekund)
        except:
            messagebox.showerror('Greska','Datum koji ste uneli nije validan!')
        pacijent = self.validacija_pacijent()
        if not pacijent.datum_rodjenja < datum_i_vreme.date() < datetime.date.today():
            messagebox.showerror('Greska!', 'Uneli ste los datum!')
            return None
        else:
            return datum_i_vreme
    
    def validacija_snimak(self):
        snimak = self.__path.get()
        for snimanje in self.__podaci.snimanja:
            if snimak == snimanje.snimak:
                messagebox.showerror('Greska!','Snimak je vec zakacen!')
                return None
        return snimak


    def dodaj_snimanje(self):
        
        pacijent = self.validacija_pacijent()
        if not pacijent:
            return
        lekar = self.validacija_lekar()
        if not lekar:
            return
        datum_i_vreme = self.validacija_datum_i_vreme()
        if not datum_i_vreme:
            return
        tip = self.__tip_snimka.get()
        izvestaj = self.__izvestaj.get()
        if len(self.__path.get()) < 6:
            return
        snimak = self.validacija_snimak()
        if not snimak:
            return
        
        self.__podaci.dodaj_snimak(snimak)
        snimanje = Snimanje(pacijent,datum_i_vreme,tip,izvestaj,lekar,snimak)
        self.__podaci.dodaj_snimanje(snimanje)
        self.dicom_izmena()

        self.__otkazan = False
        self.config(cursor='wait')
        Podaci.snimanje(self.__podaci)
        self.config(cursor= '')
        self.destroy()


    def __init__(self, master, podaci, indeks_pacijent, indeks_tip_snimka):

        super().__init__(master)

        self.__podaci = podaci
        self.__indeks_pacijent = indeks_pacijent
        self.__indeks_tip_snimka = indeks_tip_snimka


        self.__dataset = None
        self.__staza_do_datoteke = ''

        self.__path = StringVar(master)
        self.__godina = IntVar(master)
        self.__dan = IntVar(master)
        self.__mesec= IntVar(master)
        self.__sat = IntVar(master)
        self.__sekund = IntVar(master)
        self.__minut = IntVar(master)
        self.__lekar_ime = StringVar(master)
        self.__lekar_prezime = StringVar(master)
        self.__tip_snimka = StringVar(master)
        self.__pacijent = StringVar(master)
        self.__izvestaj = StringVar(master)


        self.iconbitmap('radiologija_ico.ico')
        self.title('Dodavanje snimanja')


        self.__snimanje_panel = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__snimanje_panel.pack(fill=BOTH, expand=1)

        self.__vrste_snimaka = [
                                'Computed tomography (CT)',
                                'Fluoroscopy',
                                'Magnetic resonance imaging (MRI)',
                                'Magnetic resonance angiography (MRA)',
                                'Mammography',
                                'X-rays (XR)',
                                'Positron emission tomography (PET)',
                                'Ultrasound']

        red = 0
        Label(self.__snimanje_panel, text= 'Ime i prezime pacijenta: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Ime i prezime lekara: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Datum i vreme snimanja (Godina/Mesec/Dan/Sat/Minut/Sekund): ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Izvestaj: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Tip snimanja: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Putanja do snimka: ').grid(row=red, sticky=E)
        red += 1

        kolona = 1
        red = 0
        self.__dropbox_pacijenata = ttk.Combobox(self.__snimanje_panel, values= self.pacijenti_combox(), textvariable= self.__pacijent)
        self.__dropbox_pacijenata.grid(sticky= W, row= red, column=1)
        self.__dropbox_pacijenata.current(0)
        if self.__indeks_pacijent != 0:
            self.__dropbox_pacijenata.current(self.__indeks_pacijent-1)
        else:
            self.__dropbox_pacijenata.current(0)
        red += 1
        self.__entry_lekar_ime = Entry(self.__snimanje_panel, textvariable = self.__lekar_ime)
        self.__entry_lekar_ime.grid(sticky = W, row = red, column= 1)
        self.__entry_lekar_prezime = Entry(self.__snimanje_panel, textvariable = self.__lekar_prezime)
        self.__entry_lekar_prezime.grid(sticky = W, row = red, column= 2)
        red +=1
        self.__spinbox_godina = Spinbox(self.__snimanje_panel, width=10,increment=1,from_=1900, to=2100,textvariable = self.__godina)
        self.__spinbox_godina.grid(sticky= W, row= red, column= kolona)
        kolona += 1 
        self.__spinbox_mesec = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=12,textvariable = self.__mesec)
        self.__spinbox_mesec.grid(sticky= W, row= red, column= kolona)
        kolona += 1 
        self.__spinbox_dan = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=31, textvariable = self.__dan)
        self.__spinbox_dan.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_sat = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=24, textvariable = self.__sat)
        self.__spinbox_sat.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_minut = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=60, textvariable = self.__minut)
        self.__spinbox_minut.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_sekunda = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=60, textvariable = self.__sekund)
        self.__spinbox_sekunda.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        red += 1
        self.__entry_izvestaj = Entry(self.__snimanje_panel, textvariable = self.__izvestaj)
        self.__entry_izvestaj.grid(sticky = W, row = red, column= 1)
        red += 1
        self.__dropbox_tipova = ttk.Combobox(self.__snimanje_panel,width=30, values= self.__vrste_snimaka, textvariable = self.__tip_snimka )
        self.__dropbox_tipova.grid(sticky= W, row= red, column = 1)
        self.__dropbox_tipova.current(self.__indeks_tip_snimka)
        red +=1
        self.__label_snimak = Label(self.__snimanje_panel, textvariable= self.__path)
        self.__label_snimak.grid(sticky = W, row = red, column= 1)
        self.__label_snimak['state'] = DISABLED
        self.__button_path = Button(self.__snimanje_panel,text= '...',command= self.pronadji_path)
        self.__button_path.grid(stick=W, row= red, column =2)
        self.__button_snimak = Button(self.__snimanje_panel,text= 'Otvori',command= self.otvori_dicom_snimak)
        self.__button_snimak.grid(stick=W, row= red, column =3)
        self.__button_dodaj = Button(self.__snimanje_panel,text= 'Dodaj', comman = self.dodaj_snimanje)
        self.__button_dodaj.grid(sticky= S, row= red + 1, column= 0)
        self.__button_snimak['state'] = DISABLED






        self.transient(master)
        self.focus_force()
        self.grab_set()
        self.__otkazan = True



class ProzorIzmena(Toplevel):

    @property
    def otkazan(self):
        return self.__otkazan

    def otvori_dicom_snimak(self):
        staza_do_datoteke = self.__path.get()
        if staza_do_datoteke != '':
            dataset = pydicom.dcmread(staza_do_datoteke, force= True)
            print(dataset)
        else:
            messagebox.showerror('Greska pri ucitavanju', 'Niste uneli stazu do datoteke')
        DICOMProzor(self, dataset)

    def validacija_lekar(self):
        ime = self.__lekar_ime.get()
        prezime = self.__lekar_prezime.get()
        lekar = Lekar(ime, prezime,'Opsta praksa')
        return lekar

    def validacija_datum_i_vreme(self):
        godina = self.__godina.get()
        mesec = self.__mesec.get()
        dan = self.__dan.get()
        sat = self.__sat.get()
        minut = self.__minut.get()
        sekund = self.__sekund.get()
        try:
            datum_i_vreme = datetime.datetime(godina,mesec,dan,sat,minut,sekund)
        except:
            messagebox.showerror('Greska','Datum koji ste uneli nije validan!')
        pacijent = self.__snimanje.pacijent
        if not pacijent.datum_rodjenja < datum_i_vreme.date() < datetime.date.today():
            messagebox.showerror('Greska!', 'Uneli ste los datum!')
            return None
        else:
            return datum_i_vreme
    
        
    def pronadji_path(self):

        staza_do_datoteke = filedialog.askopenfilename(
                title="Otvaranje",
                filetypes=[("All files", "*.*"), ("DICOM files", "*.dcm")])

        self.__path.set(staza_do_datoteke)

    def validacija_snimak(self):
        snimak = self.__path.get()
        for snimanje in self.__podaci.snimanja:
            if snimak == snimanje.snimak:
                messagebox.showerror('Greska!','Snimak je vec zakacen!')
                return None
        return snimak

    def sacuvaj_izmene(self):
        if self.validacija_lekar:
            self.__snimanje.lekar = self.validacija_lekar()
        else:
            messagebox.showerror('Greska', "Ime lekara je prekratko")
            return None
        if self.validacija_datum_i_vreme:
            self.__snimanje.datum_i_vreme = self.validacija_datum_i_vreme()
        else:
            return None
        self.__snimanje.snimak = self.validacija_snimak()
        self.__snimanje.izvestaj = self.__izvestaj.get()
        self.__snimanje.tip = self.__tip_snimka.get()

        self.config(cursor="wait")
        Podaci.snimanje(self.__podaci)
        self.config(cursor="")

        self.__otkazan = False
        self.destroy()


    def __init__(self, master, podaci, snimanje):

        super().__init__(master)
        self.__podaci = podaci
        self.__snimanje = snimanje
        self.__otkazan = True


        self.__path = StringVar(master)
        self.__path.set(self.__snimanje.snimak)
        self.__godina = IntVar(master)
        self.__godina.set(self.__snimanje.datum_i_vreme.year)
        self.__dan = IntVar(master)
        self.__dan.set(self.__snimanje.datum_i_vreme.day)
        self.__mesec= IntVar(master)
        self.__mesec.set(self.__snimanje.datum_i_vreme.month)
        self.__sat = IntVar(master)
        self.__sat.set(self.__snimanje.datum_i_vreme.hour)
        self.__sekund = IntVar(master)
        self.__sekund.set(self.__snimanje.datum_i_vreme.second)
        self.__minut = IntVar(master)
        self.__minut.set(self.__snimanje.datum_i_vreme.minute)
        self.__lekar_ime = StringVar(master)
        self.__lekar_ime.set(self.__snimanje.lekar.ime)
        self.__lekar_prezime = StringVar(master)
        self.__lekar_prezime.set(self.__snimanje.lekar.prezime)
        self.__tip_snimka = StringVar(master)
        self.__tip_snimka.set(self.__snimanje.tip)
        self.__izvestaj = StringVar(master)
        self.__izvestaj.set(self.__snimanje.izvestaj)

        self.iconbitmap('radiologija_ico.ico')
        self.title('Dodavanje snimanja')


        self.__snimanje_panel = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        self.__snimanje_panel.pack(fill=BOTH, expand=1)

        self.__vrste_snimaka = [
                                'Computed tomography (CT)',
                                'Fluoroscopy',
                                'Magnetic resonance imaging (MRI)',
                                'Magnetic resonance angiography (MRA)',
                                'Mammography',
                                'X-rays (XR)',
                                'Positron emission tomography (PET)',
                                'Ultrasound']

        red = 0
        Label(self.__snimanje_panel, text= 'Ime i prezime pacijenta: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Ime i prezime lekara: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Datum i vreme snimanja (Godina/Mesec/Dan/Sat/Minut/Sekund): ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Izvestaj: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Tip snimanja: ').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanje_panel, text= 'Putanja do snimka: ').grid(row=red, sticky=E)
        red += 1

        kolona = 1
        red = 0
        self.__labela_pacijent = Label(self.__snimanje_panel, text='{} {}'.format(self.__snimanje.pacijent.ime, self.__snimanje.pacijent.prezime) )
        self.__labela_pacijent.grid(sticky= W, row= red, column=1)
        red +=1
        self.__entry_lekar_ime = Entry(self.__snimanje_panel, textvariable = self.__lekar_ime)
        self.__entry_lekar_ime.grid(sticky = W, row = red, column= 1)
        self.__entry_lekar_prezime = Entry(self.__snimanje_panel, textvariable = self.__lekar_prezime)
        self.__entry_lekar_prezime.grid(sticky = W, row = red, column= 2)
        red +=1
        self.__spinbox_godina = Spinbox(self.__snimanje_panel, width=10,increment=1,from_=1900, to=2100,textvariable = self.__godina)
        self.__spinbox_godina.grid(sticky= W, row= red, column= kolona)
        kolona += 1 
        self.__spinbox_mesec = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=12,textvariable = self.__mesec)
        self.__spinbox_mesec.grid(sticky= W, row= red, column= kolona)
        kolona += 1 
        self.__spinbox_dan = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=31, textvariable = self.__dan)
        self.__spinbox_dan.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_sat = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=24, textvariable = self.__sat)
        self.__spinbox_sat.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_minut = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=60, textvariable = self.__minut)
        self.__spinbox_minut.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        self.__spinbox_sekunda = Spinbox(self.__snimanje_panel, width=5,increment=1,from_=1, to=60, textvariable = self.__sekund)
        self.__spinbox_sekunda.grid(sticky= W, row= red, column= kolona)
        kolona += 1
        red += 1
        self.__entry_izvestaj = Entry(self.__snimanje_panel, textvariable = self.__izvestaj)
        self.__entry_izvestaj.grid(sticky = W, row = red, column= 1)
        red += 1
        self.__dropbox_tipova = ttk.Combobox(self.__snimanje_panel,width=30, values= self.__vrste_snimaka, textvariable = self.__tip_snimka )
        self.__dropbox_tipova.grid(sticky= W, row= red, column = 1)
        red += 1
        self.__label_snimak = Label(self.__snimanje_panel, textvariable= self.__path)
        self.__label_snimak.grid(sticky = W, row = red, column= 1)
        self.__label_snimak['state'] = DISABLED
        self.__button_path = Button(self.__snimanje_panel,text= '...',command= self.pronadji_path)
        self.__button_path.grid(stick=W, row= red, column =2)
        self.__button_snimak = Button(self.__snimanje_panel,text= 'Otvori', command= self.otvori_dicom_snimak)
        self.__button_snimak.grid(stick=W, row= red, column =3)
        self.__button_dodaj = Button(self.__snimanje_panel,text= 'Izmena', command= self.sacuvaj_izmene)
        self.__button_dodaj.grid(sticky= S, row= red + 1, column= 0)

        
        self.transient(master)
        self.focus_force()
        self.grab_set()



class DICOMSlika(Toplevel):

    def __init__(self,master,dataset):

        super().__init__(master)
        self.__dataset = dataset

        self.__slika_label = Label(self)
        self.__slika_label.pack(side=LEFT, expand=1)
        pil_slika = pydicom_PIL.get_PIL_image(self.__dataset)
        slika = ImageTk.PhotoImage(pil_slika)
        self.__slika_label['image'] = slika
        self.__slika_label.image = slika

        self.iconbitmap('radiologija_ico.ico')
        self.title('Dodavanje snimanja')



        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient(master)
        self.focus_force()
        self.grab_set()

class DICOMProzor(Toplevel):

    def __init__(self,master,dataset):

        super().__init__(master)
        self.__dataset = dataset

        self.__slika_label = Label(self)
        self.__slika_label.pack(side=LEFT, expand=1)
        pil_slika = pydicom_PIL.get_PIL_image(self.__dataset)
        slika = ImageTk.PhotoImage(pil_slika)
        self.__slika_label['image'] = slika
        self.__slika_label.image = slika
        

        unos_frame = Frame(self, borderwidth=2, relief="ridge", padx=10, pady=10)
        unos_frame.pack(side=RIGHT, fill=BOTH, expand=1)

        red = 1
        Label(unos_frame, text= 'Patient ID:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Patient’s Name:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Patient’s Birth Date:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Date:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Modality:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Study Description:').grid(row=red, sticky=E)
        red += 1
        Label(unos_frame, text= 'Referring Physician’s Name:').grid(row=red, sticky=E)

        red = 1
        Label(unos_frame, text= self.__dataset.PatientID).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.PatientName).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.PatientBirthDate).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.DateTime).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.Modality).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.StudyDescription).grid(row=red,column=1, sticky=E)
        red += 1
        Label(unos_frame, text= self.__dataset.ReferringPhysicianName).grid(row=red,column=1, sticky=E)


        







        self.iconbitmap('radiologija_ico.ico')
        self.title('Dodavanje snimanja')



        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient(master)
        self.focus_force()
        self.grab_set()
