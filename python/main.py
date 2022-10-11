from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, ChatMemberHandler

from settings import BotToken
from log import Log

from handlers import ChatJoinHandler
from handlers import HelpHandler
from handlers import ReportHandler
from handlers import InfoHandler

from handlers import CancelHandler

from handlers import NotifyStartHandler
from handlers import NotifyEndHandler

from handlers import AddStartHandler
from handlers import AddMidleHandler
from handlers import AddEndHandler

from filters import GroupRegisteredFilter
from filters import GroupIsAdminFilter
from filters import InfoKeySolvedFilter

from filters import NotifyStartFilter
from filters import NotifyEndFilter

from filters import AddStartFilter
from filters import AddMidleFilter
from filters import AddEndFilter

from help import Help
from groups import Groups
from info import Info
from report import Report

async def post_init(application: Application) -> None:
    application.create_task(Help.update())
    application.create_task(Groups.update())
    application.create_task(Info.update())
    application.create_task(Report.update())

if __name__ == '__main__':
    Log.info("Starting...")
    app = ApplicationBuilder().token(BotToken).post_init(post_init).build()

    app.add_handler(ChatMemberHandler(ChatJoinHandler))
    
    app.add_handler(CommandHandler("help", HelpHandler, filters = GroupRegisteredFilter))
    app.add_handler(MessageHandler(GroupRegisteredFilter & InfoKeySolvedFilter, InfoHandler))

    app.add_handler(CommandHandler("cancel", CancelHandler, filters = GroupRegisteredFilter & GroupIsAdminFilter))

    app.add_handler(CommandHandler("notify", NotifyStartHandler, filters = NotifyStartFilter & GroupRegisteredFilter & GroupIsAdminFilter))
    app.add_handler(MessageHandler(NotifyEndFilter & GroupRegisteredFilter & GroupIsAdminFilter, NotifyEndHandler))

    app.add_handler(CommandHandler("add", AddStartHandler, filters = AddStartFilter & GroupRegisteredFilter & GroupIsAdminFilter))
    app.add_handler(MessageHandler(AddMidleFilter & GroupRegisteredFilter & GroupIsAdminFilter, AddMidleHandler))
    app.add_handler(MessageHandler(AddEndFilter & GroupRegisteredFilter & GroupIsAdminFilter, AddEndHandler))
    
    for report_command in Groups.get_all_report_commands():
        app.add_handler(CommandHandler(report_command, ReportHandler, filters = GroupRegisteredFilter & GroupIsAdminFilter))

    app.run_polling()
    Log.info("Done. Goodby!")