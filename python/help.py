import asyncio
import gspread
import pandas as pd

from settings import SheetsSecret, SheetsName, SheetHelp, SheetUpdateTimeout
from log import Log

from groups import Groups

gc = gspread.service_account(filename=SheetsSecret)
sh = gc.open(SheetsName)
wks = sh.worksheet(SheetHelp)

class HelpClass():
    def __init__(self) -> None:
        self.valid = self._get_help_df()
        Log.info("Initialized help df")
        Log.debug(self.valid)
    
    async def update(self) -> None:
        while True:
            await asyncio.sleep(SheetUpdateTimeout)
            self.valid = self._get_help_df()
            Log.info("Updated help df")
            Log.debug(self.valid)

    def _get_help_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(wks.get_all_records())
        valid = full_df.loc[
            (full_df['Администратор'] != '') &
            (full_df['Помощь'] != '')
        ]
        return valid

    def get_help(self, admin_status: str, group_letter: str) -> str:
        for _, row in self.valid.loc[self.valid['Администратор'] == admin_status].iterrows():
            return row['Помощь'].format(
                group_letter = group_letter,
                admin_report = Groups.get_admin_report(),
                groups_reports = "".join([ f"  - /{x[0]} группа {x[1]}\n" for x in zip(Groups.get_groups_reports(), Groups.get_groups_names()) ])
            )
        return

Help = HelpClass()