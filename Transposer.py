from os import listdir, remove
import PySimpleGUI as sg
from fpdf import FPDF
from sys import exit
from pickle import dump, load


class App():
    def __init__(self):
        self.theme = "Dark"
        self.curr_sheet = None

    class Sheet:
        def __init__(self, name = 'Song Name', author = 'Author',  source_text = 'music sheet text', og_key = 'E'):
            self.name = name
            self.author = author
            self.text = source_text
            self.og_key = og_key

    class PDF(FPDF):
        def lines(self):
            self.rect(5.0, 5.0, 200.0,287.0)
        
        def texts(self, txt):
            self.set_xy(10.0,80.0)    
            self.set_text_color(76.0, 32.0, 250.0)
            self.set_font('Arial', '', 12)
            self.multi_cell(0,10,txt)
            

    def main(self):
        sg.theme(self.theme)

        # Getting the saved Sheets
        col = []
        for i in listdir('tmp'):
            col.append(i.removesuffix(".pickle"))
        
        # Layout
        if len(col) != 0:
            lay = [
                [sg.Stretch(), sg.Frame("Your Sheets",  
                    [[sg.I("Search", size=(20,1), enable_events=True, key='-s-')], 
                    [sg.Listbox(col, key='s', size=(40, 5))]], 
                key ='frame'), sg.Stretch()],
                [sg.B("Delete Sel. Sheet", key='-D-'), sg.B("Load Sel. Sheet", key='-L-'), sg.B("Create New Sheet", key='-N-')]]
            
            flag = 0
            prev = "Search"

            # Active window
            win = sg.Window("Sheet Transposer", lay)
            while True:
                e, v = win.read(timeout=0) 
                
                if e == sg.WINDOW_CLOSED:
                    win.close(); break
                
                # Load
                if e == '-L-':
                    try:
                        sheet = load(open(f"tmp/{v['s'][0]}.pickle", "rb"))  # good place for self.curr_sheet
                    except:
                        sg.popup('Please select a file from your sheets')
                        continue

                    win.close()
                    self.Source_Editor(sheet)
                    break

                    

                # New Sheet
                if e == '-N-':
                    win.close()
                    self.Source_Editor()
                    break
                
                #delete
                if e == '-D-':
                    try:
                        remove(f"tmp/{v['s'][0]}.pickle")
                    except:
                        sg.popup('Please select a file from your sheets')
                        continue
                    
                    win.close()
                    self.main()
                    break


                # search
                if v['-s-'] != 'Search':
                    if v['-s-'] != prev:
                        search = v['-s-']
                        new_values = [x for x in col if search in x]
                        win['s'].update(new_values)
                        prev =  v['-s-']
                        flag = 1
                    else:
                        flag = 0
                else:
                    if flag != 0:
                        win['s'].update(col)
                        flag = 1
        else:
            lay = [[sg.B("Create New Sheet", key='-N-')]]
            win = sg.Window("Sheet Transposer", lay)
            while True:
                e, v = win.read(timeout=0) 
                
                if e == sg.WINDOW_CLOSED:
                    win.close(); break
                
                if e == '-L-':
                    sheet = load(open(f"tmp/{v['s'][0]}.pickle", "rb"))
                    self.Source_Editor(sheet)
                    win.close; break
                
                if e == '-N-':
                    win.close()
                    self.Source_Editor()
                    break
            
        



    def Source_Editor(self, sheet = Sheet()):
        sg.theme(self.theme)
        # reference for "Key" value
        major = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        
        # window Layout
        layout = [
            [sg.Text("Chord Transposer", font='bold', justification='c',  expand_x=True, expand_y=True)],
            [sg.T("Original Key:"), sg.Input(f"{sheet.og_key}", size =(10,1), key='-K1-'), sg.B('Set Key', key='set')],
            [sg.Input(f"{sheet.name}",  key='n')],
            [sg.Input(f"{sheet.author}", key='a')], 
            [sg.T("Please put brackets around ONLY the chords you want transposed. Ex: {C#m}\n"),sg.Stretch(), sg.Button(image_filename="assets/light.png", image_subsample=10,key ='mode')],
            [sg.Multiline(default_text = sheet.text, size=(80,30),key = '-T-', focus=True)],  #sg.Slider(range=(-12, 12), key='-KEY-', default_value= 0, orientation='h')
            [
                sg.B('Load', key='-L-'), sg.B('Save', key='-S-'), sg.Stretch(), 
                sg.Text(text='New Key:'), sg.T(f"{sheet.og_key}",key='-K-'), sg.B('+', key='+'),sg.B('-', key='-'), sg.Stretch(), 
                sg.B("Preview", key='-P-'), sg.B("Get Pdf", key='-Ok-')],

            [sg.Text('Made By Matheus Berbet', font='Times', text_color='gray' ), sg.Stretch(), sg.Text('Mattynb on GitHub', font='Times', text_color='gray' )]
        ]

        # window
        win = sg.Window('Transposer GUI', layout, finalize=True, element_justification='center', relative_location=(0,100))
        
        # active window
        while True:
            e, v = win.read(timeout=10)
            

            # exit
            if e == sg.WINDOW_CLOSED:
                win.close()
                break
            
            # color
            if e == 'mode':
                if self.theme == 'SystemDefault1':
                    win['mode'].update(image_filename="assets/dark.png", image_subsample=10)
                    self.theme = "Dark"
                    win.close()
                    self.Source_Editor(sheet)
                    break

                if self.theme == "Dark":
                    win['mode'].update(image_filename="assets/light.png", image_subsample=10)
                    self.theme = "SystemDefault1"
                    win.close()
                    self.Source_Editor(sheet)
                    break

            # load
            if e == '-L-':
                win.close()
                self.main()
                break
            
            # save
            if e == '-S-':
                sheet.name = v['n']
                sheet.author = v['a']
                sheet.text = v['-T-']
                sheet.og_key = v['-K1-']
                dump(sheet, open(f'tmp/{sheet.name}_by_{sheet.author}.pickle', "wb"))

            # preview
            if e == '-P-': 
                text = self.Process_text(v['-T-'], win['-K-'].DisplayText, sheet)
                self.Final_Preview(text)
            
            # make pdf
            if e == '-Ok-':
                text = self.Process_text(v['-T-'], win['-K-'].DisplayText, sheet)
                self.make_pdf(sheet, text, win['-K-'].DisplayText)
                sg.Popup("Pdf Ready")

            # increase key
            if e == '+':
                try:
                    i = major.index(win['-K-'].DisplayText) + 1
                    if i >= len(major):
                        i = i - len(major)
                    win['-K-'].update(major[i])
                except:
                    sg.popup("Please insert original key.\nEx: 'C#'")

            # decrease key
            if e == '-':
                try:
                    i = major.index(win['-K-'].DisplayText) - 1
                    if i <= 0:
                        i = len(major) - 1
                    win['-K-'].update(major[i])
                except: 
                    sg.popup("Please insert original key.\nEx: 'C#'")
            
            # og key change
            if e == 'set':
                sheet.og_key = v['-K1-']
                win['-K-'].update(v['-K1-'])
            


    def Final_Preview(self, text):
        lay = [[sg.Text(text,key = '-T-')]]
        win = sg.Window("Preview", lay)
        while True:
            e, v = win.read()
            if e == sg.WINDOW_CLOSED:
                win.close()
                break


    def Transpose_Chord(self, chord, key, sheet):
        major = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        minor = ['Am', 'A#m', 'Bm', 'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m']
        major_b = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
        minor_b = ['Am', 'Bbm', 'Bm', 'Cm', 'Dbm', 'Dm', 'Ebm', 'Em', 'Fm', 'Gbm', 'Gm', 'Abm']
        seventh = ['A7', 'A#7', 'B7', 'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7']
        seventh_min = ['Am7', 'A#m7', 'Bm7', 'Cm7', 'C#m7', 'Dm7', 'D#m7', 'Em7', 'Fm7', 'F#m7', 'Gm7', 'G#m7']
        scales = [major_b, minor_b, major, minor,seventh, seventh_min]

        for s in scales:
            if s.__contains__(chord):
                i = s.index(chord) + (major.index(sheet.og_key) - major.index(key))
                if i >= len(s):
                    i = i - len(s)
                return s[i]
        

        if chord != "":
            sg.Popup(f"chord \"{chord}\" not in database.\nPlease try place brackets around root of note.\n\tEx: [C]maj7   or [G]/[B]")
        return chord



    def Process_text(self, text, key, sheet):
        chord = ''
        new_text = ''

        # go through all chars
        i = 0
        while i < len(text):

            # until it finds '['
            if text[i] == '{': 
            
                # then it adds every consequent char (up to 10) to chord var 
                for j in range(i + 1, i+10): 
                    c3 = text[j]                
                    
                    if c3 == '/':
                        new_text = new_text +  self.Transpose_Chord(chord.replace(' ', ''), key, sheet) + c3
                        chord = ''
                    else:
                        if c3 != '}': chord = chord + text[j]

                    if c3 == '}':
                        c = self.Transpose_Chord(chord.replace(' ', ''), key, sheet)
                        new_text = new_text +  c
                    
                        chord = ''
                        i = j
                        break 
                    
            else:
                c2 = text[i]
                if c2 != '}':
                    new_text = new_text + c2
            
            i += 1

        return new_text


    def make_pdf(self, sheet, txt, key):
        # new pdf
        pdf = self.PDF()

        # new page
        pdf.add_page(); pdf.lines()
        
        # title
        pdf.set_font('Arial', 'B', 16); pdf.cell(60, 10, f'{sheet.name}', 0, 1, 'L')
        
        # author
        if sheet.author != None: 
            pdf.set_font('Arial','I', 10)
            pdf.cell(60, 10, f"By {sheet.author}", 0, 1, 'L')

        # key
        pdf.cell(60, 10, f"Key: {key}", 0, 1, 'L')
        # blank space
        pdf.cell(60, 10, ' ', 0, 1, 'L'); pdf.cell(60, 10, ' ', 0, 1, 'L')

        
        # content/cifra
        pdf.set_font('Arial','', 12)
        c = 0
        for l in txt.splitlines():
            if c > 20: # too many lines. New page
                pdf.add_page(); pdf.lines(); c = 0
            pdf.cell(60, 10,l, 0, 1, 'L')
            c+=1 

        # output
        pdf.output(f"pdfs/{sheet.name}.pdf", 'F')


if __name__ == '__main__':
    App().main()
