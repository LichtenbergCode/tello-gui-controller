from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import threading 

from PIL import Image, ImageTk, ImageOps
from djitellopy import tello
from time import sleep 
from sys import exit

class Window(ttk.Window):
    def __init__(self, size, name):
        super().__init__(themename = 'lumen') #sandstone
        self.geometry(f'{size[0]}x{size[1]}')
        self.title(name)
        self.iconbitmap('.\\Resources\\drone-thin.ico')
        self.resizable(False, False)
        self.columnconfigure((0,1), weight = 1, uniform = 'a')
        self.rowconfigure((0,1), weight = 1, uniform = 'a')
        self.left_button_pressed = False
        self.button_status1 = 'None'
        self.button_status2 = 'None'
        self.button_status3 = 'None'

        ########## DRONE ##########
        self.drone = tello.Tello()
        self.drone.connect()
        self.drone.streamon()
        ########## CALLING METHODS ##########
        self.menu()
        self.events()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.creating_widgets()
        self.creating_video()

        ########## Threading ##########
        thread1 = threading.Thread(target = self.drone_send, daemon = True)
        thread2 = threading.Thread(target = self.update_indicators, daemon = True)
        thread1.start()
        thread2.start()

        ########## Loop ##########
        self.mainloop()

    def menu(self):
        self.menu = ttk.Menu()

        #sub menu 
        self.file_menu = ttk.Menu(self.menu, tearoff = False)
        self.button_take_of = self.file_menu.add_command(label = 'Take Of', command = lambda:self.menu_events('TKOF'))
        self.button_Land = self.file_menu.add_command(label = 'Land', command = lambda:self.menu_events('LAND'))

        self.menu.add_cascade(label = 'Drone', menu = self.file_menu)

        # running the menu 
        self.configure(menu = self.menu)
    
    def menu_events(self, variable):
        self.button_status3 = variable
        sleep(0.5)
        self.button_status3 = 'NONE'

    def creating_widgets(self):

        self.direction = FrameControl(self,
                                        'primary',
                                        '.\\Resources\\forward.png',
                                        '.\\Resources\\left.png',
                                        '.\\Resources\\right.png',
                                        '.\\Resources\\backward.png',
                                        'FORWARD',
                                        'LEFT',
                                        'RIGHT',
                                        'BACKWARD')
        self.direction.grid(column=1, row = 1, sticky = 'nswe')

        self.direction2 = FrameControl(self,
                                        'secondary',
                                        '.\\Resources\\up2.png',
                                        '.\\Resources\\one.png',
                                        '.\\Resources\\second.png',
                                        '.\\Resources\\down.png',
                                        'UP',
                                        'TURNL',
                                        'TURNR',
                                        'DOWN')
        
        self.direction2.grid(column = 0, row = 1, sticky = 'nswe')

        self.indicators = FrameIndicator(self, 50, 70)
        self.indicators.grid(column = 0, row = 0, sticky = 'nswe')

    def events(self):
        # Basic movements
        self.bind('<KeyPress-Up>', lambda _: self.event_func('FORWARD'))
        self.bind('<KeyPress-Down>', lambda _: self.event_func('BACKWARD'))
        self.bind('<KeyPress-Left>', lambda _: self.event_func('LEFT'))
        self.bind('<KeyPress-Right>', lambda _: self.event_func('RIGHT'))
        self.bind('<KeyRelease-Up>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-Down>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-Left>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-Right>', lambda _: self.event_func('NONE'))
        self.bind('<KeyPress-a>', lambda _: self.event_func('TURNL'))
        self.bind('<KeyPress-d>', lambda _: self.event_func('TURNR'))
        self.bind('<KeyPress-w>', lambda _: self.event_func('UP'))
        self.bind('<KeyPress-s>', lambda _: self.event_func('DOWN'))
        self.bind('<KeyRelease-a>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-d>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-w>', lambda _: self.event_func('NONE'))
        self.bind('<KeyRelease-s>', lambda _: self.event_func('NONE'))

        # TakeOf/Land
        self.bind('<KeyPress-i>', lambda _: self.event_func('TKOF'))
        self.bind('<KeyRelease-i>', lambda _: self.event_func('NONE'))
        self.bind('<KeyPress-q>', lambda _: self.event_func('LAND'))
        self.bind('<KeyRelease-q>', lambda _: self.event_func('NONE'))

    def event_func(self, variable):
        self.button_status3 = variable

    def on_closing(self): # This is the routine that we're going to use at the moment that we close the window 
        self.button_status3 = 'LAND'
        sleep(3)

        self.drone.streamoff()
        self.drone.end()
        self.quit()
        self.destroy()
        print('Good Bye')
        exit

    def creating_video(self):
        self.frame_video = ttk.Frame()
        self.frame_video.grid(row=0, column=1, sticky='nswe')
        self.label_video= ttk.Label(self.frame_video)
        self.label_video.place(anchor = CENTER,  relx = 0.5, rely = 0.5)

        self.delay = 15 # 100/15 sec.
        self.update()

    def update(self):
        img = self.drone.get_frame_read().frame
        img = Image.fromarray(img)
        img = ImageOps.scale(image = img, factor = 0.5)
        self.photo = ImageTk.PhotoImage(image = img)
        self.label_video.configure(image = self.photo) 

        self.button_status1 = self.direction.send_info
        self.button_status2 = self.direction2.send_info
 
        self.after(self.delay, self.update)

    def update_indicators(self):
        while True: 
            self.indicators.meter_temp.configure(amountused = self.drone.get_temperature())
            self.indicators.meter_battery.configure(amountused = self.drone.get_battery())
            print(f'temperature:{type(self.drone.get_temperature())},{self.drone.get_temperature()}')
            print(f'battery:{type(self.drone.get_battery())}, {self.drone.get_battery()}')
            sleep(1.5)

    def drone_send(self):

        while True:
            speed = self.indicators.speed2
            lr, fb, up, yv = 0, 0, 0, 0

            match self.button_status1 :
                case 'FORWARD':
                    fb = speed
                case 'BACKWARD': 
                    fb = -speed
                case 'LEFT':
                    lr = -speed
                case 'RIGHT':
                    lr = speed

            match self.button_status2:
                case 'TURNL':
                    yv = -speed
                case 'TURNR':
                    yv = speed
                case 'UP':
                    up = speed
                case 'DOWN':
                    up = -speed
                case _:
                    pass

            match self.button_status3 :
                case 'FORWARD':
                    fb = speed
                case 'BACKWARD': 
                    fb = -speed
                case 'LEFT':
                    lr = -speed
                case 'RIGHT':
                    lr = speed
                case 'TURNL':
                    yv = -speed
                case 'TURNR':
                    yv = speed
                case 'UP':
                    up = speed
                case 'DOWN':
                    up = -speed
                case 'TKOF':
                    if not self.drone.is_flying:
                        try: 
                            self.drone.takeoff()
                            sleep(2)
                        except:
                            print('Take Of Failed')
                    else: print('THE DRONE IS FLYING')
                case 'LAND':
                    if self.drone.is_flying:
                        try:
                            self.drone.land()
                            sleep(3)
                        except:
                            print('Land Failed')
                    else: print('THE DRONE IS NOT FLYING')
                case _:
                    pass

            if self.drone.is_flying:
                try: 
                    self.drone.send_rc_control(lr, fb, up, yv)
                except: 
                    print('Rc Control Failed')

            sleep(0.20)

class FrameControl(ttk.Frame):
    def __init__(self, 
            root, 
            button_style, 
            path_button1, 
            path_button2, 
            path_button3, 
            path_button4,
            command_button1,
            command_button2,
            command_button3,
            command_button4):
        super().__init__(master = root)

        self.button_style = button_style
        self.path_button1 = path_button1
        self.path_button2 = path_button2
        self.path_button3 = path_button3
        self.path_button4 = path_button4
        self.command1 = command_button1
        self.command2 = command_button2
        self.command3 = command_button3
        self.command4 = command_button4
        self.command_not_info = 'NONE'
        self.send_info = 'NONE'
        self.root = root
        

        self.columnconfigure((0, 4), weight = 2, uniform='a')
        self.columnconfigure(2, weight = 9, uniform = 'a')
        self.columnconfigure((1,3), weight = 7, uniform = 'a')

        self.rowconfigure((0, 5), weight = 1, uniform = 'a')
        self.rowconfigure((1, 4), weight = 3, uniform = 'a')
        self.rowconfigure((2, 3), weight = 4, uniform = 'a')

        self.images()
        self.buttons()
        self.events()

    def images(self):
        # Images # 
        image_first_button = Image.open(self.path_button1).resize((70, 70))
        image_second_button = Image.open(self.path_button2).resize((70, 70))
        image_third_button = Image.open(self.path_button3).resize((70, 70))
        image_fourth_button = Image.open(self.path_button4).resize((70, 70))

        self.image_first_button_tk = ImageTk.PhotoImage(image_first_button)
        self.image_second_button_tk = ImageTk.PhotoImage(image_second_button)
        self.image_third_button_tk = ImageTk.PhotoImage(image_third_button)
        self.image_fourth_button_tk = ImageTk.PhotoImage(image_fourth_button)

        self.left_button_pressed = False
        
    def buttons(self):
        self.button_1 = ttk.Button(self, 
                                    image = self.image_first_button_tk, 
                                    bootstyle = self.button_style) 
        
        self.button_2 = ttk.Button(self, 
                                    image = self.image_second_button_tk, 
                                    bootstyle = self.button_style)
        
        self.button_3 = ttk.Button(self, 
                                    image = self.image_third_button_tk, 
                                    bootstyle = self.button_style)
        
        self.button_4 = ttk.Button(self, 
                                    image = self.image_fourth_button_tk, 
                                    bootstyle = self.button_style)

        # grid
        self.button_1.grid(column = 2, row = 1, sticky = 'nswe', rowspan = 2, padx=8, pady = 5)
        self.button_2.grid(column = 1, row = 2, sticky = 'nswe', rowspan = 2)
        self.button_3.grid(column = 3, row =  2, sticky = 'nswe', rowspan = 2)
        self.button_4.grid(column = 2, row = 3, sticky = 'nswe', rowspan = 2, padx=8, pady = 5)

    def events(self):
        self.button_1.bind('<ButtonPress-1>', lambda _: self.event_func(self.command1))
        self.button_2.bind('<ButtonPress-1>', lambda _: self.event_func(self.command2))
        self.button_3.bind('<ButtonPress-1>', lambda _: self.event_func(self.command3))
        self.button_4.bind('<ButtonPress-1>', lambda _: self.event_func(self.command4))

        self.button_1.bind('<ButtonRelease-1>', lambda _: self.event_func(self.command_not_info))
        self.button_2.bind('<ButtonRelease-1>', lambda _: self.event_func(self.command_not_info))
        self.button_3.bind('<ButtonRelease-1>', lambda _: self.event_func(self.command_not_info))
        self.button_4.bind('<ButtonRelease-1>', lambda _: self.event_func(self.command_not_info))

    def event_func(self, variable):
        self.send_info = variable

class FrameIndicator(ttk.Frame):
    def __init__(self, root, value1, value2):
        super().__init__(master = root)

        self.temperature = ttk.IntVar
        self.temperature = value1
        self.battery = ttk.IntVar
        self.battery = value2

        self.columnconfigure((1, 3, 5), weight = 1, uniform = 'a')
        self.columnconfigure((2, 4), weight = 28, uniform = 'a')
        self.rowconfigure((0, 3), weight = 1, uniform = 'a')
        self.rowconfigure(2, weight = 4, uniform = 'a')
        self.rowconfigure((1), weight = 10, uniform = 'a')
        self.creating_widgets()

    def creating_widgets(self):

        self.meter_temp = ttk.Meter(
                        self,
                        textright = '°C',
                        amounttotal = 100,
                        amountused =  0,
                        #stripethickness = 2,
                        interactive = False,
                        metertype = 'semi', #'full'
                        subtext = 'Temperature',
                        bootstyle = 'danger')
        self.meter_temp.grid(column = 4, row = 1, sticky = 'nswe')

        self.meter_battery = ttk.Meter(
                        self,
                        textright = '%',
                        amounttotal = 100,
                        amountused = self.battery,
                        #stripethickness=2,
                        interactive = False,
                        metertype = 'semi', #'full'
                        subtext = 'Battery',
                        bootstyle = 'success')
        self.meter_battery.grid(column = 2, row = 1, sticky = 'nswe')


        self.speed = ttk.IntVar(value = 50)
        self.scale = ttk.Scale(self, from_ = 0, 
                                to = 100, 
                                variable = self.speed, 
                                command = lambda _: self.scale_variable())
        self.scale.grid(column = 2, row = 2, rowspan = 3, sticky = NSEW)
        self.scale_variable()
    
    def scale_variable(self):
        self.speed2 = self.speed.get()
        label = ttk.Label(self, 
                            text = f'Speed = {self.speed2}', 
                            anchor = 'center',
                            font = "Calibri 24 bold")
        label.grid(column = 4, row = 2, sticky = 'nswe')

def main():
    root = Window((1300, 800), 'Drone Control')#1300, 800

if __name__ == '__main__': 
    main()