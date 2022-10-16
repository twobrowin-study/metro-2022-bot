import asyncio
import gspread
import pandas as pd

from settings import SheetsSecret, SheetsName, SheetReport, SheetUpdateTimeout
from log import Log

from info import Info

gc = gspread.service_account(filename=SheetsSecret)
sh = gc.open(SheetsName)
wks = sh.worksheet(SheetReport)

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

class ReportClass():
    def __init__(self) -> None:
        self.valid = self._get_report_df()
        Log.info("Initialized report df")
        Log.debug(self.valid)
    
    async def update(self) -> None:
        while True:
            await asyncio.sleep(SheetUpdateTimeout)
            try:
                self.valid = self._get_report_df()
                Log.info("Updated report df")
                Log.debug(self.valid)
            except Exception as e:
                    Log.info("Got an exception", e)

    def _get_report_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Обозначение группы'] != '') &
            (full_df['Код информации'] != '')
        ]
        return valid

    def check_if_group_did_not_get_code(self, group: str, code: str) -> bool:
        if self.valid.empty:
            return True
        return self.valid.loc[
            (self.valid['Обозначение группы'] == group) &
            (self.valid['Код информации'] == code)
        ].empty
    
    async def write_founded_code(self, group: str, code: str) -> None:
        tmp_df = pd.DataFrame([{
            'Обозначение группы': group,
            'Код информации': code
        }])

        if self.valid.empty:
            self.valid = tmp_df
        else:
            self.valid = self.valid.append(tmp_df)
        
        wks_row = next_available_row(wks)
        wks.update_cell(wks_row, 1, group)
        wks.update_cell(wks_row, 2, code)
        
        Log.info("Wrote to report df")
        Log.debug(self.valid)
    
    def get_report_md(self, group: str = None) -> str:
        report_df = self.valid.loc[self.valid['Обозначение группы'] == group if group != None else self.valid.index]
        if report_df.empty:
            if group == None:
                return "Коды не найдены ни одной из групп"
            return f"Группа {group} - коды не найдены"

        report_df['code_num'] = report_df['Код информации'].map(Info.get_maped_df())
        ans = []
        for group_name, grouped in report_df.sort_values('code_num').groupby('Обозначение группы'):
            group_codes = "".join([ f"  - {x} \n" for x in grouped['Код информации']])
            ans += [f"Группа {group_name} - найдены коды:\n{group_codes}"]
        return "\n".join(ans)

Report = ReportClass()