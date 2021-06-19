# Предисловие
Библиотека для удобной работой с реестром windows. Является оберткой над стандартной библиотекой `winreg`.

```python
from easy_reg import py_reg

me_reg = py_reg.open(r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer',
                     py_reg.KEY_ALL_ACCESS)
```

## class easy_reg
содержит всего 3 метода:

`open(reg_path: str, access: int = winreg.KEY_ALL_ACCESS) -> RegObj:`

