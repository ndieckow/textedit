import tkinter as tk

from event_handlers import *
from edit_context import EditContext
from utils import rc2px

# memory:
# - for each line, save length
# - save text in a nice data structure (rope)

def save_txt(context: EditContext, path: str):
    with open(path, 'w') as f:
        f.write('\n'.join([line.to_str() for line in context.lines]))
    save_to_label.pack(side='left', fill='both')
    save_to_label.after(3000, lambda: save_to_label.pack_forget())

def load_txt(context: EditContext, path: str):
    # completely obliterate the previous stuff
    context.reset()

    with open(path, 'r') as f:
        for line in f:
            context.appendline(line[:-1]) # cut off the newlines
    
    context.update('text', 'cursor')

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("850x450")

    frm = tk.Frame(root, padx=5, pady=5)
    frm.grid()

    canvas = tk.Canvas(frm, width=800, height=400, bg='white', cursor='xterm')

    cursor_xpos, cursor_ypos = rc2px(0, 0)
    cursor_line = canvas.create_line(cursor_xpos, cursor_ypos, cursor_xpos, cursor_ypos + 15, fill="black", width=1)

    text_object = canvas.create_text(7, 2, text='', fill="black", anchor="nw", font=("Andale Mono",))

    context: EditContext = EditContext(canvas, cursor_line, text_object)

    def attach_context(fn):
        return lambda x: fn(context, x)
    
    for eventstring, handler in HANDLER_DICT.items():
        canvas.bind(eventstring, attach_context(handler))
    
    canvas.pack()
    canvas.focus_set()

    tk.Button(frm, text="Quit", command=root.destroy).pack(side='left', fill='both')
    tk.Button(frm, text="Save", command=lambda: save_txt(context, 'out.txt')).pack(side='left', fill='both')
    tk.Button(frm, text="Load from in.txt", command=lambda: load_txt(context, 'in.txt')).pack(side='left', fill='both')
    save_to_label = tk.Label(frm, text="Saved to out.txt")
    root.mainloop()