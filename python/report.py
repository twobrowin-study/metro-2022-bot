import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetReport
from log import Log

from info import Info

class ReportClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
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
        
        wks_row = self._next_available_row()
        self.wks.update_cell(wks_row, 1, group)
        self.wks.update_cell(wks_row, 2, code)
        
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

Report = ReportClass(SheetReport, 'report')