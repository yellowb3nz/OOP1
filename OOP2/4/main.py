import re
from typing import Protocol, Any, List


class PropertyChangedListenerProtocol(Protocol):
    def on_property_changed(self, obj: Any, property_name) -> None:
        pass


class DataChangedProtocol(Protocol):
    def add_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        pass
    def remove_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        pass


class PropertyChangingListenerProtocol(Protocol):
    def on_property_changing(self, obj: Any, property_name, old_value, new_value) -> bool:
        return True


class DataChangingProtocol(Protocol):
    def add_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        pass
    def remove_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        pass


########################################################################################


NAME, EMAIL = 'name', 'email'


class Listener:
    def on_property_changed(self, obj: Any, property_name : str) -> None:
        print(f'-> поле {property_name} поменялось в классе {obj.__class__.__name__} на {getattr(obj, property_name)}')


class NameValidator:
    def on_property_changing(self, obj: Any, property_name, old_value : str, new_value : str) -> bool:
        if property_name == NAME:
            if not (new_value[0] in '0123456789'):
                return True
            print('-> имя не может начинаться с цифры')
        return False


class EmailValidator:
    def on_property_changing(self, obj: Any, property_name, old_value : str, new_value : str) -> bool:
        if property_name == EMAIL:
            if re.match(r'[a-zA-z0-9]*@[a-zA-z]*[.][a-zA-z]*', new_value):
                return True
            print('-> данное значение не может быть эл. почтой')
        return False


########################################################################################


class User:
    def __init__(self, name : str, email : str) -> None:
        self._name = name
        self._email = email
        self.changing_listeners: List[PropertyChangingListenerProtocol] = []
        self.changed_listeners: List[PropertyChangedListenerProtocol] = []

    def add_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        self.changed_listeners.append(listener)

    def remove_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        self.changed_listeners.remove(listener)

    def add_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        self.changing_listeners.append(listener)

    def remove_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        self.changing_listeners.remove(listener)
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value) -> None:
        if self.changing_listeners:
            if not any(listener.on_property_changing(self, NAME, self._name, value) for listener in self.changing_listeners):
                return
        self._name = value
        for listener in self.changed_listeners:
            listener.on_property_changed(self, NAME)
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value) -> None:
        if self.changing_listeners:
            if not any(listener.on_property_changing(self, EMAIL, self._email, value) for listener in self.changing_listeners):
                return
        self._email = value
        for listener in self.changed_listeners:
            listener.on_property_changed(self, EMAIL)


if __name__ == '__main__':
    user = User('danil', 'danil.strokoff@pochta.ru')
    print(f'логин : {user.name}\tпочта : {user.email}')

    user.add_property_changed_listener(Listener())
    user.add_property_changing_listener(NameValidator())
    user.add_property_changing_listener(EmailValidator())

    user.name = 'danya'
    user.name = '228_Danya_Strokov_228'
    user.email = 'persik2kot'
    user.email = 'danya@pochta.ru'

    print(f'логин : {user.name}\tпочта : {user.email}')