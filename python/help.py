import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetHelp
from log import Log

from groups import Groups

class HelpClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
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

Help = HelpClass(SheetHelp, 'help')