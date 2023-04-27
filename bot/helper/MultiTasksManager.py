import datetime
from pyrogram.types import Message 
from asyncio import sleep , Lock,run as async_run

from bot import DOWNLOAD_DIR, tgClient ,LOGGER
from bot.helper.ext_utils.bot_utils import async_to_sync, is_url
from bot.helper.listener import MirrorLeechListener
from bot.helper.mirror_utils.download_utils.aria2_download import \
    add_aria2c_download
from bot.helper.mirror_utils.download_utils.telegram_downloader import \
    TelegramDownloadHelper
from bot.helper.telegram_helper.message_utils import sendMessage

urls_lock = Lock()
medias_lock = Lock()


class Multi_Tasks_Manager():
    def __init__(self,Client,chat_id:int|str,start_message:Message,
                 isZip=False,extract=False,isLeech=False,pswd=None,
                 authen="") -> None:
        self.auth = authen
        self.client : tgClient
        self.client = Client
        self.start_id = start_message.id + 1 
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
        self.send_listening_message()

    def send_listening_message(self):
        text = "<b>Waiting For Your Tasks!</b>"
        if self.isZip:
            text += "\n\nZIP Files : ✅"
        if self.pswd:
            text += f"\nPassword For ZIP File : {self.pswd}"
        if self.isLeech :
            text += f"\nLeech Files : ✅"
        async_to_sync(sendMessage,(self.start,text))

    def status_str(self):
        return f"\nRemaining Tasks {len(self.medias)+len(self.urls)}/{self.total_tasks}"

    def set_end_message(self,message:Message):
        self.end = message
        self.end_id = self.end.id
        if username := self.end.from_user.username:
            self.tag = f"@{username}"
        else:
            self.tag = self.end.from_user.mention


    def create_listener(self):
        self.listener = MirrorLeechListener(self.end,self.isZip,self.extract,False,
                                            self.isLeech,self.pswd,self.tag,False,
                                            False,{},
                                            f"{DOWNLOAD_DIR}{self.user_id}.MultiTask.{self.time}",
                                            self,self.time)

    async def get_messages(self):
        list_ = list(range(self.start_id + 1,self.end_id))
        while len(list_) > 190:
            await self._get_messages(list_[:190])
            del list_[:190]
        if len(list_) >= 1:
            await self._get_messages(list_)
        
    async def _get_messages(self,list_of_message_ids):
        all_messages  = await self.client.get_messages(self.chat_id,list_of_message_ids)

        for message in all_messages:
            message : Message
            media = message.document or message.photo or message.video or message.audio or \
                 message.voice or message.video_note or message.sticker or message.animation or None
            
            if media is None:
                if message is not None:
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
            async with urls_lock:
                url = self.urls[0]
                del self.urls[0]
            await add_aria2c_download(url, self.listener.dir, self.listener, None,self.auth,None,None)

    async def downloader_medias(self):
        if self.medias:
            async with medias_lock:
                media = self.medias[0]
                del self.medias[0]
            await self.TelegramDownloadHelper.add_download(media, f'{self.listener.dir}/', "",multi=True)
    
    async def downloader(self):
        await sleep(1)
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
        self.total_tasks = len(self.medias) + len(self.urls)
        if self.check_not_empty():
            await sendMessage(self.end,"<b>Started To Do Your Tasks One by One!</b>\nA 1s delay Between your tasks will showen")
            if self.medias:
                self.TelegramDownloadHelper = TelegramDownloadHelper(self.listener)
            await self.downloader()
        else:
            await sendMessage(self.end,"<b>No URL Or Media Provided!</b>\nDone!")
