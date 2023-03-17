import datetime
from pyrogram.types import Message 

from bot import DOWNLOAD_DIR, tgClient
from bot.helper.ext_utils.bot_utils import is_url
from bot.helper.listener import MirrorLeechListener
from bot.helper.mirror_utils.download_utils.aria2_download import \
    add_aria2c_download
from bot.helper.mirror_utils.download_utils.telegram_downloader import \
    TelegramDownloadHelper
from bot.helper.telegram_helper.message_utils import sendMessage


class Multi_Tasks_Manager():
    def __init__(self,Client,chat_id:int|str,start_message:Message,
                 isZip=False,extract=False,isLeech=False,pswd=None,
                 authen="") -> None:
        self.auth = authen
        self.client : tgClient
        self.client = Client
        self.start_id = start_message.id
        self.start = start_message
        self.chat_id = chat_id
        self.urls = []
        self.medias = []
        self.time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.user_id = self.start.from_user.id

        ######################

        self.listener : MirrorLeechListener

        self.Completed = False

        self.isZip = isZip
        self.extract = extract
        self.pswd = pswd
        self.isLeech = isLeech

        if username := self.end.from_user.username:
            self.tag = f"@{username}"
        else:
            self.tag = self.end.from_user.mention

    def set_end_message(self,message:Message):
        self.end = message
        self.end_id = self.end.id

    def create_listener(self):
        self.listener = MirrorLeechListener(self.end,self.isZip,self.extract,False,
                                            self.isLeech,self.pswd,self.tag,False,
                                            False,directory=f"{DOWNLOAD_DIR}{self.user_id}.MultiTask.{self.time}")

    async def get_messages(self):
        all_messages  = await self.client.get_messages(self.chat_id, list(range(self.start_id + 1,self.end_id)))

        for message in all_messages:
            message : Message
            media = message.document or message.photo or message.video or message.audio or \
                 message.voice or message.video_note or message.sticker or message.animation or None
            
            if media is None:
                #Text - URLs
                splitted_text = message.text.split('\n')
                for text in splitted_text:
                    if is_url(text):
                        self.urls.append(text)
            else:
                #Medias
                self.medias.append(message)
        
    def check_not_empty(self):
        if (not self.urls) and (not self.medias):
            return False
        return True
    
    def check_completed(self):
        return self.Completed
    
    async def downloader_urls(self):
        if self.urls:
            await add_aria2c_download(self.urls[0], self.listener.dir, self.listener, None,self.auth,None,None)
            del self.urls[0]

    async def downloader_medias(self):
        if self.medias:
            await self.TelegramDownloadHelper.add_download(self.medias[0], f'{self.listener.dir}/', "")
            del self.medias[0]
    
    async def downloader(self):
        if self.urls:
            await self.downloader_urls()
            return
        if self.medias:
            await self.downloader_medias()
            return
        
        #send to listener that download completed
        self.Completed = True
        await self.listener.onDownloadComplete()
            

    async def run(self):
        self.create_listener()
        await self.get_messages()
        if self.check_not_empty():
            if self.medias:
                self.TelegramDownloadHelper = TelegramDownloadHelper(self.listener)
            await self.downloader()
        else:
            await sendMessage(self.end,"<b>No URL Or Media Provided!</b>\nDone!")
