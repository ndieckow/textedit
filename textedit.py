import tkinter as tk
import xerox

from enum import Enum
from typing import Optional

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
        self.marker_rect: Optional[int] = None
    
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


# TODO: store those 4 numbers in one place
def rc2px(line: int, pos: int) -> tuple[int, int]:
    x = 7 + pos * 8
    y = 3 + line * 15
    return x, y

def px2rc(x: int, y: int) -> tuple[int, int]:
    line = (y - 3) // 15  # floor works better for lines
    pos = round((x - 7) / 8)  # nearest rounding works better for pos
    return line, pos

def move_handler(dir: str):
    marker_pre()
    move = getattr(Cursor, 'move_' + dir)
    move(cursor)
    marker_post()
    update('cursor', 'marker')

def right_handler(event): move_handler('right')
def left_handler(event): move_handler('left')
def up_handler(event): move_handler('up')
def down_handler(event): move_handler('down')

Key = Enum('Key', ['SHIFT', 'CMD'])

cursor: Cursor = Cursor()
lines: list[Line] = [Line()]
keysym_key_dict: dict[str, Key] = {
    'Shift_L': Key.SHIFT,
    'Meta_L': Key.CMD
}
key_hold_dict: dict[Key, bool] = {key : False for key in Key}
marker_start = (-1, -1)
marker_end = (-1, -1)
marked_lines: set[int] = set() # we need to keep track of the lines that are (partially) marked in order to remove the rectangles

def marker_pre():
    global marker_start, marker_end
    if key_hold_dict[Key.SHIFT]:
        if marker_start == (-1, -1): marker_start = (cursor.line, cursor.pos)
    else:
        marker_start = (-1, -1)
        marker_end = (-1, -1)

def marker_post():
    global marker_start, marker_end
    if key_hold_dict[Key.SHIFT]:
        marker_end = (cursor.line, cursor.pos)

def get_marked_text():
    global marker_start, marker_end
    if -1 in marker_start + marker_end:
        return ''
    if marker_start > marker_end: # swap if they're wrongly ordered
        tmp = marker_start
        marker_start = marker_end
        marker_end = tmp
    if marker_start[0] == marker_end[0]:
        return ''.join(lines[marker_start[0]].content[marker_start[1]:marker_end[1]])
    else:
        # TODO: refactor this ugly-ass line
        return '\n'.join(''.join(lines[l].content[(marker_start[1] if l == marker_start[0] else 0) : (marker_end[1] if l == marker_end[0] else lines[l].length)]) for l in range(marker_start[0], marker_end[0] + 1))

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

# TODO: support other OS's than macOS
def key_press_handler(event):
    if event.keysym in keysym_key_dict:
        key_hold_dict[keysym_key_dict[event.keysym]] = True
    global cursor
    if len(event.char) == 0:
        return
    if key_hold_dict[Key.CMD]:
        if event.char == 'v':
            paste = xerox.paste()
            lines[cursor.line].insert(cursor.pos, paste)
            cursor.move_right(len(paste))
        elif event.char == 'c':
            marked_text = get_marked_text()
            if marked_text != '': xerox.copy(marked_text)
    else:
        lines[cursor.line].insert(cursor.pos, event.char)
        cursor.move_right()
    update('text', 'cursor')

def key_release_handler(event):
    if event.keysym in keysym_key_dict:
        key_hold_dict[keysym_key_dict[event.keysym]] = False

def left_click_handler(event):
    marker_pre()
    line, pos = px2rc(event.x, event.y)
    cursor.teleport(line, pos)
    marker_post()
    update('cursor', 'marker')

def update(*what):
    global marker_start, marker_end
    if 'text' in what:
        canvas.itemconfigure(text_object, text='\n'.join([line.to_str() for line in lines]))
    if 'cursor' in what:
        cursor_xpos, cursor_ypos = rc2px(cursor.line, cursor.pos)
        canvas.coords(cursor_line, cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15)
    if 'marker' in what:
        mstart = marker_start if marker_start < marker_end else marker_end
        mend = marker_end if marker_start < marker_end else marker_start
        
        if -1 not in mstart + mend:
            for l in range(mstart[0], mend[0] + 1):
                marker_start_pos = rc2px(*(mstart if l == mstart[0] else (l, 0)))
                marker_end_pos = rc2px(*(mend if l == mend[0] else (l, lines[l].length + 1)))
                if (rect := lines[l].marker_rect) is not None:
                    canvas.coords(rect, *marker_start_pos, marker_end_pos[0], marker_end_pos[1] + 15)
                else:
                    lines[l].marker_rect = canvas.create_rectangle(*marker_start_pos, marker_end_pos[0], marker_end_pos[1] + 15, fill='lightblue')
                    canvas.tag_lower(lines[l].marker_rect) # type: ignore
                    marked_lines.add(l)
        for l in marked_lines.difference(set(range(mstart[0], mend[0] + 1))): # remove all other markings
            assert lines[l].marker_rect is not None, 'marked_lines is inconsistent'
            canvas.delete(lines[l].marker_rect) # type: ignore
            lines[l].marker_rect = None
            marked_lines.remove(l)
    canvas.update()

root = tk.Tk()
root.geometry("850x450")

frm = tk.Frame(root, padx=5, pady=5)
frm.grid()

canvas = tk.Canvas(frm, width=800, height=400, bg='white', cursor='xterm')

marker_rect = canvas.create_rectangle(-1, -1, -1, -1, fill='lightblue')

cursor_xpos, cursor_ypos = rc2px(cursor.line, cursor.pos)
cursor_line = canvas.create_line(cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15, fill="black", width=1)

text_object = canvas.create_text(7, 2, text='', fill="black", anchor="nw", font=("Andale Mono",))

canvas.bind('<Left>', left_handler)
canvas.bind('<Right>', right_handler)
canvas.bind('<Up>', up_handler)
canvas.bind('<Down>', down_handler)
canvas.bind('<BackSpace>', backspace_handler)
canvas.bind('<Return>', return_handler)
canvas.bind('<Tab>', tab_handler)
canvas.bind('<Button-1>', left_click_handler)
canvas.bind('<KeyPress>', key_press_handler)
canvas.bind('<KeyRelease>', key_release_handler)
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