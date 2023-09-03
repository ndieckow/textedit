import xerox

from typing import Callable

from edit_context import EditContext, Cursor
from key_state import Key, keysym_key_dict, key_hold_dict
from utils import px2rc

def move_handler(ctx: EditContext, dir: str):
    ctx.marker_pre()
    move = getattr(Cursor, 'move_' + dir)
    move(ctx.cursor)
    ctx.marker_post()
    ctx.update('cursor', 'marker')

def right_handler(ctx, event): move_handler(ctx, 'right')
def left_handler(ctx, event): move_handler(ctx, 'left')
def up_handler(ctx, event): move_handler(ctx, 'up')
def down_handler(ctx, event): move_handler(ctx, 'down')

def backspace_handler(ctx: EditContext, event): # TODO: can I give each handler function more arguments, like a context?
    if ctx.cursor.pos == 0:
        if ctx.cursor.line == 0: # no previous line to merge with
            return

        prev_line_len = ctx.prevline.length
        if not ctx.currentline.is_empty:
            ctx.prevline.append(ctx.currentline)
        
        del ctx.lines[ctx.cursor.line]
        ctx.cursor.move_up()
        ctx.cursor.pos = prev_line_len
    else:
        ctx.currentline.remove_at(ctx.cursor.pos - 1)
        ctx.cursor.move_left()
    ctx.update('text', 'cursor')

def return_handler(ctx: EditContext, event):
    # insert first, then move down!
    ctx.insertline(ctx.cursor.line + 1, '')
    ctx.nextline.content += ctx.currentline.content[ctx.cursor.pos:]
    ctx.currentline.content = ctx.currentline.content[:ctx.cursor.pos]
    ctx.cursor.move_down()
    ctx.cursor.pos = 0
    ctx.update('text', 'cursor')

def tab_handler(ctx: EditContext, event):
    ctx.currentline.insert(ctx.cursor.pos, '    ') # TODO: add some kind of write function that also moves the cursor
    ctx.cursor.move_right(4)
    ctx.update('text', 'cursor')
    return 'break'

# TODO: support other OS's than macOS
def key_press_handler(ctx: EditContext, event):
    if event.keysym in keysym_key_dict:
        key_hold_dict[keysym_key_dict[event.keysym]] = True
    if len(event.char) == 0:
        return
    if key_hold_dict[Key.CMD]:
        if event.char == 'v':
            paste = xerox.paste()
            paste_lines = paste.split('\n')
            remainder = ctx.currentline.content[ctx.cursor.pos:]
            ctx.currentline.content = ctx.currentline.content[:ctx.cursor.pos]
            ctx.currentline.insert(ctx.cursor.pos, paste_lines[0])
            for i in range(1, len(paste_lines)):
                ctx.insertline(ctx.cursor.line + i, paste_lines[i])
            ctx.lines[ctx.cursor.line + len(paste_lines) - 1].content += remainder
            #cursor.move_right(len(paste))
            ctx.cursor.teleport(ctx.cursor.line + len(paste_lines) - 1, len(paste_lines[-1]))
        elif event.char == 'c':
            marked_text = ctx.get_marked_text()
            if marked_text != '': xerox.copy(marked_text)
    else:
        ctx.currentline.insert(ctx.cursor.pos, event.char)
        ctx.cursor.move_right()
    ctx.update('text', 'cursor')

def key_release_handler(ctx: EditContext, event):
    if event.keysym in keysym_key_dict:
        key_hold_dict[keysym_key_dict[event.keysym]] = False

def left_click_press_handler(ctx: EditContext, event):
    ctx.marker_pre()
    line, pos = px2rc(event.x, event.y)
    ctx.cursor.teleport(line, pos)
    ctx.marker_post()
    ctx.update('cursor', 'marker')

    key_hold_dict[Key.MOUSE_LEFT] = True

def left_click_release_handler(ctx: EditContext, event):
    key_hold_dict[Key.MOUSE_LEFT] = False

def mouse_move_handler(ctx: EditContext, event):
    if key_hold_dict[Key.MOUSE_LEFT]:
        ctx.marker_pre()
        ctx.cursor.teleport(*px2rc(event.x, event.y))
        ctx.marker_post()
        ctx.update('cursor', 'marker')


HANDLER_DICT: dict[str, Callable] = {
    '<Left>':               left_handler,
    '<Right>':              right_handler,
    '<Up>':                 up_handler,
    '<Down>':               down_handler,
    '<BackSpace>':          backspace_handler,
    '<Return>':             return_handler,
    '<Tab>':                tab_handler,
    '<ButtonPress-1>':      left_click_press_handler,
    '<ButtonRelease-1>':    left_click_release_handler,
    '<Motion>':             mouse_move_handler,
    '<KeyPress>':           key_press_handler,
    '<KeyRelease>':         key_release_handler
}