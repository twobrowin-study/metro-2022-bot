from telegram import Message
from telegram.ext.filters import MessageFilter

from groups import Groups
from info import Info
from report import Report

from state import State

class GroupRegisteredClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Groups.check_if_group_registered(message.chat_id)

class GroupIsAdminClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return Groups.check_if_group_admin(message.chat_id)

class InfoKeySolvedClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        chat_id = message.chat_id
        code = message.text
        
        admin_status = Groups.get_group_admin_status_by_id(chat_id)
        if admin_status == 'Да':
            return False
        
        code_exists = Info.check_if_code_exists(code)
        if code_exists == False:
            return False
        
        group_letter = Groups.get_group_letter_by_id(chat_id)
        return Report.check_if_group_did_not_get_code(group_letter, code)

class NotifyStartClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return State['notify'] == False

class NotifyEndClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return State['notify'] == True

class AddStartClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return State['add'] == (False, False)

class AddMidleClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return State['add'] == (True, False)

class AddEndClass(MessageFilter):
    def filter(self, message: Message) -> bool:
        return State['add'] == (True, True)

GroupRegisteredFilter = GroupRegisteredClass()
GroupIsAdminFilter = GroupIsAdminClass()
InfoKeySolvedFilter = InfoKeySolvedClass()

NotifyStartFilter = NotifyStartClass()
NotifyEndFilter = NotifyEndClass()

AddStartFilter = AddStartClass()
AddMidleFilter = AddMidleClass()
AddEndFilter = AddEndClass()