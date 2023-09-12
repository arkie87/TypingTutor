from tkinter import Tk, Frame, Button, Label, StringVar
from random import choice, randrange
from time import time as tic


FPS = 60
DELAY = 1000 // FPS

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

BACKGROUND_COLOR = "blue"
FONT = ("Comic Sans", 16)

class TypingTutor:
    def __init__(self):
        self.root = Tk()
        self.root.title("Arkie's Typing Tutor")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
        self.main_menu()
        self.root.mainloop()
        
    def main_menu(self, score=0):
        self.frame = Frame(self.root)
        self.label = Label(self.frame, text=f"High Score: {score}")
        self.new_button = Button(self.frame, text="New Game", command=self.new_game)
        self.quit_button = Button(self.frame, text="Quit", command=self.quit_game)
        self.frame.pack()
        self.label.pack()
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
        
        self.root.bind("<KeyPress>", self.keypress)
        self.root.bind("<Escape>", self.quit)
        
        self.frame = Frame(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.window = Frame(self.frame, width=SCREEN_WIDTH-100, height=SCREEN_HEIGHT-100, bg="blue")
        self.score_var = StringVar(self.root)
        self.enemies_var = StringVar(self.root)
        self.score_label = Label(self.frame, textvariable=self.score_var)
        self.enemies_label = Label(self.frame, textvariable=self.enemies_var)
        self.quit_label = Label(self.frame, text="Press Esc to Quit")
        
        self.frame.pack()
        self.score_label.grid(row=0, column=0)
        self.enemies_label.grid(row=0, column=1)
        self.quit_label.grid(row=0, column=2)
        self.window.grid(row=1, column=0, columnspan=3)
        
        
        self.dictionary = Dictionary()
        self.words = []
        self.text = ""
        self.word = None
        
        self.enemies = 50
        self.max_score = 0
        self.level = 3
        self.score = 0
        self.score_min = 0
        self.delay = 1000
        self.min_delay = 1000
        self.max_delay = 3000
        
        self.spawn_loop()
        
    def set_level(self):
        if self.score > 100 + self.score_min:
            self.score_min += 100
            self.level += 1
            if self.level > 9:
                self.level = 9
        
    def spawn_loop(self):
        if self.enemies > 0:
            self.set_level()
            self.spawn_word()
            self.delay = randrange(self.min_delay,self.max_delay)
            self.root.after(self.delay, self.spawn_loop)
    
    def spawn_word(self):
        self.enemies -= 1
        word = Word(self)
        self.words += [word]
        return word
        
    def keypress(self, event):
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

    def clear_word(self):
        self.text = ""
        self.word = None
        
    def defeat(self, word):
        self.words.remove(word)
        self.score += word.score
        self.check_win()
        
    def missed(self, word):
        self.words.remove(word)
        self.score += word.score
        self.check_win()
        
    def check_win(self):
        if self.enemies == 0 and len(self.words)==0:
            self.win()

    @property
    def score(self):
        return self._score
        
    @score.setter
    def score(self, value):
        self._score = int(value)
        self.max_score = max(self.max_score, self.score)
        self.score_var.set(f"Score: {self._score} ({self.max_score})")
        if self._score < 0:
            self.lose()
            
    @property
    def enemies(self):
        return self._enemies
        
    @enemies.setter
    def enemies(self, value):
        self._enemies = value
        self.enemies_var.set(f"{self.enemies} enemies remaining...")
        
    def win(self):
        print("You Won!")
        self.exit()
        
    def lose(self):
        print("You Lost!")
        self.exit()
        
    def quit(self, event):
        self.exit()
        
    def exit(self):
        self.frame.destroy()
        self.parent.main_menu(self.max_score)


class Dictionary:
    def __init__(self):
        self.filedir = "/".join(__file__.replace("\\", "/").split("/")[:-1])
    
        with open(f"{self.filedir}/Words.txt", 'r') as f:
            words = f.read().split("\n")
            
        self.words = {}
        for word in words:
            if len(word) not in self.words:
                self.words[len(word)] = []
                
            self.words[len(word)] += [word]
    
    def save(self):
        text = []
        for n in range(3,10):
            text += [*self.words[n]]
        text = "\n".join(text)
        
        with open(f"{self.filedir}/Words.txt", "w") as f:
            f.write(text)

    def get_random_word(self, word_length):
        word = choice(self.words[word_length])
        self.words[word_length].remove(word)
        return word


class Word:
    def __init__(self, game):
        self.spawn = tic()
        self.game = game
        self.root = game.window
        self.string = game.dictionary.get_random_word(game.level) + " "
        
        self.speed = game.delay / 1000
        
        self.frame = Frame(self.root)
        self.label = Label(self.frame, text="", fg="red", bg=BACKGROUND_COLOR, font=FONT)
        self.label2 = Label(self.frame, text=self.string, fg="white", bg=BACKGROUND_COLOR, font=FONT)
        
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
            self.y += self.speed * len(self.string) / 6
            if self.y > 900:
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
            
    def get_score(self):
        if self.destroyed:
            t0 = self.spawn
            ti = self.times[0]
            tf = self.times[-1]

            creation_time_multiplier = 1 + 1 /(ti-t0)
            typing_speed_multiplier = 1 + 0.3 /(tf-ti)
                
            self.score = round(len(self.string) * self.speed * creation_time_multiplier * typing_speed_multiplier)
        else:
            self.score = - round(10 * len(self.string) / self.speed)

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
        self.get_score()
        self.display_score()
        self.frame.destroy()
        
    def display_score(self):
        score = f"+{self.score}" if self.score > 0 else f"{self.score}"
        color = "lime" if self.score > 0 else "red"
        label = Label(self.root, text=score, fg=color, bg=BACKGROUND_COLOR, font=FONT)
        label.place(relx=self.x/1000, rely=self.y/1000)
        self.root.after(200, lambda: label.destroy())


if __name__ == "__main__":
    game = TypingTutor()
    
