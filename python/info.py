from telegram import PhotoSize, Animation, Audio, Voice, Video, VideoNote, Location, Document

import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetInfo
from log import Log

LAST_CODE = 'last'

class InfoClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Код'] != '') &
            (full_df['Команда'] != '') &
            (
                (full_df['Текстовая информация'] != '') |
                (full_df['Изображение'] != '') |
                (full_df['Анимация'] != '') |
                (full_df['Аудио'] != '') |
                (full_df['Голос'] != '') |
                (full_df['Видео'] != '') |
                (full_df['Круглешок'] != '') |
                (full_df['Геолокация'] != '') |
                (full_df['Документ'] != '')
            )
        ]
        for str_name in ['Код', 'Команда', 'Текстовая информация']:
            valid[str_name] = valid[str_name].apply(str)
        return valid
        
    def get_info_dy_code(self, code: str, team: str = None) -> pd.Series:
        if team == None:
            for _,row in self.valid.loc[self.valid['Код'] == code].iterrows():
                return row
        else:
            for _,row in self.valid.loc[
                (self.valid['Код'] == code) &
                (self.valid['Команда'] == team)
            ].iterrows():
                return row
        return None

    def check_if_code_exists(self, code: str) -> bool:
        return not self.valid.loc[self.valid['Код'] == code].empty

    def check_if_code_exists_but_not_last(self, code: str) -> bool:
        return code != LAST_CODE and self.check_if_code_exists(code)
    
    def get_maped_df(self) -> pd.Series:
        return self.valid.reset_index().set_index('Код')['index']
    
    def get_all_codes(self) -> pd.DataFrame:
        if self.valid.empty:
            return []
        return self.valid[['Код', 'Команда']]
    
    def get_all_codes_but_last_for_team(self, team: str) -> list[str]:
        if self.valid.empty:
            return []
        return self.valid[(self.valid['Код'] != LAST_CODE) & (self.valid['Команда'] == team)]['Код'].to_list()
    
    def get_all_codes_md(self) -> str:
        if self.valid.empty:
            return "Коды ещё не добавлены"
        ans = "Все коды:\n"
        ans += "".join([ f"  - `{x['Код']}` - команда *{x['Команда']}* \n" for _,x in self.get_all_codes().iterrows()])
        return ans

    async def write_new_info(self, code: str, team: str,
        text_markdown_v2: str,
        photo: list[PhotoSize],
        animation: Animation,
        audio: Audio,
        voice: Voice,
        video: Video,
        video_note: VideoNote,
        location: Location,
        document: Document,
    ) -> None:
        photo_stored = photo[-1].to_json() if photo != [] else ""
        animation_stored = animation.to_json() if animation != None else ""
        audio_stored = audio.to_json() if audio != None else ""
        voice_stored = voice.to_json() if voice != None else ""
        video_stored = video.to_json() if video != None else ""
        video_note_stored = video_note.to_json() if video_note != None else ""
        location_stored = location.to_json() if location != None else ""
        document_stored = document.to_json() if document != None else ""

        tmp_df = pd.DataFrame([{
            'Код': code,
            'Команда': team,
            'Текстовая информация': text_markdown_v2,
            'Изображение': photo_stored,
            'Анимация': animation_stored,
            'Аудио': audio_stored,
            'Голос': voice_stored,
            'Видео': video_stored,
            'Круглешок': video_note_stored,
            'Геолокация': location_stored,
            'Документ': document_stored,
        }])

        if self.valid.empty:
            self.valid = tmp_df
        else:
            self.valid = pd.concat([self.valid, tmp_df], ignore_index=True)
        
        wks_row = self._next_available_row()
        self.wks.update_cell(wks_row, 1, code)
        self.wks.update_cell(wks_row, 2, team)
        self.wks.update_cell(wks_row, 3, text_markdown_v2)
        self.wks.update_cell(wks_row, 4, photo_stored)
        self.wks.update_cell(wks_row, 5, animation_stored)
        self.wks.update_cell(wks_row, 6, audio_stored)
        self.wks.update_cell(wks_row, 7, voice_stored)
        self.wks.update_cell(wks_row, 8, video_stored)
        self.wks.update_cell(wks_row, 9, video_note_stored)
        self.wks.update_cell(wks_row, 10, location_stored)
        self.wks.update_cell(wks_row, 11, document_stored)
        
        Log.info(f"Wrote to {self.name} df")
        Log.debug(self.valid)

Info = InfoClass(SheetInfo, 'info')