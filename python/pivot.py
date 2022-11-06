import pandas as pd

from telegram.ext import Application

from sheet import AbstractSheetAdapter

from settings import SheetPivot
from log import Log

from info import Info

class PivotClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Обозначение группы'] != '') &
            (full_df['Код информации'] != '') &
            (full_df['Команда'] != '')
        ]
        return valid

    def check_if_group_did_not_get_code(self, group: str, code: str) -> bool:
        if self.valid.empty:
            return True
        return self.valid.loc[
            (self.valid['Обозначение группы'] == group) &
            (self.valid['Код информации'] == code)
        ].empty
    
    def write_founded_code(self, group: str, code: str, team: str, app: Application) -> None:
        tmp_df = pd.DataFrame([{
            'Обозначение группы': group,
            'Код информации': code,
            'Команда': team
        }])

        if self.valid.empty:
            self.valid = tmp_df
        else:
            self.valid = pd.concat([self.valid, tmp_df], ignore_index=True)    
        Log.info("Wrote to pivot df")
        Log.debug(self.valid)

        app.create_task(self._write_founded_code_wks(group, code, team))
    
    async def _write_founded_code_wks(self, group: str, code: str, team: str) -> None:
        wks_row = self._next_available_row()
        self.wks.update_cell(wks_row, 1, group)
        self.wks.update_cell(wks_row, 2, code)
        self.wks.update_cell(wks_row, 3, team)
    
    def get_pivot_md(self, group: str = None) -> str:
        pivot_df = self.valid.loc[self.valid['Обозначение группы'] == group if group != None else self.valid.index]
        if pivot_df.empty:
            if group == None:
                return "Коды не найдены ни одной из групп"
            return f"Группа {group} - коды не найдены"

        pivot_df['code_num'] = pivot_df['Код информации'].map(Info.get_maped_df())
        ans = []
        for group_name, grouped in pivot_df.sort_values('code_num').groupby('Обозначение группы'):
            group_codes = "".join([ f"  - {x} \n" for x in grouped['Код информации']])
            ans += [f"Группа {group_name} - найдены коды:\n{group_codes}"]
        return "\n".join(ans)
    
    def group_found_all_codes_but_last(self, group: str, team: str) -> bool:
        if self.valid.empty:
            return False
        founded_codes = self.valid.loc[
            (self.valid['Обозначение группы'] == group) &
            (self.valid['Команда'] == team)
        ]['Код информации'].to_list()
        all_codes_but_last = Info.get_all_codes_but_last_for_team(team)
        return set(founded_codes) == set(all_codes_but_last)

Pivot = PivotClass(SheetPivot, 'pivot')