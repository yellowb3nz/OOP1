import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Protocol, Sequence, TypeVar, Generic, List, Any


T = TypeVar('T')
ID = 'id'
LOGIN = 'login'
USER_ID = 'user_id'


@dataclass(order=True)
class User:
    id : int
    name : str
    login : str
    password: str = field(repr=False)
    email: Optional[str] = None
    address: Optional[str] = None


def convert(obj: Any):
    if not hasattr(obj, '__dataclass_fields__'):
        raise ValueError('!!!объект не является датаклассом')
    return asdict(obj)


############################################################


class AuthServiceProtocol(Protocol):
    def sign_in(self, user: User) -> None:
        pass

    def sign_out(self, user: User) -> None:
        pass
    
    def is_authorized(self) -> bool:
        return True
    
    def current_user(self)  -> User:
        ...


class DataRepositoryProtocol(Protocol[T]):
    def get_all(self) -> Sequence[T]:
        return ()
    
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    def add(self, item: T) -> None:
        pass
    
    def update(self, item: T) -> None:
        pass
    
    def delete(self, item: T) -> None:
        pass


class UserRepositoryProtocol(DataRepositoryProtocol[User], Protocol):
    def get_by_login(self, login: str) -> User | None:
        pass


############################################################


class DataRepository(Generic[T]):
    def __init__(self, filename : str) -> None:
        self.filename = filename
        self.data : List[T] = []
    
    def load(self) -> bool:
        try:
            with open(self.filename, 'r') as jason:
                self.data = [item for item in json.load(jason)]
        except:
            print('!!!что-то пошло не так при чтении из файла')
            return False
        return True
    
    def save(self) -> bool:
        try:
            with open(self.filename, 'w') as jason: # мб поиенять на 'w'
                json.dump([convert(item) for item in self.data], jason, indent=4)
        except:
            print('!!!что-то пошло не так при записи в файл')
            return False
        return True

    def get_all(self) -> Sequence[T]:
        return self.data
    
    def get_by_id(self, id: int) -> Optional[T]:
        for item in self.data:
            if getattr(item, ID, None) == id:
                return item
    
    def add(self, item: T) -> None:
        self.data.append(item)
        self.save()
    
    def update(self, item: T) -> None:
        for index, old_item in enumerate(self.data):
            if getattr(old_item, ID) == getattr(item, ID):
                self.data[index] = item
                self.save()
                return
        raise ValueError('!!!такого элемента не существует')
    
    def delete(self, item: T) -> None:
        self.data = [
            it for it in self.data
            if getattr(it, ID, None) != getattr(item, ID, None)
            ]
        self.save()


class UserRepository(DataRepository[User]):
    def __init__(self, filename: str):
        super().__init__(filename)

    def get_by_login(self, login: str) -> Optional[User]:
        for item in self.data:
            if getattr(item, LOGIN) == login:
                return item


class AuthService:
    def __init__(self, user_repo: UserRepository, auth_file: str):
        self.user_repo = user_repo
        self.auth_file = auth_file
        self.auth_user: Optional[User] = None
        self.load_auth()

    def load_auth(self) -> None:
        try:
            with open(self.auth_file, 'r') as save_jason:
                try:
                    data = json.load(save_jason)
                except:
                    data = {USER_ID : None}
                user_id = data.get(USER_ID)
                if user_id is not None:
                    self.auth_user = self.user_repo.get_by_id(user_id)
        except FileNotFoundError:
            self.auth_user = None

    def save_auth(self) -> None:
        curr_auth = dict()
        if self.auth_user:
            curr_auth[USER_ID] = self.auth_user.id 
        else:
            curr_auth[USER_ID] = None
        with open(self.auth_file, 'w') as f:
            json.dump(curr_auth, f)

    def sign_in(self, user: User) -> None:
        self.auth_user = user
        self.save_auth()

    def sign_out(self) -> None:
        self.auth_user = None
        self.save_auth()

    @property
    def is_authorized(self) -> bool:
        return bool(self.auth_user)

    @property
    def current_user(self) -> User:
        if not self.auth_user:
            raise ValueError('!!!пользователь не авторизован')
        return self.auth_user


############################################################


if __name__ == '__main__':
    user_repos = UserRepository('C:\\Users\\Danya\\Desktop\\OOP2\\5\\database.json')
    auth_service = AuthService(user_repos, 'C:\\Users\\Danya\\Desktop\\OOP2\\5\\authorized.json')
    
    user1 = User(
        id = 1,
        name = "danya",
        login = "danya",
        password = 'qwerty',
        email = "danya@pochta.ru"
        )
    user_repos.add(user1)
    input('enter для продолжения...')

    auth_service.sign_in(user1)
    print(f'[сейчас авторизован: {auth_service.current_user.name}]')
    input('enter для продолжения...')
    
    user2 = User(
        id = 2,
        name = "oleg",
        login = "oleg",
        password = '12345',
        address = "pravdinsk"
        )
    user_repos.add(user2)
    input('enter для продолжения...')

    auth_service.sign_in(user2)
    print(f'[сейчас авторизован: {auth_service.current_user.name}]')
    input('enter для продолжения...')
    
    new_auth_service = AuthService(user_repos, 'C:\\Users\\Danya\\Desktop\\OOP2\\5\\authorized.json')
    if new_auth_service.is_authorized:
        print(f'[авторизован в новой сессии: {new_auth_service.current_user.name}]')
    else:
        print('[никто не авторизован]')
    input('enter для продолжения...')
    
    auth_service.sign_out()
    if auth_service.is_authorized:
        print(f'[авторизован в сессии: {auth_service.current_user.name}]')
    else:
        print('[никто не авторизован]')
