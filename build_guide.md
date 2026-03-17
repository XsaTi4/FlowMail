# Инструкция по сборке (Компиляция в .exe / .app)

Для того чтобы скомпилировать приложение в исполняемый файл и передавать его другим пользователям без установки Python, мы будем использовать `PyInstaller`.

## 1. Подготовка

В терминале (при активированном venv) установите `pyinstaller` и убедитесь, что папка с системными шаблонами создана:
```bash
pip install pyinstaller
python generate_templates.py
```

Перед сборкой проверьте production-режим `pywebview` в `app.py`:
```python
webview.start(debug=False)
```

## 2. Рекомендуемая сборка через `.spec` (Windows / Mac)

Выполняйте команду в корне проекта:
```bash
pyinstaller --noconfirm FlowMail.spec
```

Этот способ использует параметры из `FlowMail.spec`, где уже зафиксированы:
- `console=False` (без консольного окна)
- `debug=False` (без DevTools при запуске)

## 3. Альтернативная ручная сборка

Если нужно собрать без `.spec`, используйте команды ниже.

**Windows (.exe):**
```bash
pyinstaller --noconfirm --onedir --windowed --icon "icon.ico" --name "FlowMail" --add-data "ui;ui/" --add-data "data/templates;data/templates/" "app.py"
```

**Mac (.app):**
```bash
pyinstaller --noconfirm --onedir --windowed --icon "icon.ico" --name "FlowMail" --add-data "ui:ui/" --add-data "data/templates:data/templates/" "app.py"
```

---
**Важные нюансы:**
- **Пути:** Программа теперь корректно находит UI и шаблоны внутри скомпилированного пакета.
- **Данные:** Все ваши настройки, шаблоны и очередь теперь сохраняются в папке пользователя: `~/.flowmail_data` (на Linux/Mac) или `C:\Users\Имя\.flowmail_data` (на Windows). Это сделано для того, чтобы приложение не вылетало из-за ограничений прав доступа в папке с программой.
- **Первый запуск:** При первом открытии Mac может потребовать подтверждение (ПКМ -> Открыть).
- Временные папки `build`, `dist` и файлы `.spec` можно удалять после сборки.
