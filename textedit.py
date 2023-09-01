import tkinter as tk

# memory:
# - for each line, save length
# - save text in a nice data structure (rope)

class Cursor:
    def __init__(self):
        self.line: int = 0  # Line number
        self.pos: int = 0 # Position on the line
    
    def move_right(self, amt = 1):
        if self.pos + amt <= lines[self.line].length:
            self.pos += amt
        elif self.line < len(lines) - 1: # wrap to next line, NOTE: amt is ignored
            self.line += 1
            self.pos = 0
    
    def move_left(self):
        if self.pos > 0:
            self.pos -= 1
        elif self.line > 0: # wrap to previous line
            self.line -= 1
            self.pos = lines[self.line].length
    
    def move_up(self):
        if self.line > 0:
            self.line -= 1
        self.clip_line_pos()
    
    def move_down(self):
        # TODO: line length checks
        if self.line < len(lines) - 1:
            self.line += 1
        self.clip_line_pos()

    def clip_line_pos(self):
        self.pos = min(self.pos, lines[self.line].length)
    
    def teleport(self, line, pos):
        self.line = min(line, len(lines) - 1)
        self.pos = min(pos, lines[self.line].length)

class Line:
    def __init__(self, content = ''):
        self.content = list(content)
    
    @property
    def length(self):
        return len(self.content)

    @property
    def is_empty(self):
        return self.length == 0

    def insert(self, i, char):
        if len(char) == 1:
            self.content.insert(i, char)
        else:
            self.content[i:i] = char
    
    def remove_at(self, i):
        del self.content[i]
    
    def append(self, o):
        # append another line to self
        self.content += o.content

    def to_str(self):
        return ''.join(self.content)


def move_handler(dir):
    move = getattr(Cursor, 'move_' + dir)
    move(cursor)
    update('cursor')

def right_handler(event): move_handler('right')
def left_handler(event): move_handler('left')
def up_handler(event): move_handler('up')
def down_handler(event): move_handler('down')

cursor = Cursor()
lines = [Line()]

def key_handler(event):
    global cursor
    if len(event.char) == 0:
        return
    lines[cursor.line].insert(cursor.pos, event.char)
    cursor.move_right()
    update('text', 'cursor')

def backspace_handler(event):
    global cursor
    if cursor.pos == 0:
        if cursor.line == 0: # no previous line to merge with
            return

        prev_line_len = lines[cursor.line - 1].length
        if not lines[cursor.line].is_empty:
            lines[cursor.line - 1].append(lines[cursor.line])
        
        del lines[cursor.line]
        cursor.move_up()
        cursor.pos = prev_line_len
    else:
        lines[cursor.line].remove_at(cursor.pos - 1)
        cursor.move_left()
    update('text', 'cursor')

def return_handler(event):
    # insert first, then move down!
    lines.insert(cursor.line + 1, Line())
    lines[cursor.line + 1].content += lines[cursor.line].content[cursor.pos:]
    lines[cursor.line].content = lines[cursor.line].content[:cursor.pos]
    cursor.move_down()
    cursor.pos = 0
    update('text', 'cursor')

def tab_handler(event):
    lines[cursor.line].insert(cursor.pos, '    ') # TODO: add some kind of write function that also moves the cursor
    cursor.move_right(4)
    update('text', 'cursor')
    return 'break'

# TODO: store those 4 numbers in one place
# cursor_xpos = 7 + cursor.pos * 8
# cursor_ypos = 3 + cursor.line * 15 
def left_click_handler(event):
    line = (event.y - 3) // 15  # floor works better for lines
    pos = round((event.x - 7) / 8)  # nearest rounding works better for pos
    cursor.teleport(line, pos)
    update('cursor')

def update(*what):
    if 'text' in what:
        canvas.itemconfigure(text_object, text='\n'.join([line.to_str() for line in lines]))
    if 'cursor' in what:
        cursor_xpos = 7 + cursor.pos * 8
        cursor_ypos = 3 + cursor.line * 15
        canvas.coords(cursor_line, cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15)
    canvas.update()

root = tk.Tk()
root.geometry("850x450")

frm = tk.Frame(root, padx=5, pady=5)
frm.grid()

canvas = tk.Canvas(frm, width=800, height=400, bg="white")
text_object = canvas.create_text(7, 2, text='', fill="black", anchor="nw", font=("Andale Mono",))

cursor_xpos = 7 + cursor.pos * 8
cursor_ypos = 3 + cursor.line * 15
cursor_line = canvas.create_line(cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15, fill="black", width=1)

canvas.bind('<Left>', left_handler)
canvas.bind('<Right>', right_handler)
canvas.bind('<Up>', up_handler)
canvas.bind('<Down>', down_handler)
canvas.bind('<Key>', key_handler)
canvas.bind('<BackSpace>', backspace_handler)
canvas.bind('<Return>', return_handler)
canvas.bind('<Tab>', tab_handler)
canvas.bind('<Button-1>', left_click_handler)
canvas.pack()
canvas.focus_set()

def save_txt(path):
    with open(path, 'w') as f:
        f.write('\n'.join([line.to_str() for line in lines]))
    save_to_label.pack(side='left', fill='both')
    save_to_label.after(3000, lambda: save_to_label.pack_forget())

def load_txt(path):
    global lines, cursor
    # completely obliterate the previous stuff
    lines = []
    cursor = Cursor()

    with open(path, 'r') as f:
        for line in f:
            lines.append(Line(line[:-1])) # cut off the newlines
    
    update('text', 'cursor')

tk.Button(frm, text="Quit", command=root.destroy).pack(side='left', fill='both')
tk.Button(frm, text="Save", command=lambda: save_txt('out.txt')).pack(side='left', fill='both')
tk.Button(frm, text="Load from in.txt", command=lambda: load_txt('in.txt')).pack(side='left', fill='both')
save_to_label = tk.Label(frm, text="Saved to out.txt")
root.mainloop()