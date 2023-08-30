import tkinter as tk

# memory:
# - for each line, save length
# - save text in a nice data structure (rope)

class Cursor:
    def __init__(self):
        self.line: int = 0  # Line number
        self.pos: int = 0  # Position on the line
    
    def move_right(self):
        # TODO: only move if self.pos is smaller than line length
        self.pos += 1
    
    def move_left(self):
        if self.pos > 0: self.pos -= 1
    
    def move_up(self):
        # TODO: line length checks
        if self.line > 0:
            self.line -= 1
    
    def move_down(self):
        # TODO: line length checks
        self.line += 1
    
    def teleport(self, line, pos):
        pass

def move_handler(dir):
    move = getattr(Cursor, 'move_' + dir)
    move(cursor)
    cursor_xpos = 7 + cursor.pos * 8
    cursor_ypos = 3 + cursor.line * 15
    canvas.coords(cursor_line, cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15)
    canvas.update()

def right_handler(event): move_handler('right')
def left_handler(event): move_handler('left')
def up_handler(event): move_handler('up')
def down_handler(event): move_handler('down')

cursor = Cursor()
content = []

def key_handler(event):
    global content, cursor
    if len(event.char) == 0:
        return
    content.insert(cursor.pos, event.char)
    move_handler('right')
    update_text()

def backspace_handler(event):
    global content, cursor
    #content.remove(cursor.pos - 1)
    del content[cursor.pos - 1]
    move_handler('left')
    update_text()

root = tk.Tk()
root.geometry("850x450")

frm = tk.Frame(root, padx=5, pady=5)
frm.grid()

canvas = tk.Canvas(frm, width=800, height=400, bg="white")
text_object = canvas.create_text(7, 2, text='', fill="black", anchor="nw", font=("Andale Mono",))

def update_text():
    canvas.itemconfigure(text_object, text=''.join(content))
    canvas.update()

cursor_xpos = 7 + cursor.pos * 8
cursor_ypos = 3 + cursor.line * 15
cursor_line = canvas.create_line(cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15, fill="black", width=1)

canvas.bind('<Left>', left_handler)
canvas.bind('<Right>', right_handler)
canvas.bind('<Up>', up_handler)
canvas.bind('<Down>', down_handler)
canvas.bind('<Key>', key_handler)
canvas.bind('<BackSpace>', backspace_handler)
canvas.pack()
canvas.focus_set()

tk.Button(frm, text="Quit", command=root.destroy).pack()
root.mainloop()