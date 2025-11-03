from enum import Enum
from typing import Type, TypeVar, Any, Callable, Dict, Optional
from contextlib import contextmanager


T = TypeVar('T')


class LifeStyle(Enum):
    PER_REQUEST = 1
    SCOPED = 2
    SINGLETON = 3

class Injector:
    def __init__(self):
        self._registrations: Dict[Type, Dict] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._scope_active = False
    
    def register(self, interface_type: Type[T], realization: Type[T], life_style: LifeStyle = LifeStyle.PER_REQUEST, *params : dict):
        if params is None:
            params = {}
            
        self._registrations[interface_type] = {
            'realization': realization,
            'life_style': life_style,
            'params': params
        }
    
    @contextmanager
    def scope(self):
        self._scoped_instances = {}
        self._scope_active = True
        try:
            yield self
        finally:
            self._scoped_instances = {}
            self._scope_active = False
    
    def get_instance(self, interface_type: Type[T]) -> T:
        if interface_type not in self._registrations:
            raise ValueError(f'!!! такого интерфейса для инстанса нет {interface_type.__name__}')
        
        registration = self._registrations[interface_type]
        life_style = registration['life_style']
        realization = registration['realization']
        params = registration['params']
        
        if life_style == LifeStyle.SINGLETON:
            if interface_type in self._singleton_instances:
                return self._singleton_instances[interface_type]
            
            instance = self._create_instance(realization, params)
            self._singleton_instances[interface_type] = instance
            return instance
        
        elif life_style == LifeStyle.SCOPED:
            if not self._scope_active:
                raise RuntimeError('!!!нельзя использовать вне scope')
            
            if interface_type in self._scoped_instances:
                return self._scoped_instances[interface_type]
            
            instance = self._create_instance(realization, params)
            self._scoped_instances[interface_type] = instance
            return instance
        else:
            return self._create_instance(realization, params)
    
    def _create_instance(self, realization: Type[T] | Callable[..., T], params: Dict[str, Any]) -> T:
        if callable(realization) and not isinstance(realization, type):
            return realization()
        
        constructor_params = {}
        constructor = realization.__init__ if hasattr(realization, '__init__') else None
        
        if constructor:
            import inspect
            sig = inspect.signature(constructor)
            
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                if name in params:
                    constructor_params[name] = params[name]
                elif param.annotation != inspect.Parameter.empty:
                    try:
                        constructor_params[name] = self.get_instance(param.annotation)
                    except ValueError:
                        if param.default == inspect.Parameter.empty:
                            raise ValueError(f'!!! нельзя установить {name} для параметра {param.annotation.__name__}')
        return realization(**constructor_params)


############################################################


class Interface1:
    pass

class Interface2:
    pass

class Interface3:
    pass

class Class1Debug(Interface1):
    def __init__(self, service2: Optional[Interface2] = None):
        self.service2 = service2
        print('вызван конструктор Class1Debug')

class Class1Release(Interface1):
    def __init__(self, service3: Interface3):
        self.service3 = service3
        print('вызван конструктор Class1Release')

class Class2Debug(Interface2):
    def __init__(self):
        print('вызван конструктор Class2Debug')

class Class2Release(Interface2):
    def __init__(self, param1: str, param2: int):
        self.param1 = param1
        self.param2 = param2
        print(f'вызван конструктор Class2Release с параметрами: {param1}, {param2}')

class Class3Debug(Interface3):
    def __init__(self):
        print('вызван конструктор Class3Debug')

class Class3Release(Interface3):
    def __init__(self):
        print('вызван конструктор Class3Release')


def class1_factory(injector: Injector) -> Interface1:
    print('вызвана фабрика класса 1')
    return Class1Debug()

def class2_factory(injector: Injector) -> Interface2:
    print('вызвана фабрика класса 2')
    return Class2Debug()

def class3_factory(injector: Injector) -> Interface3:
    print('вызвана фабрика класса 3')
    return Class3Debug()


############################################################


if __name__ == '__main__':
    injector = Injector()
    
    injector.register(Interface1, Class1Debug, LifeStyle.PER_REQUEST)
    injector.register(Interface2, Class2Debug, LifeStyle.SCOPED)
    injector.register(
        interface_type=Interface3,
        realization = lambda: class3_factory(injector),
        life_style=LifeStyle.SINGLETON
    )
    
    print('-> singleton')
    instance1 = injector.get_instance(Interface3)
    instance2 = injector.get_instance(Interface3)
    print(f'одинаковый инстанс:  {instance1 is instance2}\n')
    
    print('-> scope')
    with injector.scope():
        scoped1 = injector.get_instance(Interface2)
        scoped2 = injector.get_instance(Interface2)
        print(f'тот же инстанс в скопе:  {scoped1 == scoped2}')

        with injector.scope():
            scoped3 = injector.get_instance(Interface2)
            print(f'новый инстанс в старом скопе:  {scoped1 == scoped3}\n')
    
    print('-> per request')
    per_req1 = injector.get_instance(Interface1)
    per_req2 = injector.get_instance(Interface1)
    print(f'одинаковый инстанс:  {per_req1 is per_req2}\n')
