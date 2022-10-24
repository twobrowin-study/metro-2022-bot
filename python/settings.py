from os import environ, getenv

BotToken = environ.get('BOT_TOKEN')
if BotToken == '' or BotToken == None:
    with open('telegram.txt', 'r') as fp:
        BotToken = fp.read()

SheetsAccJson = environ.get('SHEETS_ACC_JSON')
SheetsSecret = './serviceacc.json'
if SheetsAccJson != None and SheetsAccJson != '':
    with open(SheetsSecret, 'w') as fp:
        fp.write(SheetsAccJson)

SheetsName = getenv('SHEETS_NAME', 'Таблица бота Метро 2022')

SheetGroups = getenv('SHEET_GROUPS', 'Группы')
SheetInfo = getenv('SHEET_INFO', 'Таблица информации')
SheetPivot = getenv('SHEET_PIVOT', 'Сводная таблица кто и что нашёл')
SheetHelp = getenv('SHEET_HELP', 'Помощь по боту')

SheetUpdateTimeout = int(getenv('SHEET_UPDATE_TIMEOUT', '10'))