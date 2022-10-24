import pandas as pd

from sheet import AbstractSheetAdapter

from settings import SheetGroups
from log import Log

class GroupsClass(AbstractSheetAdapter):
    def _get_df(self) -> pd.DataFrame:
        full_df = pd.DataFrame(self.wks.get_all_records())
        if full_df.empty:
            return full_df
        valid = full_df.loc[
            (full_df['Id'] != '') &
            (full_df['Обозначение'] != '') &
            (full_df['Команда отчёта'] != '') &
            (full_df['Администратор'] != '')
        ]
        return valid
    
    def get_group_letter_by_id(self, chat_id: int) -> str:
        for _,row in self.valid.loc[self.valid['Id'] == chat_id].iterrows():
            return row['Обозначение']
        return ""
    
    def get_group_admin_status_by_id(self, chat_id: int) -> str:
        for _,row in self.valid.loc[self.valid['Id'] == chat_id].iterrows():
            return row['Администратор']
        return ""
    
    def check_if_group_registered(self, chat_id: int) -> bool:
        return not self.valid.loc[self.valid['Id'] == chat_id].empty
    
    def check_if_group_admin(self, chat_id: int) -> bool:
        return not self.valid.loc[(self.valid['Id'] == chat_id) & (self.valid['Администратор'] == 'Да')].empty
    
    def get_all_pivot_commands(self) -> list[str]:
        return self.valid['Команда отчёта'].values.tolist()
    
    def get_admin_pivot(self) -> list[str]:
        for _,row in self.valid.loc[self.valid['Администратор'] == 'Да'].iterrows():
            return row['Команда отчёта']
        return ""

    def get_groups_pivots(self) -> list[str]:
        return self.valid.loc[self.valid['Администратор'] == 'Нет']['Команда отчёта'].values.tolist()

    def get_groups_names(self) -> list[str]:
        return self.valid.loc[self.valid['Администратор'] == 'Нет']['Обозначение'].values.tolist()
    
    def get_normal_group_name_by_pivot_command(self, pivot_command: str) -> str:
        for _,row in self.valid.loc[self.valid['Команда отчёта'] == pivot_command].iterrows():
            return row['Обозначение'] if row['Администратор'] == 'Нет' else None
        return ""
    
    def get_all_normal_groups(self) -> list[str]:
        return self.valid.loc[self.valid['Администратор'] == 'Нет']['Id'].values.tolist()
    
    def get_all_admin_groups(self) -> list[str]:
        return self.valid.loc[self.valid['Администратор'] == 'Да']['Id'].values.tolist()
        
Groups = GroupsClass(SheetGroups, 'groups')