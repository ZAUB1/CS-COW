from tkinter import *
from sound import ThreadedSound

class HelpText:
    def __init__(self, win, text, hidden, sound):
        self.str = StringVar();
        self.helptext = Label(win, textvariable = self.str);
        self.helptext.place(x = 395, y = 5);

        self.placement = self.helptext.place_info();

        self.str.set(text);

        if hidden == True:
            self.helptext.place_forget();

        self.sound = sound;

        if (sound == True) and (hidden == False):
            ThreadedSound("./sounds/notification.mp3");

        self.hidden = hidden;

    def show(self):
        if self.hidden == True:
            self.helptext.place(self.placement);

            if self.sound == True:
                ThreadedSound("./sounds/notification.mp3");

    def hide(self):
        if self.hidden == False:
            self.helptext.place_forget();