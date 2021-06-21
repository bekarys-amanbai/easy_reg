import pytest

from py_reg import py_reg, RegObj


@pytest.fixture
def open_key():
    open_key = py_reg.open(r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer')

    open_key.create_sub_key('AAA_TEST_EASY_REG', True)
    return open_key


def test_backward():
    pass


def test_open_sub_key():
    pass


@pytest.mark.parametrize("key", ['My List', 'Blander', 'Doctor', 'Micro'])
def test_create_sub_key(open_key: RegObj, key):
    open_key.create_sub_key(key)

    assert key in open_key.get_all_sub_key()


def test_delete_sub_key():
    pass


def test_delete_me():
    pass


def test_enum_key():
    pass


def test_get_all_sub_key():
    pass


def test_enum_value():
    pass


def test_info_key():
    pass


def test_info_value():
    pass


@pytest.mark.parametrize("name, type, value", [
    ('Zero', py_reg.REG_DWORD, 0),
    ('One', py_reg.REG_DWORD, 1),
    ('Dwatchat', py_reg.REG_DWORD, 20),
    ('Milion', py_reg.REG_DWORD, 1_000_000),

    ('Zeros_z', py_reg.REG_SZ, ''),
    ('Ones_z', py_reg.REG_SZ, 'fea'),
    ('Dwatchat_sz', py_reg.REG_SZ, 'b4iifj;as'),
    ('Milion_sz', py_reg.REG_SZ, 'bfa45y&(*&fs'),

    ('Zero_b', py_reg.REG_BINARY, b'0'),
    ('One_b', py_reg.REG_BINARY, b'1'),
    ('Dwatchat_b', py_reg.REG_BINARY, b'20'),
    ('Milion_b', py_reg.REG_BINARY, b'1_000_000'),
    ('Zero_sz_b', py_reg.REG_BINARY, None),  # если value = b'' то из реестра вернет None
    ('One_sz_b', py_reg.REG_BINARY, b'fea'),
    ('Dwatchat_sz_b', py_reg.REG_BINARY, b'b4iifj;as'),
    ('Milion_sz_b', py_reg.REG_BINARY, b'bfa45y&(*&fs'),
])
def test_set_value(open_key: RegObj, name, type, value):
    open_key.set_value(name, type, value)
    got_type, got_value = open_key.info_value(name)

    assert open_key._types.index(got_type) == type
    assert got_value == value


@pytest.mark.parametrize("name", ('Zero', 'One', 'Dwatchat', 'Milion', 'Zeros_z', 'Ones_z', 'Dwatchat_sz',
                                  'Milion_sz', 'Zero_b', 'One_b', 'Dwatchat_b', 'Milion_b', 'Zero_sz_b',
                                  'One_sz_b', 'Dwatchat_sz_b', 'Milion_sz_b',))
def test_delete_value(open_key: RegObj, name):
    got_type, got_value = open_key.info_value(name)
    assert got_type

    open_key.delete_value(name)
    for got_name, _, _ in open_key.enum_value():
        assert name != got_name
