from enum import Enum

Key = Enum('Key', ['SHIFT', 'CMD', 'MOUSE_LEFT'])

keysym_key_dict: dict[str, Key] = {
    'Shift_L': Key.SHIFT,
    'Meta_L': Key.CMD
}
key_hold_dict: dict[Key, bool] = {key : False for key in Key}