from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import MessageEntityType

import pandas as pd

from telegram import PhotoSize, Animation, Audio, Voice, Video, VideoNote

from telegram.constants import ParseMode

import json

from log import Log
from help import Help
from info import Info
from groups import Groups
from pivot import Pivot

from state import State

from info import LAST_CODE

async def ChatJoinHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"I've join chat {update.effective_chat.id}")

async def HelpHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    group_letter = Groups.get_group_letter_by_id(chat_id)
    admin_status = Groups.get_group_admin_status_by_id(chat_id)
    Log.debug(f"Got help request from chat {chat_id} as group {group_letter}")
    await update.message.reply_markdown(Help.get_help(admin_status, group_letter))

async def PivotHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for entity in update.message.entities:
        if entity.type == MessageEntityType.BOT_COMMAND:
            command = update.message.parse_entity(entity)[1:].split('@')[0]
            normal_group_name = Groups.get_normal_group_name_by_pivot_command(command)
            Log.debug(f"Got pivot request from with command {command} - as normal group {normal_group_name}")
            await update.message.reply_markdown(Pivot.get_pivot_md(normal_group_name))

async def InfoHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    code = update.effective_message.text
    group_letter = Groups.get_group_letter_by_id(chat_id)
    
    Log.debug(f"Got info request from chat {chat_id} as group {group_letter} with code {code}")
    info = Info.get_info_dy_code(code)
    team = info['Команда']
    await reply_to_code(update, context, info)
    Pivot.write_founded_code(group_letter, code, team, context.application)

    if Pivot.group_found_all_codes_but_last(group_letter, team):
        Log.debug(f"Chat {chat_id} as group {group_letter} founded the last code for team {team}! Congrats!")
        await reply_to_code(update, context, Info.get_info_dy_code(LAST_CODE, team=team))
        for admin_id in Groups.get_all_admin_groups():
            await context.bot.send_message(admin_id, f"Группа *{group_letter}* нашла все коды команды *{team}*!", parse_mode=ParseMode.MARKDOWN)
        Pivot.write_founded_code(group_letter, LAST_CODE, team, context.application)

async def reply_to_code(update: Update, context: ContextTypes.DEFAULT_TYPE, info: pd.Series) -> None:
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

async def CancelHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['notify'] = False
    State['add'] = 'start'
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
    State['add'] = 'code'
    Log.debug(f"Start add")
    await update.message.reply_markdown("Введите код загадки - текст без пробелов")

async def AddCodeHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "" or update.message.text == None or " " in update.message.text:
        await update.message.reply_markdown("Код некорректен - повторите")
        return
    State['add'] = 'team'
    State['add_code'] = update.message.text
    Log.debug(f"Saved add code {State['add_code']}")
    await update.message.reply_markdown("Введите номер команды для загадки - цифра `1`, `2` или `3`",
        reply_markup=ReplyKeyboardMarkup([["1", "2", "3"]])
    )

async def AddTeamHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "" or update.message.text == None or update.message.text not in ['1', '2', '3']:
        await update.message.reply_markdown("Не получен код - повторите")
        return
    State['add'] = 'data'
    State['add_team'] = update.message.text
    Log.debug(f"Saved add team {State['add_team']}")
    await update.message.reply_markdown("""
Теперь перешлите информацию - одно из:
  - текст - будет сохранён с форматированием
  - фото
  - анимация
  - аудиофайл
  - голосовое сообщение
  - видеофайл
  - круглешок
  - геолокация
  - документ - только один
""", reply_markup=ReplyKeyboardRemove())

async def AddDataHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    State['add'] = 'start'
    code = State['add_code']
    team = State['add_team']

    Log.debug(f"Add ended and saved with code {code} for team {team}")
    await update.message.reply_markdown("Загадка добавлена")
    
    text = update.message.text_markdown_v2
    caption = update.message.caption_markdown_v2

    context.application.create_task(Info.write_new_info(
        code, team,
        text if text != None else caption,
        update.message.photo,
        update.message.animation,
        update.message.audio,
        update.message.voice,
        update.message.video,
        update.message.video_note,
        update.message.location,
        update.message.document,
    ))

async def AllHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(Info.get_all_codes_md())