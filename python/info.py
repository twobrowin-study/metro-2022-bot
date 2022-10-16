from telegram import PhotoSize, Animation, Audio, Voice, Video, VideoNote, Location

import asyncio
import gspread
import pandas as pd

from settings import SheetsSecret, SheetsName, SheetInfo, SheetUpdateTimeout
from log import Log

gc = gspread.service_account(filename=SheetsSecret)
sh = gc.open(SheetsName)
wks = sh.worksheet(SheetInfo)

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

class InfoClass():
    def __init__(self) -> None:
        self.valid = self._get_info_df()
        Log.info("Initialized info df")
        Log.debug(self.valid)
    
    async def update(self) -> None:
        while True:
            await asyncio.sleep(SheetUpdateTimeout)
            try:
                self.valid = self._get_info_df()
                Log.info("Updated info df")
                Log.debug(self.valid)
            except Exception as e:
                    Log.info("Got an exception", e)

    def _get_info_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(wks.get_all_records())
        valid = full_df.loc[
            (full_df['Код'] != '') &
            (
                (full_df['Текстовая информация'] != '') |
                (full_df['Изображение'] != '') |
                (full_df['Анимация'] != '') |
                (full_df['Аудио'] != '') |
                (full_df['Голос'] != '') |
                (full_df['Видео'] != '') |
                (full_df['Круглешок'] != '') |
                (full_df['Геолокация'] != '')
            )
        ]
        return valid
        
    def get_info_dy_code(self, code: str) -> pd.Series:
        for _,row in self.valid.loc[self.valid['Код'] == code].iterrows():
            return row
        return None

    def check_if_code_exists(self, code: str) -> bool:
        return not self.valid.loc[self.valid['Код'] == code].empty
    
    def get_maped_df(self) -> pd.Series:
        return self.valid.reset_index().set_index('Код')['index']

    async def write_new_info(self, code: str,
        text_markdown_v2: str,
        photo: list[PhotoSize],
        animation: Animation,
        audio: Audio,
        voice: Voice,
        video: Video,
        video_note: VideoNote,
        location: Location,
    ) -> None:
        photo_stored = photo[-1].to_json() if photo != [] else ""
        animation_stored = animation.to_json() if animation != None else ""
        audio_stored = audio.to_json() if audio != None else ""
        voice_stored = voice.to_json() if voice != None else ""
        video_stored = video.to_json() if video != None else ""
        video_note_stored = video_note.to_json() if video_note != None else ""
        location_stored = location.to_json() if location != None else ""

        tmp_df = pd.DataFrame([{
            'Код': code,
            'Текстовая информация': text_markdown_v2,
            'Изображение': photo_stored,
            'Анимация': animation_stored,
            'Аудио': audio_stored,
            'Голос': voice_stored,
            'Видео': video_stored,
            'Круглешок': video_note_stored,
            'Геолокация': location_stored,
        }])

        if self.valid.empty:
            self.valid = tmp_df
        else:
            self.valid = self.valid.append(tmp_df)
        
        wks_row = next_available_row(wks)
        wks.update_cell(wks_row, 1, code)
        wks.update_cell(wks_row, 2, text_markdown_v2)
        wks.update_cell(wks_row, 3, photo_stored)
        wks.update_cell(wks_row, 4, animation_stored)
        wks.update_cell(wks_row, 5, audio_stored)
        wks.update_cell(wks_row, 6, voice_stored)
        wks.update_cell(wks_row, 7, video_stored)
        wks.update_cell(wks_row, 8, video_note_stored)
        wks.update_cell(wks_row, 9, location_stored)
        
        Log.info("Wrote to report df")
        Log.debug(self.valid)

Info = InfoClass()