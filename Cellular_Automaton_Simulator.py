#!/usr/bin/env python3

import numpy as np
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import Image, ImageTk
import pygame, os
from pygame.locals import *


class Automaton:
    def __init__(self):
        self.row_len = 400
        self.height = 0
        self.scale = 1
        self.speed = 6 # range: 1-25
        self.colors = np.array([[  0,   0,   0], # Default colors
                                [113,  72,  17],
                                [ 17, 138,  20],
                                [155, 132,  36],
                                [149, 187,  17]], dtype='uint8')
        self.C = 3
        self.rule_list = []
        self.random_rule()
        self.IC_num = 0
        # Preview Image
        self.W = 200
        self.xW = 3*self.W
        self.IC = np.zeros(self.W, dtype='uint8')
        
    #------------------------------ Iteration ---------------------------------
    def iterate(self):
        self.row[:] = self.rule[np.roll(self.row, 1), self.row,
                                np.roll(self.row, -1)]

    def draw(self):
        p_arr = np.zeros((self.W,self.W), dtype='uint8')
        p_arr[0] = self.IC
        for i in range(1, self.W):
            p_arr[i] = self.rule[np.roll(p_arr[i - 1], 1), p_arr[i - 1],
                                 np.roll(p_arr[i - 1], -1)]
        p_RGB_arr = self.colors[p_arr]
        img = Image.fromarray(p_RGB_arr, 'RGB')
        img = img.resize((self.xW,self.xW))
        self.photo = ImageTk.PhotoImage(img)
        self.preview_cv.create_image(0,0, image=self.photo, anchor=tk.NW)

    #-------------------------- Initial Conditions ----------------------------
    # Animation
    def random_row(self):
        self.row[:] = np.random.randint(0, self.C, self.row_len)
        
    def FiveCell_row(self):
        self.row[:] = np.zeros(self.row_len)
        i = self.row_len//2
        self.row[i-2:i+3] = np.random.randint(0, self.C, 5)
    
    def OneCell_row(self):
        self.row[:] = np.zeros(self.row_len)
        self.row[self.row_len//2] = np.random.randint(1, self.C)

    def new_row(self):
        if self.IC_num == 0:
            self.random_row()
        elif self.IC_num == 1:
            self.FiveCell_row()
        else:
            self.OneCell_row()
    
    # Preview Image        
    def random_IC(self):
        self.IC[:] = np.random.randint(0, self.C, self.W)
    
    def FiveCell_IC(self):
        self.IC[:] = np.zeros(self.W)
        i = self.W//2
        self.IC[i-2:i+3] = np.random.randint(0, self.C, 5)
    
    def OneCell_IC(self):
        self.IC[:] = np.zeros(self.W)
        self.IC[self.W//2] = np.random.randint(1, self.C)
    
    def new_IC(self):
        self.IC_num = self.IC_num_var.get()
        if self.IC_num == 0:
            self.random_IC()
        elif self.IC_num == 1:
            self.FiveCell_IC()
        else:
            self.OneCell_IC()
        self.draw()

    #--------------------------------- Rules ----------------------------------
    def append_rule(self):
        self.rule_list = self.rule_list[-20:]   # Save previous 20 rules
        self.rule_list.append(self.rule)
    
    # Animation
    def random_rule(self):
        self.rule = np.random.randint(0, self.C, (self.C,self.C,self.C),
                                      dtype='uint8')
        self.append_rule()
    
    def back_rule(self):
        self.rule_list = self.rule_list[-1:] + self.rule_list[:-1]
        self.rule = self.rule_list[-1]
        C_num = self.rule.shape[0]
        if self.C != C_num:
            self.C = C_num
            self.new_row()

    def forward_rule(self):
        self.rule_list = self.rule_list[1:] + self.rule_list[:1]
        self.rule = self.rule_list[-1]
        C_num = self.rule.shape[0]
        if self.C != C_num:
            self.C = C_num
            self.new_row()
    
    # Preview Image
    def p_back_rule(self):
        self.rule_list = self.rule_list[-1:] + self.rule_list[:-1]
        self.rule = self.rule_list[-1]
        C_num = self.rule.shape[0]
        if self.C != C_num:
            self.C = C_num
            self.C_var.set(C_num)
            self.new_IC()
        else:
            self.draw()
        
    def p_forward_rule(self):
        self.rule_list = self.rule_list[1:] + self.rule_list[:1]
        self.rule = self.rule_list[-1]
        C_num = self.rule.shape[0]
        if self.C != C_num:
            self.C = C_num
            self.C_var.set(C_num)
            self.new_IC()
        else:
            self.draw()

    def new_rule(self):
        self.random_rule()
        self.draw()

    #------------------------------------ GUI ---------------------------------
    def color_change(self, event):
        if self.C != self.C_var.get():
            self.C = self.C_var.get()
            self.random_rule()
            self.new_IC()

    def rgb2hex(self, color):
        return '#%02x%02x%02x' % tuple(color)

    def hex2rgb(self, color):
        return tuple(int(color[i:i+2], 16) for i in (1,3,5))
    
    def set_color(self, i, button):
        hexcolor = askcolor(self.rgb2hex(self.colors[i]))[1]
        if hexcolor == None: # No color picked
            return
        button.config(background=hexcolor)
        self.colors[i] = self.hex2rgb(hexcolor)
        self.draw()
    
    def save_rule(self):
        filename = filedialog.asksaveasfilename(initialdir='./Saved',
                                                title='Save Current Rule')
        if len(filename) > 0:
            np.save(filename, self.rule)
    
    def load_rule(self):
        filename = filedialog.askopenfilename(initialdir='./Saved',
                                              title='Select Rule')
        if len(filename) > 0:
            self.rule = np.load(filename)
            self.append_rule()
            self.C = self.rule.shape[0]
            self.C_var.set(self.C)
            self.new_IC()
            
    def save_palette(self):
        filename = filedialog.asksaveasfilename(initialdir='./Palettes',
                                            title='Save Current Color Palette')
        if len(filename) > 0:
            np.save(filename, self.colors)
            
    def load_palette(self):
        filename = filedialog.askopenfilename(initialdir='./Palettes',
                                              title='Select Color Palette')
        if len(filename) > 0:
            self.colors = np.load(filename)
            buttons = self.color_fr.grid_slaves(column=1)
            buttons.reverse()
            for i in range(5):
                buttons[i].config(background=self.rgb2hex(self.colors[i]))
            self.draw()

    def on_closing(self):
        self.finished.set(True)
        self.root.destroy()
        
    def setup_GUI(self):
        self.root = tk.Tk()
        self.root.title('Cellular Automaton Simulator')
        self.root.lift()
        self.root.state('zoomed') #self.root.attributes('-zoomed', True) <= On Linux 
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.menu.add_command(label='Save Rule', command=self.save_rule)
        self.menu.add_command(label='Load Rule', command=self.load_rule)
        self.menu.add_command(label='Save Palette', command=self.save_palette)
        self.menu.add_command(label='Load Palette', command=self.load_palette)
        self.finished = tk.IntVar(value=False)
        self.root.protocol(name="WM_DELETE_WINDOW", func=self.on_closing)
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.row_len_var = tk.IntVar(value=self.row_len)
        self.C_var = tk.IntVar(value=self.C)
        self.IC_num_var = tk.IntVar(value=self.IC_num)
        #----------------------------------------------------------------------
        self.main_fr = tk.Frame(self.root)
        self.main_fr.place(relx=.5, rely=.5, anchor=tk.CENTER)
        self.preview_fr = tk.Frame(self.main_fr)
        self.preview_fr.grid(row=0, column=0, padx=9)
        self.preview_cv = tk.Canvas(self.preview_fr, width=self.xW,
                                    height=self.xW)
        self.preview_cv.configure(highlightthickness=0, borderwidth=0)
        self.preview_cv.grid()
        self.controls_fr = tk.Frame(self.main_fr)
        self.controls_fr.grid(row=0, column=1, padx=9)
        #----------------------------------------------------------------------
        self.rule_fr = tk.LabelFrame(self.controls_fr, text='Iteration Rule')
        self.C_scl = tk.Scale(self.rule_fr, variable=self.C_var, from_=5, to=2,
                             label='Colors')
        self.C_scl.bind("<ButtonRelease-1>", self.color_change)
        self.new_rule_btn = tk.Button(self.rule_fr, command=self.new_rule,
                                      text='New Rule')
        self.back_btn = tk.Button(self.rule_fr, command=self.p_back_rule,
                                  text='Previous')
        self.forward_btn = tk.Button(self.rule_fr, command=self.p_forward_rule,
                                     text='Forward')
        self.C_scl.grid(row=0, column=0, columnspan=2)
        self.new_rule_btn.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)
        self.back_btn.grid(row=2, column=0, sticky=tk.W+tk.E)
        self.forward_btn.grid(row=2, column=1, sticky=tk.W+tk.E)
        #----------------------------------------------------------------------
        self.IC_fr = tk.LabelFrame(self.controls_fr, text='Initial Condition')
        self.random_IC_rbtn = tk.Radiobutton(self.IC_fr, command=self.new_IC,
                                             text='Random',
                                             variable=self.IC_num_var, value=0,
                                             indicatoron=0)
        self.FiveP_IC_rbtn = tk.Radiobutton(self.IC_fr, command=self.new_IC,
                                            text='Five Cells',
                                            variable=self.IC_num_var, value=1,
                                            indicatoron=0)
        self.OneP_IC_rbtn = tk.Radiobutton(self.IC_fr, command=self.new_IC,
                                           text='One Cell',
                                           variable=self.IC_num_var, value=2,
                                           indicatoron=0)
        self.new_IC_btn = tk.Button(self.IC_fr, command=self.new_IC,
                                    text='New Initial Condition')
        self.random_IC_rbtn.grid(row=0, column=0)
        self.FiveP_IC_rbtn.grid(row=0, column=1)
        self.OneP_IC_rbtn.grid(row=0, column=2)
        self.new_IC_btn.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E)
        #----------------------------------------------------------------------
        self.ani_fr = tk.LabelFrame(self.controls_fr, text='Animation')
        self.row_len_scl = tk.Scale(self.ani_fr, variable=self.row_len_var,
                                   from_=self.screenwidth, to=20,
                                   resolution=20, label='Width')
        self.run_btn = tk.Button(self.ani_fr, command=self.root.destroy,
                                 text='Run')
        self.row_len_scl.grid(row=0, column=0)
        self.run_btn.grid(row=1, column=0, sticky=tk.W+tk.E)
        #----------------------------------------------------------------------
        self.color_fr = tk.LabelFrame(self.controls_fr, text='Colors')
        for i in range(5):
            l = tk.Label(self.color_fr, text='Color %d' %(i+1))
            l.grid(row=i, column=0)
            b = tk.Button(self.color_fr,
                          background=self.rgb2hex(self.colors[i]))
            b.config(command=lambda i=i, b=b: self.set_color(i,b))
            b.grid(row=i, column=1, sticky=tk.W+tk.E)
        #----------------------------------------------------------------------
        self.rule_fr.grid(row=0, column=0, pady=(0,9), sticky=tk.W+tk.E)
        self.IC_fr.grid(row=1, column=0, pady=9, sticky=tk.W+tk.E)
        self.ani_fr.grid(row=2, column=0, pady=9, sticky=tk.W+tk.E)
        self.color_fr.grid(row=3, column=0, pady=(9,0), sticky=tk.W+tk.E)        
        self.rule_fr.columnconfigure(0, weight=1)
        self.rule_fr.columnconfigure(1, weight=1)        
        self.ani_fr.columnconfigure(0, weight=1)
        self.color_fr.columnconfigure(0, weight=1)
        self.color_fr.columnconfigure(1, weight=3)
        self.new_IC()

    #-------------------------------- Animation -------------------------------
    def lock(self):
        self.row_len = self.row_len_var.get()
        self.scale, self.height = self.set_size()
        self.C = self.C_var.get()
        self.row = np.zeros(self.row_len, dtype='uint8')
        self.new_row()

    def set_size(self):
        max_scale = self.screenheight//100 # Fullscreen at least 100 cells high
        for i in range(2, max_scale + 1):
            if self.row_len*i > self.screenwidth:
                scale = i - 1
                height = self.screenheight//(i - 1)
                return scale, height
        return max_scale, self.screenheight//max_scale

    def set_scroll(self):
        if self.speed < 21:
            FPS = 5*self.speed -4
            shift = 1
        else:
            FPS = 100
            shift = self.speed - 20
        return FPS, shift
    
    def update(self, p_vals, shift):
        p_vals[:,:-shift] = p_vals[:,shift:]
        for i in range(shift - 1):
            p_vals[:,-shift + i] = self.colors[self.row]
            self.iterate()
        p_vals[:,-1] = self.colors[self.row]

if not os.path.exists('Saved'):
    os.makedirs('Saved')

if not os.path.exists('Palettes'):
    os.makedirs('Palettes')

alice = Automaton()

while True:
    alice.setup_GUI()
    alice.root.mainloop() 
    if alice.finished.get():
        break
    alice.lock()
    
    pygame.init()
    pygame.display.set_caption("Cellular Automaton Simulator")
    X = alice.row_len*alice.scale
    Y = alice.height*alice.scale
    screen = pygame.display.set_mode((X,Y), FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.event.set_blocked((MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN,
                              KEYDOWN))
    FPS, shift = alice.set_scroll()
    p_surf = pygame.Surface((alice.row_len,alice.height))
    p_vals = pygame.surfarray.pixels3d(p_surf)
    alice.update(p_vals, 1)
    running = True
    scroll = True
    
    while running:
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_RETURN:
                    alice.random_rule()
                elif event.key == K_BACKSPACE:
                    alice.back_rule()
                elif event.key == K_EQUALS:
                    alice.forward_rule()
                elif event.key == K_DOWN:
                    if alice.speed > 1:
                        alice.speed -= 1
                    FPS, shift = alice.set_scroll()
                elif event.key == K_UP:
                    if alice.speed < 25:
                        alice.speed += 1
                    FPS, shift = alice.set_scroll()
                elif event.key == K_LEFTBRACKET:
                    if alice.C > 2:
                        alice.C -= 1
                        alice.random_rule()
                        alice.new_row()
                elif event.key == K_RIGHTBRACKET:
                    if alice.C < 5:
                        alice.C += 1
                        alice.random_rule()
                        alice.new_row()
                elif event.key in (K_BACKSLASH, K_1, K_2, K_3):
                    if event.key == K_BACKSLASH:
                        alice.new_row()
                    elif event.key == K_1:
                        alice.IC_num = 0
                        alice.random_row()
                    elif event.key == K_2:
                        alice.IC_num = 1
                        alice.FiveCell_row()
                    else:
                        alice.IC_num = 2
                        alice.OneCell_row()
                    alice.update(p_vals, 1)
                    pygame.transform.scale(p_surf, (X, Y), screen)
                    pygame.display.flip()
                    clock.tick(FPS)
                elif event.key == K_SPACE:
                    scroll = not scroll
                elif event.key == K_DELETE:
                    p_vals[:,:] = [0,0,0]
                elif event.key in (K_q, K_ESCAPE):
                    running = False
                    break

        if scroll:
            alice.iterate()
            alice.update(p_vals, shift)
        
        pygame.transform.scale(p_surf, (X, Y), screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()