from telegram import PhotoSize, Animation, Audio, Voice, Video, VideoNote, Location

import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetInfo
from log import Log

LAST_CODE = 'last'

class InfoClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
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

    def check_if_code_exists_but_not_last(self, code: str) -> bool:
        return code != LAST_CODE and self.check_if_code_exists(code)
    
    def get_maped_df(self) -> pd.Series:
        return self.valid.reset_index().set_index('Код')['index']
    
    def get_all_codes(self) -> list[str]:
        return self.valid['Код'].to_list()
    
    def get_all_codes_but_last(self) -> list[str]:
        return self.valid[self.valid['Код'] != LAST_CODE]['Код'].to_list()
    
    def get_all_codes_md(self) -> str:
        ans = "Все коды:\n"
        ans += "".join([ f"  - {x} \n" for x in self.get_all_codes()])
        return ans

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
        
        wks_row = self._next_available_row()
        self.wks.update_cell(wks_row, 1, code)
        self.wks.update_cell(wks_row, 2, text_markdown_v2)
        self.wks.update_cell(wks_row, 3, photo_stored)
        self.wks.update_cell(wks_row, 4, animation_stored)
        self.wks.update_cell(wks_row, 5, audio_stored)
        self.wks.update_cell(wks_row, 6, voice_stored)
        self.wks.update_cell(wks_row, 7, video_stored)
        self.wks.update_cell(wks_row, 8, video_note_stored)
        self.wks.update_cell(wks_row, 9, location_stored)
        
        Log.info(f"Wrote to {self.name} df")
        Log.debug(self.valid)

Info = InfoClass(SheetInfo, 'info')