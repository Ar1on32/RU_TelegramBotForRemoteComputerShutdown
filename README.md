# RU_tgBOT_off--сomputer

### Бот сделан на Python 21.6


# Пояснение

Это бот для удаленного выключения ПК(Персональный комютер) через Telegram.

# Функционал

1. `/shutdown` - выключить компьютер через 5 секунд
2. `/timer_shutdown` - выключить компьютер через указанное количество секунд
3. `/status` - получить статус системы(Бот покажет Загрузку ЦП,ГП, Оперативной памяти и темперутуру ГП)
4. `/screenshot` - получить скриншот экрана(Делает скриншот того что в данный момент показано на экране)

# Что нужно поменять в коде что бы он работал:

1. Поставить Ваш токен(можно получать в BotFather в Telegram)
2. Поставить id Telegram человека который сможет выключать компьютер(конечно желательно самого себя)
3. Поставить свой сообственный пароль
4. Указать путь к изображению(это иконка которая будет отоброжаться в скрытых значках в панели задач)

# Библиотеки
```
pip install python-telegram-bot
pip install PyQt5
pip install urllib3
pip install six
pip install psutil
pip install pyautogui
pip install GPUtil
```

> [!IMPORTANT]
> - После того как вы поменяли всё что нужно, сохраняйте и поменяйте формат файла `py` на `pyw` (таким образом, когда бот будет включаться не будет открываться консоль)
> 
> - Скомилируйте файл pyw с icon.png  и получите .exe
> 
> - Отправляйте файл .exe в Автозагрузку(win+r--->shell:startup)
> 
> - При включении ПК у вас на панели задач в скрытых значках появиться новая иконка, это и есть Ваш бот, если появился значит работает.

### Берем телефон --> уходим по своим делам оставив ПК включённым --> открываем бота и выключаем компьютер через команду /shutdown и ура победа!

