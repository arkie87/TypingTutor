from tkinter import Tk, Frame, Button, Label, StringVar
from random import choice, randrange
from time import time as tic
from math import sqrt


FPS = 60
DELAY = 1000 // FPS

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


class TypingTutor:
    def __init__(self):
        self.root = Tk()
        self.root.title("Arkie's Typing Tutor")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
        self.main_menu()
        self.root.mainloop()
        
    def main_menu(self):
        self.frame = Frame(self.root)
        self.new_button = Button(self.frame, text="New Game", command=self.new_game)
        self.quit_button = Button(self.frame, text="Quit", command=self.quit_game)
        self.frame.pack()
        self.new_button.pack()
        self.quit_button.pack()
        
    def new_game(self):
        self.frame.destroy()
        g = Game(self)
    
    def quit_game(self):
        self.root.destroy()
        print("Thanks for playing!")


class Game:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self.score_var = StringVar(self.root, "Score: ")
        
        self.frame = Frame(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.score_label = Label(self.frame, textvariable=self.score_var)
        self.window = Frame(self.frame, width=SCREEN_WIDTH-100, height=SCREEN_HEIGHT-100, bg="blue")
        self.root.bind("<KeyPress>", self.keydown)
        self.root.bind("<Escape>", self.quit)
        self.dictionary = Dictionary()
        
        self.frame.pack()
        self.score_label.pack()
        self.window.pack()
        
        self.words = []
        self.text = ""
        self.word = None
        
        self.level = 3
        self.score = 0
        self.score_min = 0
        self.min_delay = 1000
        self.max_delay = 3000
        self.enemies = 100
        self.spawn_loop()
        
    def spawn_loop(self):
        if self.enemies > 0:
            if self.score > 100 + self.score_min:
                self.score_min += 100
                self.level += 1
                
            self.spawn_word()
            self.enemies -= 1
            self.root.after(randrange(self.min_delay,self.max_delay), self.spawn_loop)
    
    def spawn_word(self):
        word = Word(self, self.dictionary.get_random_word(self.level))
        self.words += [word]
        return word
        
    def keydown(self, event):
        text = self.text + event.char
        for word in self.words:
            word.check(text)
            if word.index > 0:
                self.text = text
                self.word = word
                break
            else:
                self.clear_word()
        
        if self.word and self.word.destroyed:
            self.clear_word()
                
        print(self.word)
        
    def clear_word(self):
        self.word = None
        self.text = ""
        
        
    def defeat(self, word):
        self.words.remove(word)
        
        ti = word.times[0]
        tf = word.times[-1]
        
        m = (tf-ti) / (len(word.times) - 1)
        error = [(m*i + ti - t)**2 for i, t in enumerate(word.times)]
        print(error)
        
        self.score += len(word.times) / (tf - ti) + (1 - 2*sqrt(sum(error)))
        
    def missed(self, word):
        self.words.remove(word)
        
        self.score -= 2*len(word.string)
        
    @property
    def score(self):
        return self._score
        
    @score.setter
    def score(self, value):
        self._score = int(value)
        self.score_var.set(f"Score: {self._score}")
        if self._score < 0:
            self.lose()
        
    def lose(self):
        self.quit(None)
        
    def quit(self, event):
        self.frame.destroy()
        self.parent.main_menu()


class Word:
    def __init__(self, game, string):
        self.game = game
        self.root = game.window
        self.string = string + " "
        self.frame = Frame(self.root)
        self.label = Label(self.frame, text="", fg="red", bg="blue")
        self.label2 = Label(self.frame, text=self.string, fg="white", bg="blue")
        
        self.times = []
        self.index = 0
        self.x = randrange(100, 900)
        self.y = 0
        self.destroyed = False
        print(f"{self.string} word spawned")
        
        self.frame.place(relx=self.x, rely=self.y)
        self.label.grid(row=0, column=0)
        self.label2.grid(row=0, column=1)
        self.tick()
        
    def __repr__(self):
        return self.string
        
    def tick(self):
        if self.destroyed:
            self.defeat()
        else:
            self.y += 1
            if self.y > 950:
                self.missed()
            else:
                self.frame.place(relx=self.x/1000, rely=self.y/1000)
                self.label.config(text=self.string[:self.index], fg="red")
                self.label2.config(text=self.string[self.index:])
                self.root.after(DELAY, self.tick)
        
    def check(self, text):
        if self.string.startswith(text):
            self.index = len(text)
            self.times += [tic()]
        else:
            self.index = 0
            self.times = []
            
        if self.index == len(self.string):
            self.destroyed  = True
            
    def show(self):
        print(f"{self.string[:self.index]}")
            
    def defeat(self):
        self.destroy()
        print(f"Defeated {self.string}")
        self.game.defeat(self)
        
    def missed(self):
        self.destroy()
        print(f"Missed {self.string}")
        self.game.missed(self)
        
    def destroy(self):
        self.frame.destroy()




class Dictionary:
    def __init__(self):
        filedir = "/".join(__file__.replace("\\", "/").split("/")[:-1])
    
        with open(f"{filedir}/Words.txt", 'r') as f:
            words = f.read().split("\n")
            
        self.words = {}
        for word in words:
            if len(word) not in self.words:
                self.words[len(word)] = []
                
            self.words[len(word)] += [word]
        
        
    def get_random_word(self, N=3):
        return choice(self.words[N])


if __name__ == "__main__":
    game = TypingTutor()
    
