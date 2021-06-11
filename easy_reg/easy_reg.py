import winreg
from typing import Union, Iterable


class RegObj:
    def __init__(self, registry_path, mode, access):
        """
        Открывает или создает раздел

        :param registry_path: раздел
        :param mode:
            если 'open' - открывает раздел;
            если 'create' - создает, а если уже есть, открывает раздел
        :param access: доступ к разделу
        """
        hkeys = {
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKCU': winreg.HKEY_CURRENT_USER,
            'HKEY_USERS': winreg.HKEY_USERS,
            'HKU': winreg.HKEY_USERS,
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKLM': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
            'HKCR': winreg.HKEY_CLASSES_ROOT,
            'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
            'HKCC': winreg.HKEY_CURRENT_CONFIG,
            'HKEY_PERFORMANCE_DATA': winreg.HKEY_PERFORMANCE_DATA,
            'HKEY_DYN_DATA': winreg.HKEY_DYN_DATA,
        }
        self._path = registry_path.split('\\')
        hkey = self._path[0]

        if hkey not in hkeys:
            raise ValueError(f'Error in the name of the registry branch: {hkey}')

        self.hkey = winreg.ConnectRegistry(None, hkeys[hkey])

        self._access = access
        if mode == 'open':
            self._open_key()
        elif mode == 'create':
            self.handle = winreg.CreateKeyEx(self.hkey, self.key, 0, self._access)
        else:
            raise ValueError(f'parameter mode got "{mode}", expected "open" or "create"')

        self._types = ['none', 'sz', 'expand_sz', 'binary', 'dword', 'dword_big_endian', 'link', 'multi_sz',
                       'resource_list', 'full_resource_descriptor', 'resource_requirements_list', 'qword']

    @property
    def full_path(self) -> str:
        """
        Вернет строку с открытым разделом

        :return: str
        """
        return '\\'.join(self._path)

    @property
    def now(self) -> str:
        """
        Вернет имя открытого раздела

        :return: str
        """
        return self._path[-1]

    @property
    def key(self) -> str:
        return '\\'.join(self._path[1:])

    def _open_key(self) -> None:
        self.handle = winreg.OpenKey(self.hkey, self.key, 0, self._access)

    def open_sub_key(self, name: str) -> None:
        """
        Открыть подраздел открытого раздела

        :param name: имя подраздела
        :return: None
        """
        self._path.append(name)
        self._open_key()

    def backward(self) -> None:
        """
        Перейти на родительский раздел

        :return: None
        """
        self._path = self._path[:-1]
        self._open_key()

    def create_sub_key(self, name: str, open_key: bool = False) -> None:
        """
        Создать подраздел в открытом разделе

        :param name: имя создаваемого подраздела
        :param open_key: если True, откроет этот раздел
        :return: None
        """
        winreg.CreateKey(self.handle, name)
        if open_key:
            self.open_sub_key(name)

    def delete_sub_key(self, name) -> None:
        """
        Удалить подраздел открытого раздела

        :param name: имя удаляемого подраздела
        :return: None
        """
        winreg.DeleteKey(self.handle, name)

    def delete_me(self) -> None:
        """
        Удалить открытый раздел и перейти на родительский

        :return: None
        """
        winreg.DeleteKey(self.hkey, self.key)
        self.backward()

    def delete_value(self, name: str) -> None:
        """
        Удалить параметр открытого раздела

        :param name: имя удаляемого параметра
        :return: None
        """
        winreg.DeleteValue(self.handle, name)

    def enum_key(self) -> Iterable[str]:
        """
        Вернет генератор с именами подразделов открытого раздела
        :return: Iterable[str]
        """
        def name_key():
            i = 0
            while True:
                try:
                    yield winreg.EnumKey(self.handle, i)
                except OSError:
                    break
                i += 1

        return name_key()

    def get_all_sub_key(self) -> list[str]:
        return [name for name in self.enum_key()]

    def enum_value(self) -> Iterable[tuple[str, str, Union[str, int]]]:
        """
        Вернет генератор с параметрами имени, типа и значение открытого раздела
        :return: Iterable[tuple[str, str, Union[str, int]]]
        """
        def values():
            i = 0
            while True:
                try:
                    name, value, type_value = winreg.EnumValue(self.handle, i)
                    yield name, self._types[type_value], value
                except OSError:
                    break
                i += 1

        return values()

    def info_key(self) -> tuple[int, int, int]:
        """
        Вернет информацию об открытом разделе, а именно:
        количество подразделов, количество параметров и
        последнее изменение с 1 янв 1600г. в наносекундах

        :return: tuple[int, int, int]
        """
        return winreg.QueryInfoKey(self.handle)

    def info_value(self, value_name: str) -> tuple[str, Union[str, int]]:
        """
        Вернет информацию о параметре в открытом разделе, а именно:
        тип значение и значение параметра

        :return: tuple[str, Union[str, int]]
        """
        value, type_value = winreg.QueryValueEx(self.handle, value_name)
        return self._types[type_value], value

    def set_value(self, name: str, type: int, value: Union[str, int]) -> None:
        """
        Изменить или создать новый параметра

        :param name: имя параметра
        :param type: тип значение
        :param value: значение параметра
        :return: None
        """
        winreg.SetValueEx(self.handle, name, 0, type, value)


class EasyReg:
    # HKEY_CLASSES_ROOT = 18446744071562067968
    # HKEY_CURRENT_CONFIG = 18446744071562067973
    # HKEY_CURRENT_USER = 18446744071562067969
    # HKEY_DYN_DATA = 18446744071562067974
    # HKEY_LOCAL_MACHINE = 18446744071562067970
    # HKEY_PERFORMANCE_DATA = 18446744071562067972
    # HKEY_USERS = 18446744071562067971

    KEY_ALL_ACCESS = 983103
    KEY_CREATE_LINK = 32
    KEY_CREATE_SUB_KEY = 4
    KEY_ENUMERATE_SUB_KEYS = 8
    KEY_EXECUTE = 131097
    KEY_NOTIFY = 16
    KEY_QUERY_VALUE = 1
    KEY_READ = 131097
    KEY_SET_VALUE = 2
    KEY_WOW64_32KEY = 512
    KEY_WOW64_64KEY = 256
    KEY_WRITE = 131078

    REG_BINARY = 3
    REG_CREATED_NEW_KEY = 1
    REG_DWORD = 4
    REG_DWORD_BIG_ENDIAN = 5
    REG_DWORD_LITTLE_ENDIAN = 4
    REG_EXPAND_SZ = 2
    REG_FULL_RESOURCE_DESCRIPTOR = 9
    REG_LEGAL_CHANGE_FILTER = 268435471
    REG_LEGAL_OPTION = 31
    REG_LINK = 6
    REG_MULTI_SZ = 7
    REG_NONE = 0
    REG_NOTIFY_CHANGE_ATTRIBUTES = 2
    REG_NOTIFY_CHANGE_LAST_SET = 4
    REG_NOTIFY_CHANGE_NAME = 1
    REG_NOTIFY_CHANGE_SECURITY = 8
    REG_NO_LAZY_FLUSH = 4
    REG_OPENED_EXISTING_KEY = 2
    REG_OPTION_BACKUP_RESTORE = 4
    REG_OPTION_CREATE_LINK = 2
    REG_OPTION_NON_VOLATILE = 0
    REG_OPTION_OPEN_LINK = 8
    REG_OPTION_RESERVED = 0
    REG_OPTION_VOLATILE = 1
    REG_QWORD = 11
    REG_QWORD_LITTLE_ENDIAN = 11
    REG_REFRESH_HIVE = 2
    REG_RESOURCE_LIST = 8
    REG_RESOURCE_REQUIREMENTS_LIST = 10
    REG_SZ = 1
    REG_WHOLE_HIVE_VOLATILE = 1

    @staticmethod
    def open(registry_path: str, access: int = winreg.KEY_ALL_ACCESS) -> RegObj:
        return RegObj(registry_path, 'open', access)

    @staticmethod
    def create(registry_path: str, access: int = winreg.KEY_ALL_ACCESS) -> RegObj:
        return RegObj(registry_path, 'create', access)
