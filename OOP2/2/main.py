from enum import Enum
from typing import Tuple, Optional
from json import load


class Color(Enum):
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34


class Font:
    def __init__(self, sym : str, file : str):
        # выгружает соответствия {символ : псевдошрифт символа} из json файла
        self.font_syms = dict()
        if len(sym) == 1:
            self.sym = sym
        else:
            self.sym = sym[0]
        try:
            with open(file) as jason:
                self.font_syms = load(jason)
            # меняет из каких символов будет псевдошрифт
            for key in self.font_syms.keys():
                self.font_syms[key] = list(map(lambda x: x.replace('#', sym), self.font_syms[key]))
        except:
            raise FileNotFoundError("Файл шрифта не найден, либо нечитаем")
        # размер выгружаемого шрифта
        self.size = len(self.font_syms['A'])
    
    def get_sym(self, sym : str):
        return self.font_syms[sym.upper()]
    
    def font_size(self):
        return self.size


class Printer:
    def __init__(self, font : Font, position: Tuple[int, int], color : Color):
        self.font = font
        self.position = position
        self.color = color
        self.reset_console()
    
    # вход и выход для использования с with для создания фиксированного экземпляра
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[object]):
        self.reset_console()
    
    # очистка консоли
    # \033[0m - ANSCII последовательность очищающая консоль
    @staticmethod
    def reset_console():
        print("\033[0m", end='')

    # статический вывод
    @classmethod
    def print_static(cls, text: str, font: Font, position: Tuple[int, int], color: Color) -> None:
        with cls(font, position, color) as printer_instance:
            printer_instance.print(text)
    
    
    def print(self, text : str):
        print()
        x, y = self.position[0], self.position[1] + 1
        for row in range(self.font.font_size()):
            line = str()
            for sym in text:
                # добавление пробела между словами
                if sym == ' ':
                    sym_rows = ['   '] * self.font.font_size()
                else:
                    sym_rows = self.font.get_sym(sym)
                line += sym_rows[row] + ' '
            if line: 
                print(f"\033[{y + row};{x}H\033[{self.color.value}m{line}\033[0m")


if __name__ == '__main__':
    font = Font('█', 'C:\\Users\\Danya\\Desktop\\OOP2\\2\\letters.json')
    font1 = Font('?', 'C:\\Users\\Danya\\Desktop\\OOP2\\2\\letters1.json')
    font2 = Font('%', 'C:\\Users\\Danya\\Desktop\\OOP2\\2\\letters1.json')

    Printer.print_static("AAABCBCBCA", font1, (0, 0), Color.GREEN)

    Printer.print_static("HELLO WORLD", font, (0, 6), Color.RED)

    with Printer(font, (0, 42), Color.BLUE) as pisalka:
        pisalka.print("ABABA ABABA ABA")
        pisalka.print("LALALA LALA LA")
        pisalka.print("DA DADADA DADADADA")
    
    Printer.print_static("AAAAAAAA", font2, (0, 52), Color.YELLOW)
    
    input()
