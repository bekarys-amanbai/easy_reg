# Предисловие
Библиотека для удобной работой с реестром windows. Является оберткой над стандартной библиотекой `winreg`.

```python
from py_reg import py_reg

me_reg = py_reg.open(r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer',
                     py_reg.KEY_ALL_ACCESS,
                     create=True)
```

## class PyReg
содержит куча атрбиутов и всего 2 метода:

`open(reg_path: str, access: int = winreg.KEY_ALL_ACCESS, create: bool = False) -> RegObj:`

открывает ключ; eсли он не существует, вызывает ошибку OSError, если 'create' не указан как True
- `reg_path`: полный путь к открываемому разделу
- `access`: уровень доступа https://docs.python.org/3/library/winreg.html#access-rights
- `create`: создать ключ, если он не существует

`execute(self, reg_string: str):`

Парсит строку с .reg командами. На данный момент поддерживает только типы DWORD, BINARY, SZ

## class RegObj

### атрибуты
- `full_path` - Вернет полный путь до открытого раздела
- `key_name` - Вернет имя открытого раздела

### методы
#### `open_sub_key(self, name: str) -> None`:
Открыть подраздел открытого раздела

#### `backward(self) -> None:`
Перейти на родительский раздел

#### `create_sub_key(self, name: str, open_key: bool = False) -> None:`
Создать подраздел в открытом разделе. Если указан параметр open_key как True, открывает созданный раздел

#### `delete_sub_key(self, name) -> None:`
Удалить подраздел открытого раздела

#### `delete_me(self) -> None:`
Удалить открытый раздел и перейти на родительский

#### `delete_value(self, name: str) -> None:`
Удалить значение открытого раздела

#### `enum_key(self) -> Iterable[str]:`
Вернет генератор с именами подразделов открытого раздела

#### `get_all_sub_key(self) -> list[str]`
Вернет все ключи открытого раздела

#### `enum_value(self) -> Iterable[tuple[str, str, Union[str, int]]]:`
Вернет генератор с именем значение, типа и значение из открытого раздела

#### `get_all_value(self) -> list[tuple[str, str, Union[str, int]]]:`
Вернет список именем значение, типа и значение из открытого раздела

#### `info_key(self) -> tuple[int, int, int]:`
Вернет информацию об открытом разделе, а именно: количество подразделов, количество значений и последнее изменение с 1 янв 1600г. в наносекундах

#### `info_value(self, value_name: str) -> tuple[str, Union[str, int]]:`
Вернет информацию о имени значение в открытом разделе, а именно: тип значение и само значение

#### `set_value(self, name: str, type_value: int, value: Union[str, int]) -> None:`
Изменяет или создает новое значение в открытом разделе
