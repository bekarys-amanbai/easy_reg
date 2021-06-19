import logging
import winreg
from typing import Union, Iterable


log_easy_reg = logging.getLogger('py_reg')


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
            self.ctx_key = winreg.CreateKeyEx(self.hkey, self._key, 0, self._access)
            log_easy_reg.debug(f'open or create[{self.full_path}]')
        else:
            log_easy_reg.exception(f'parameter mode got "{mode}", expected "open" or "create"')
            raise ValueError(f'parameter mode got "{mode}", expected "open" or "create"')

        self._types = ['none', 'sz', 'expand_sz', 'binary', 'dword', 'dword_big_endian', 'link', 'multi_sz',
                       'resource_list', 'full_resource_descriptor', 'resource_requirements_list', 'qword']

    @property
    def full_path(self) -> str:
        """
        Вернет полный путь до открытого раздела

        :return: str
        """
        return '\\'.join(self._path)

    @property
    def key_name(self) -> str:
        """
        Вернет имя открытого раздела

        :return: str
        """
        return self._path[-1]

    @property
    def _key(self) -> str:
        return '\\'.join(self._path[1:])

    def _open_key(self) -> None:
        try:
            self.ctx_key = winreg.OpenKey(self.hkey, self._key, 0, self._access)
            log_easy_reg.debug(f'open [{self.full_path}]')
        except OSError:
            raise

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
        Создать подраздел в открытом разделе. Если указан
        параметр open_key как True, открывает созданный раздел

        :param name: имя создаваемого подраздела
        :param open_key: если True, откроет созданный раздел
        :return: None
        """
        try:
            winreg.CreateKeyEx(self.ctx_key, name, 0, self._access)
            log_easy_reg.debug(f'create [{name}] with [{self.full_path}]')
        except OSError:
            raise
        if open_key:
            self.open_sub_key(name)

    def delete_sub_key(self, name) -> None:
        """
        Удалить подраздел открытого раздела

        :param name: имя удаляемого подраздела
        :return: None
        """
        try:
            winreg.DeleteKey(self.ctx_key, name)
            log_easy_reg.debug(f'delete key [{name}] with [{self.full_path}]')
        except OSError:
            raise

    def delete_me(self) -> None:
        """
        Удалить открытый раздел и перейти на родительский

        :return: None
        """
        try:
            winreg.DeleteKey(self.hkey, self._key)
            log_easy_reg.debug(f'delete key [{self.full_path}]')
        except OSError:
            raise
        self.backward()

    def delete_value(self, name: str) -> None:
        """
        Удалить значение открытого раздела

        :param name: имя удаляемого параметра
        :return: None
        """
        try:
            winreg.DeleteValue(self.ctx_key, name)
            log_easy_reg.debug(f'delete value [{name}] with [{self.full_path}]')
        except OSError:
            raise

    def enum_key(self) -> Iterable[str]:
        """
        Вернет генератор с именами подразделов открытого раздела

        :return: Iterable[str]
        """
        def name_key():
            i = 0
            while True:
                try:
                    yield winreg.EnumKey(self.ctx_key, i)
                except OSError:
                    break
                i += 1

        return name_key()

    def get_all_sub_key(self) -> list[str]:
        return [name for name in self.enum_key()]

    def enum_value(self) -> Iterable[tuple[str, str, Union[str, int]]]:
        """
        Вернет генератор с именем значение, типа и значение из открытого раздела

        :return: Iterable[tuple[str, str, Union[str, int]]]
        """
        def values():
            i = 0
            while True:
                try:
                    name, value, type_value = winreg.EnumValue(self.ctx_key, i)
                    yield name, self._types[type_value], value
                except OSError:
                    break
                i += 1

        return values()

    def get_all_value(self) -> list[tuple[str, str, Union[str, int]]]:
        return [name for name in self.enum_value()]

    def info_key(self) -> tuple[int, int, int]:
        """
        Вернет информацию об открытом разделе, а именно:
        количество подразделов, количество значений и
        последнее изменение с 1 янв 1600г. в наносекундах

        :return: tuple[int, int, int]
        """
        try:
            info = winreg.QueryInfoKey(self.ctx_key)
            log_easy_reg.debug(f'get info key [{self.full_path}]')
            return info
        except OSError:
            raise

    def info_value(self, value_name: str) -> tuple[str, Union[str, int]]:
        """
        Вернет информацию о имени значение в открытом разделе, а именно:
        тип значение и само значение

        :return: tuple[str, Union[str, int]]
        """
        try:
            value, type_value = winreg.QueryValueEx(self.ctx_key, value_name)
            log_easy_reg.debug(f'get info value_name [{value_name}] with [{self.full_path}]')
            return self._types[type_value], value
        except OSError:
            raise

    def set_value(self, name: str, type_value: int, value: Union[str, int]) -> None:
        """
        Изменяет или создает новое значение в открытом разделе

        :param name: имя значение
        :param type_value: тип значение
        :param value: значение
        :return: None
        """
        try:
            winreg.SetValueEx(self.ctx_key, name, 0, type_value, value)
            log_easy_reg.debug(f'set or create value_name:[{name}], value_type:[{self._types[type_value]}], '
                               f'value:[{value}] with [{self.full_path}]')
        except OSError:
            raise


class PyReg:
    # HKEY_CLASSES_ROOT = 18446744071562067968
    # HKEY_CURRENT_CONFIG = 18446744071562067973
    # HKEY_CURRENT_USER = 18446744071562067969
    # HKEY_DYN_DATA = 18446744071562067974
    # HKEY_LOCAL_MACHINE = 18446744071562067970
    # HKEY_PERFORMANCE_DATA = 18446744071562067972
    # HKEY_USERS = 18446744071562067971
    def __init__(self):
        self.KEY_ALL_ACCESS = 983103
        self.KEY_CREATE_LINK = 32
        self.KEY_CREATE_SUB_KEY = 4
        self.KEY_ENUMERATE_SUB_KEYS = 8
        self.KEY_EXECUTE = 131097
        self.KEY_NOTIFY = 16
        self.KEY_QUERY_VALUE = 1
        self.KEY_READ = 131097
        self.KEY_SET_VALUE = 2
        self.KEY_WOW64_32KEY = 512
        self.KEY_WOW64_64KEY = 256
        self.KEY_WRITE = 131078

        self.REG_BINARY = 3
        self.REG_CREATED_NEW_KEY = 1
        self.REG_DWORD = 4
        self.REG_DWORD_BIG_ENDIAN = 5
        self.REG_DWORD_LITTLE_ENDIAN = 4
        self.REG_EXPAND_SZ = 2
        self.REG_FULL_RESOURCE_DESCRIPTOR = 9
        self.REG_LEGAL_CHANGE_FILTER = 268435471
        self.REG_LEGAL_OPTION = 31
        self.REG_LINK = 6
        self.REG_MULTI_SZ = 7
        self.REG_NONE = 0
        self.REG_NOTIFY_CHANGE_ATTRIBUTES = 2
        self.REG_NOTIFY_CHANGE_LAST_SET = 4
        self.REG_NOTIFY_CHANGE_NAME = 1
        self.REG_NOTIFY_CHANGE_SECURITY = 8
        self.REG_NO_LAZY_FLUSH = 4
        self.REG_OPENED_EXISTING_KEY = 2
        self.REG_OPTION_BACKUP_RESTORE = 4
        self.REG_OPTION_CREATE_LINK = 2
        self.REG_OPTION_NON_VOLATILE = 0
        self.REG_OPTION_OPEN_LINK = 8
        self.REG_OPTION_RESERVED = 0
        self.REG_OPTION_VOLATILE = 1
        self.REG_QWORD = 11
        self.REG_QWORD_LITTLE_ENDIAN = 11
        self.REG_REFRESH_HIVE = 2
        self.REG_RESOURCE_LIST = 8
        self.REG_RESOURCE_REQUIREMENTS_LIST = 10
        self.REG_SZ = 1
        self.REG_WHOLE_HIVE_VOLATILE = 1

    @staticmethod
    def open(reg_path: str, access: int = winreg.KEY_ALL_ACCESS) -> RegObj:
        """

        :param reg_path: полный путь к открываемому разделу
        :param access: уровень доступа
            https://docs.python.org/3/library/winreg.html#access-rights
        :return:
        """
        return RegObj(reg_path, 'open', access)

    @staticmethod
    def create(reg_path: str, access: int = winreg.KEY_ALL_ACCESS) -> RegObj:
        return RegObj(reg_path, 'create', access)

    def execute(self, reg_string: str):
        # clear
        while "\n\n" in reg_string:
            reg_string = reg_string.replace("\n\n", "\n")
        reg_string = reg_string.strip()

        rows = reg_string.split('\n')

        reg_obj = None
        for row in rows:
            row = row.strip()
            # del comment
            index_comment = row.find(';')
            if index_comment != -1:
                row = row[:index_comment].strip()

            if row[0] == '[':
                # delete
                if row[1] == '-':
                    reg_path = row[2:-1]
                    reg_obj = RegObj(reg_path, 'open', winreg.KEY_ALL_ACCESS)
                    reg_obj.delete_me()
                    continue
                # change
                else:
                    reg_path = row[1:-1]
                    reg_obj = RegObj(reg_path, 'create', winreg.KEY_ALL_ACCESS)
                    continue

            name, type_and_value = row.split('=')
            name = name.replace('"', '')
            if name == '@':
                name = ''

            if type_and_value == '-':
                reg_obj.delete_value(name)
                continue

            if ':' in type_and_value:
                type_value, value = type_and_value.split(':')
                if type_value == 'dword':
                    reg_obj.set_value(name, self.REG_DWORD, int(value, 16))
                elif type_value == 'hex':
                    value = value.replace(',', '')
                    reg_obj.set_value(name, self.REG_BINARY, value.encode())
            else:
                value = type_and_value
                reg_obj.set_value(name, self.REG_SZ, value)
