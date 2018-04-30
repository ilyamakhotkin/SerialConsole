import tkinter
import serial
import threading


class Application(tkinter.Frame):
    """ docstring """
    def __init__(self, master=None):
        super().__init__(master)
        self.history_index = 0
        self.history = []
        self.ser = serial.Serial()
        self.read_thread = threading.Thread(None, self.serial_reader, '', ())
        self.create_widgets()

    def button1_action(self):
        """This action will be performed upon the press of button 1"""
        print('BUTTON1 PRESSED')
        self.ser.write(b'boot t 192.168.1.100 m7.elf.net\n')

    def button2_action(self):
        """This action will be performed upon the press of button 2"""
        print('BUTTON2 PRESSED')
        self.ser.write(b'\nlog version\n')

    def button3_action(self):
        """This action will be performed upon the press of button 3"""
        print('BUTTON3 PRESSED')
        self.ser.write(b'\nlog timea ontime 0.1\n')

    def finish_it(self):
        """This action will be performed upon the press of the press of red cross"""
        print('closing')
        self.ser.close()
        self.read_thread.join()
        root.destroy()

    def up_button(self, args):
        """This action will be performed upon the press of up button on keyboard"""
        self.history_index -= 1
        if self.history_index < 0:
            self.history_index = len(self.history)-1

        self.commwindow.delete(0,'end')
        print("length " + str(len(self.history)) + ' index ' + str(self.history_index))
        self.commwindow.insert(0, self.history[self.history_index])

    def down_button(self, args):
        """This action will be performed upon the press of down button on keyboard"""
        self.history_index -= 1
        if self.history_index < 0:
            self.history_index = len(self.history) - 1

        self.commwindow.delete(0, 'end')
        print("length " + str(len(self.history)) + ' index ' + str(self.history_index))
        self.commwindow.insert(0, self.history[self.history_index])

    def mouse_click(self, args):
        """ WHen console window is clicked, set command window in focus"""
        print('clicked mouse')
        self.commwindow.focus_set()

    def connect_serial(self):
        """Opens serial port"""
        print('Connecting serial port ' + self.port_string.get())
        self.ser.port = self.port_string.get()
        self.ser.baudrate = self.baud_string.get()
        self.ser.inter_byte_timeout = 0.1
        self.ser.open()

        if self.ser.is_open:
            self.read_thread.start()
            self.port_status_label['text'] = 'CONNECTED'
            self.port_status_label['foreground'] = 'green'
            root.bind('<Return>', self.comm_send)
            root.bind("<KeyPress-Up>", self.up_button)
        else:
            self.port_status_label['foreground'] = 'red'
        root.protocol("WM_DELETE_WINDOW", self.finish_it)

    def clear_screen_function(self):
        """ Clears screen"""
        print('Clearing Screen')
        self.console["state"] = "normal"
        self.console.delete(1.0 ,"end")
        self.console["state"] = "disabled"

    def serial_reader(self):
        """ Runs in separate thread """
        while True:
            # print("Waiting to read")
            s = self.ser.read(1000)
            print("read " + str(len(s)))
            if len(s) == 0:
                print("read thread returning")
                exit(0)
            self.console["state"] = "normal"
            self.console.insert("end", s)
            self.console["state"] = "disabled"
            self.console.see("end")

    def comm_send(self, *args):
        """ sends command over serial, and prints it to console"""
        command = self.commwindow.get()
        self.commwindow.delete(0, "end")
        if len(command) > 0:
            self.console["state"] = "normal"
            self.console.insert("end", command + '\n')
            self.console["state"] = "disabled"
            self.console.see("end")
            if self.history_index == -1:
                self.history.append(command)
                if len(self.history) > 10:
                    self.history.pop[0]
        command += '\n'
        self.ser.write(bytes(command, 'utf-8'))
        self.history_index = -1

    def create_widgets(self):
        """ creates gui"""
        # ROW0
        self.port_label = tkinter.Label(text='PORT', width=5)
        self.port_label.grid(column=0, row=0)

        self.port_string = tkinter.StringVar()
        self.port_string.set('COM2')
        self.port = tkinter.Entry(textvariable=self.port_string, width=6 )
        self.port.grid(column=1, row=0)

        self.baud_label =  tkinter.Label(text='BAUD')
        self.baud_label.grid(column=2, row=0)

        self.baud_string = tkinter.StringVar()
        self.baud_string.set('115200')
        self.baud = tkinter.Entry(textvariable=self.baud_string, width=10)
        self.baud.grid(column=3, row=0)

        self.port_status_label = tkinter.Label(text='DISCONNECTED')
        self.port_status_label.grid(column=6, row=0)

        self.connect_button = tkinter.Button(text='CONNECT', command=self.connect_serial)
        self.connect_button.grid(column=7, row=0)

        self.clear_screen_button = tkinter.Button(text='CLEAR SCREEN', command=self.clear_screen_function)
        self.clear_screen_button.grid(column=8, row=0, sticky=tkinter.E)

        # ROW1
        self.console = tkinter.Text(state="disabled")
        self.console.grid(column=0, row=1, columnspan=9, sticky=(tkinter.N, tkinter.W, tkinter.S, tkinter.E))
        root.columnconfigure(8, weight=1)
        root.rowconfigure(1, weight=1)

        self.s = tkinter.Scrollbar(orient=tkinter.VERTICAL, command=self.console.yview)
        self.s.grid(column=9, row=1, sticky=(tkinter.N, tkinter.W, tkinter.S))
        self.console['yscrollcommand'] = self.s.set

        # ROW2
        self.button1 = tkinter.Button(text='BOOT', command=self.button1_action)
        self.button1.grid(column=0, row=2)

        self.button2 = tkinter.Button(text='VERSION', command=self.button2_action)
        self.button2.grid(column=1, row=2)

        self.button3 = tkinter.Button(text='TIME', command=self.button3_action)
        self.button3.grid(column=2, row=2)

        # ROW3
        self.commwindow = tkinter.Entry()
        self.commwindow.grid(column=0, row=3, columnspan=9, sticky=(tkinter.E, tkinter.N, tkinter.W))

        self.console.bind('<1>', self.mouse_click)
        self.console.bind('<Double-1>', self.mouse_click)
        # l.bind('<1>', lambda e: l.configure(text='Clicked left mouse button'))


root = tkinter.Tk()
root.title('Ilya Console')
app = Application(master=root)
app.mainloop()
