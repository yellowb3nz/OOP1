import json
from typing import Protocol, Dict


class Command(Protocol):
    def execute(self) -> str:
        ...

    def undo(self) -> str|None:
        ...

    def redo(self) -> str|None:
        ...


############################################################


class KeyCommand():
    def __init__(self, controller, sym) -> None:
        self.controller = controller
        self.sym = sym

    def execute(self) -> str:
        self.controller.print_sym(self.sym)
        return self.controller.curr_text

    def undo(self) -> str:
        self.controller.del_sym()
        return self.controller.curr_text

    def redo(self) -> str:
        return self.execute()


class VolumeUpCommand():
    def __init__(self, controller, step : int = 10) -> None:
        self.controller = controller
        self.step = step

    def execute(self) -> str:
        self.controller.vol_increase(self.step)
        return f'volume +{self.step}'

    def undo(self) -> str:
        self.controller.vol_decrease(self.step)
        return f'volume -{self.step}'

    def redo(self) -> str:
        return self.execute()


class VolumeDownCommand():
    def __init__(self, controller, step : int = 10) -> None:
        self.controller = controller
        self.step = step

    def execute(self) -> str:
        self.controller.vol_decrease(self.step)
        return f'volume -{self.step}'

    def undo(self) -> str:
        self.controller.vol_increase(self.step)
        return f'volume +{self.step}'

    def redo(self) -> str:
        return self.execute()


class MediaPlayerCommand():
    def __init__(self, controller, play : bool = False) -> None:
        self.controller = controller
        self.play = play

    def execute(self) -> str:
        self.play = not self.play
        if self.play:
            self.controller.media_on()
            return 'media play'
        else:
            self.controller.media_off()
            return 'media pause'

    def undo(self) -> str:
        return self.execute()

    def redo(self) -> str:
        return self.execute()


############################################################


class KeyBoard:
    def __init__(self, volume : int = 50, media : bool = False, binds : Dict[str, Command] = dict()) -> None:
        self._key_binds : Dict[str, Command] = binds
        self.curr_text = str()
        self.journal = list()
        self.out = list()
        self.move = -1
        self.volume = volume
        self.media_player_switch = media
    
    @property
    def key_binds(self) -> Dict[str, Command]:
        return self._key_binds

    @key_binds.setter
    def key_binds(self, binds : Dict[str, Command]) -> None:
        self._key_binds = binds

    def new_key_bind(self, button : str, command : Command) -> None:
        self._key_binds[button] = command
    
    def keyboard_execute(self, button) -> None:
        if button in self._key_binds.keys():
            command = self._key_binds[button]
            self.out.append(command.execute())
            if self.move != -1:
                self.journal = self.journal[:self.move]
                self.move = -1
            self.journal.append(command)

    
    def keyboard_undo(self) -> None:
        if abs(self.move) <= len(self.journal):
            command = self.journal[self.move]
            self.move -= 1
            self.out.append(command.undo())
            return
        print('undo не undo')
    
    def keyboard_redo(self) -> None:
        if self.move < -1:
            self.move += 1
            command = self.journal[self.move]
            self.out.append(command.redo())
            return
        print('redo не redo')
    
    def print_sym(self, sym) -> None:
        self.curr_text += sym

    def del_sym(self) -> None:
        if self.curr_text:
            self.curr_text = self.curr_text[:-1]
    
    def vol_increase(self, step) -> None:
        if (self.volume + step) <= 100:
            self.volume += step
        else:
            self.volume = 100
    
    def vol_decrease(self, step) -> None:
        if (self.volume - step) >= 0:
            self.volume -= step
        else:
            self.volume = 0
    
    def media_on(self) -> None:
        self.media_player_switch = True

    def media_off(self) -> None:
        self.media_player_switch = False


class KeyboardStateSaver:
    def __init__(self, filename):
        self.filename = filename
    
    def save(self, binds) -> None:
        for button, command in binds.items():
            if 'KeyCommand' in str(command.__class__):
                binds[button] = command.sym
            elif 'VolumeUpCommand' in str(command.__class__):
                binds[button] = f'volume +{command.step}'
            elif 'VolumeDownCommand' in str(command.__class__):
                binds[button] = f'volume -{command.step}'
            elif 'MediaPlayerCommand' in str(command.__class__):
                binds[button] = 'media player'
        try:
            with open(self.filename, 'w') as jason:
                json.dump(binds, jason, indent=4)
        except:
            print('!!!что-то пошло не так при записи в файл')
    
    def load(self, controller) -> dict:
        try:
            with open(self.filename, 'r') as jason:
                binds = json.load(jason)
        except:
            print('!!!что-то пошло не так при чтении файла')
            return dict()
        
        for button, command in binds.items():
            if len(command) == 1:
                binds[button] = KeyCommand(controller, command)
            elif 'volume +' in command:
                binds[button] = VolumeUpCommand(controller, int(command[8:]))
            elif 'volume -' in command:
                binds[button] = VolumeDownCommand(controller, int(command[8:]))
            elif 'media player' in command:
                binds[button] = MediaPlayerCommand(controller)
        return binds
    
def save_to(filename, binds) -> None:
    KeyboardStateSaver(filename).save(binds)

def load_from(filename, controller) -> dict:
    return KeyboardStateSaver(filename).load(controller)


############################################################


if __name__ == '__main__':
    A, B, C, SPACE, UP, DOWN, UNDO, REDO = 'a', 'b', 'c', 'space', 'up', 'down', 'undo', 'redo'

    macrosses = dict()
    macrosses[A] = KeyCommand(KeyBoard(), 'a')
    macrosses[B] = KeyCommand(KeyBoard(), 'b')
    macrosses[C] = KeyCommand(KeyBoard(), 'c')
    macrosses[UP] = VolumeUpCommand(KeyBoard(), 10)
    macrosses[DOWN] = VolumeDownCommand(KeyBoard(), 10)
    macrosses[SPACE] = MediaPlayerCommand(KeyBoard())

    save_to('C:\\Users\\Danya\\Desktop\\OOP2\\6\\keyboard_binds.json', macrosses)

    new_keyboard = KeyBoard()
    new_keyboard.key_binds = load_from('C:\\Users\\Danya\\Desktop\\OOP2\\6\\keyboard_binds.json', new_keyboard)
    for key in [C, A, UP, UNDO, UNDO, REDO,  UP, DOWN, SPACE, SPACE, SPACE]:
        if key == 'undo':
            new_keyboard.keyboard_undo()
        elif key == 'redo':
            new_keyboard.keyboard_redo()
        else:
            new_keyboard.keyboard_execute(key)

    with open('C:\\Users\\Danya\\Desktop\\OOP2\\6\\journal.txt', 'w') as file:
        for line in new_keyboard.out:
            print(line)
            file.write(line + '\n')
