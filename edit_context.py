from typing import Optional

from key_state import Key, keysym_key_dict, key_hold_dict
from utils import rc2px

class EditContext:
    def __init__(self, canvas, cursor_line, text_object):
        # internal state
        self.cursor: Cursor = Cursor(self)
        self.lines: list[Line] = [Line()]
        self.marker_start = (-1, -1)
        self.marker_end = (-1, -1)
        self.marked_lines: set[int] = set() # we need to keep track of the lines that are (partially) marked in order to remove the rectangles

        # visual stuff (TODO: use something like an EditContextRenderer eventually)
        self.canvas = canvas
        self.cursor_line = cursor_line
        self.text_object = text_object
    
    @property
    def currentline(self):
        return self.lines[self.cursor.line]
    
    @property
    def nextline(self):
        return self.lines[self.cursor.line + 1] # NOTE: no out-of-bounds check
    
    @property
    def prevline(self):
        return self.lines[self.cursor.line - 1] # NOTE: no out-of-bounds check

    def reset(self):
        self.cursor.reset()
        self.lines = []
        self.marker_start = (-1, -1)
        self.marker_end = (-1, -1)
        self.marked_lines = set()

    def update(self, *what):
        if 'text' in what:
            self.canvas.itemconfigure(self.text_object, text='\n'.join([line.to_str() for line in self.lines]))
        if 'cursor' in what:
            cursor_xpos, cursor_ypos = rc2px(self.cursor.line, self.cursor.pos)
            self.canvas.coords(self.cursor_line, cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15)
        if 'marker' in what:
            # TODO: outsource this swap to a function
            mstart = self.marker_start if self.marker_start < self.marker_end else self.marker_end
            mend = self.marker_end if self.marker_start < self.marker_end else self.marker_start
            
            if -1 not in mstart + mend:
                for l in range(mstart[0], mend[0] + 1):
                    marker_start_pos = rc2px(*(mstart if l == mstart[0] else (l, 0)))
                    marker_end_pos = rc2px(*(mend if l == mend[0] else (l, self.lines[l].length + 1)))
                    if (rect := self.lines[l].marker_rect) is not None:
                        self.canvas.coords(rect, *marker_start_pos, marker_end_pos[0], marker_end_pos[1] + 15)
                    else:
                        self.lines[l].marker_rect = self.canvas.create_rectangle(*marker_start_pos, marker_end_pos[0], marker_end_pos[1] + 15, fill='lightblue')
                        self.canvas.tag_lower(self.lines[l].marker_rect) # type: ignore
                        self.marked_lines.add(l)
            for l in self.marked_lines.difference(set(range(mstart[0], mend[0] + 1))): # remove all other markings
                assert self.lines[l].marker_rect is not None, 'marked_lines is inconsistent'
                self.canvas.delete(self.lines[l].marker_rect) # type: ignore
                self.lines[l].marker_rect = None
                self.marked_lines.remove(l)
        self.canvas.update()
    
    def appendline(self, content: str):
        self.lines.append(Line(content))
    
    def insertline(self, i: int, content: str):
        self.lines.insert(i, Line(content))

    def marker_pre(self):
        if key_hold_dict[Key.SHIFT] or key_hold_dict[Key.MOUSE_LEFT]:
            if self.marker_start == (-1, -1): self.marker_start = (self.cursor.line, self.cursor.pos)
        else:
            self.marker_start = (-1, -1)
            self.marker_end = (-1, -1)

    def marker_post(self):
        if key_hold_dict[Key.SHIFT] or key_hold_dict[Key.MOUSE_LEFT]:
            self.marker_end = (self.cursor.line, self.cursor.pos)

    def get_marked_text(self) -> str:
        if -1 in self.marker_start + self.marker_end:
            return ''
        mstart = self.marker_start if self.marker_start < self.marker_end else self.marker_end
        mend = self.marker_end if self.marker_start < self.marker_end else self.marker_start
        #mstart, mend = swap_if_bigger(self.marker_start, self.marker_end)
        if mstart[0] == mend[0]:
            return ''.join(self.lines[mstart[0]].content[mstart[1]:mend[1]])
        else:
            # TODO: refactor this ugly-ass line
            return '\n'.join(''.join(self.lines[l].content[(mstart[1] if l == mstart[0] else 0) : (mend[1] if l == mend[0] else self.lines[l].length)]) for l in range(mstart[0], mend[0] + 1))

class Cursor:
    def __init__(self, context):
        self.context: EditContext = context
        self.line: int = 0  # Line number
        self.pos: int = 0 # Position on the line
        self.goal_pos: int = 0 # desired position, whenever possible
    
    @property
    def _ll(self) -> int:
        # helper function to determine line length of current line
        return self.context.lines[self.line].length

    def reset(self):
        self.line = self.pos = self.goal_pos = 0

    def move_right(self, amt = 1):
        if self.pos + amt <= self._ll:
            self.pos += amt
        elif self.line < len(self.context.lines) - 1: # wrap to next line, NOTE: amt is ignored
            self.line += 1
            self.pos = 0
        self.goal_pos = self.pos
    
    def move_left(self):
        if self.pos > 0:
            self.pos -= 1
        elif self.line > 0: # wrap to previous line
            self.line -= 1
            self.pos = self._ll
        self.goal_pos = self.pos
    
    def move_up(self):
        if self.line > 0:
            self.line -= 1
            self.pos = self.goal_pos # see if we can get back to goal pos
        else:
            self.pos = self.goal_pos = 0
        self.clip_line_pos()
    
    def move_down(self):
        if self.line < len(self.context.lines) - 1:
            self.line += 1
            self.pos = self.goal_pos
        else:
            self.pos = self.goal_pos = self._ll
        self.clip_line_pos()

    def clip_line_pos(self):
        self.pos = min(self.pos, self._ll)
    
    def teleport(self, line, pos):
        self.line = min(line, len(self.context.lines) - 1)
        self.pos = self._ll if pos == -1 else min(pos, self._ll)
        self.goal_pos = self.pos

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