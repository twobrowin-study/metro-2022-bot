from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import MessageEntityType

from telegram import PhotoSize, Animation, Audio, Voice, Video, VideoNote

import json

from log import Log
from help import Help
from info import Info
from groups import Groups
from report import Report

from state import State

async def ChatJoinHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"I've join chat {update.effective_chat.id}")

async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    group_letter = Groups.get_group_letter_by_id(chat_id)
    admin_status = Groups.get_group_admin_status_by_id(chat_id)
    Log.debug(f"Got help request from chat {chat_id} as group {group_letter}")
    await update.message.reply_markdown(Help.get_help(admin_status, group_letter))

async def ReportHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for entity in update.message.entities:
        if entity.type == MessageEntityType.BOT_COMMAND:
            command = update.message.parse_entity(entity)[1:].split('@')[0]
            normal_group_name = Groups.get_normal_group_name_by_report_command(command)
            Log.debug(f"Got report request from with command {command} - as normal group {normal_group_name}")
            await update.message.reply_markdown(Report.get_report_md(normal_group_name))

async def InfoHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    code = update.effective_message.text
    group_letter = Groups.get_group_letter_by_id(chat_id)
    
    Log.debug(f"Got info request from chat {chat_id} as group {group_letter} with code {code}")
    
    info = Info.get_info_dy_code(code)

    if info['Текстовая информация'] != "":
        await update.message.reply_markdown_v2(info['Текстовая информация'])

    if info['Изображение'] != "":
        json_tmp = json.loads(info['Изображение'])
        obj_tmp = PhotoSize.de_json(json_tmp, context.bot)
        await update.message.reply_photo(obj_tmp)

    if info['Анимация'] != "":
        json_tmp = json.loads(info['Анимация'])
        obj_tmp = Animation.de_json(json_tmp, context.bot)
        await update.message.reply_animation(obj_tmp)

    if info['Аудио'] != "":
        json_tmp = json.loads(info['Аудио'])
        obj_tmp = Audio.de_json(json_tmp, context.bot)
        await update.message.reply_audio(obj_tmp)

    if info['Голос'] != "":
        json_tmp = json.loads(info['Голос'])
        obj_tmp = Voice.de_json(json_tmp, context.bot)
        await update.message.reply_voice(obj_tmp)

    if info['Видео'] != "":
        json_tmp = json.loads(info['Видео'])
        obj_tmp = Video.de_json(json_tmp, context.bot)
        await update.message.reply_video(obj_tmp)

    if info['Круглешок'] != "":
        json_tmp = json.loads(info['Круглешок'])
        obj_tmp = VideoNote.de_json(json_tmp, context.bot)
        await update.message.reply_video_note(obj_tmp)

    if info['Геолокация'] != "":
        json_tmp = json.loads(info['Геолокация'])
        await update.message.reply_location(json_tmp['latitude'], json_tmp['longitude'])
    
    context.application.create_task(Report.write_founded_code(group_letter, code))

async def CancelHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['notify'] = False
    State['add'] = (False, False)
    Log.debug(f"Cancel last operation")
    await update.message.reply_markdown("Все операции отменены")

async def NotifyStartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['notify'] = True
    Log.debug(f"Start notify")
    await update.message.reply_markdown("Теперь введите сообщение для оповещения")

async def NotifyEndHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['notify'] = False
    Log.debug(f"End notify")
    for group_id in Groups.get_all_normal_groups():
        Log.debug(f"Send notify to chat {group_id}")
        await update.message.copy(group_id)
    await update.message.reply_markdown("Оповещение отправлено")

async def AddStartHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['add'] = (True, False)
    Log.debug(f"Start add")
    await update.message.reply_markdown("Введите код загадки - любой текст")

async def AddMidleHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "" or update.message.text == None:
        await update.message.reply_markdown("Не получен код - повторите")
        return
    State['add'] = (True, True)
    State['add_code'] = update.message.text
    Log.debug(f"Saved add code {State['add_code']}")
    await update.message.reply_markdown("""
Теперь перешлите информацию - одно из:
  - текст - будет сохранён с форматированием
  - фото - будет сохранено без подписи
  - анимация
  - аудиофайл
  - голосовое сообщение
  - видеофайл
  - круглешок
  - геолокация
""")

async def AddEndHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['add'] = (False, False)
    code = State['add_code']

    Log.debug(f"Add ended and saved with code {code}")
    await update.message.reply_markdown("Загадка добавлена")
    
    context.application.create_task(Info.write_new_info(
        code,
        update.message.text_markdown_v2,
        update.message.photo,
        update.message.animation,
        update.message.audio,
        update.message.voice,
        update.message.video,
        update.message.video_note,
        update.message.location,
    ))