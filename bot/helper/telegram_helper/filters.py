#!/usr/bin/env python3
from pyrogram.filters import create

from bot import user_data, OWNER_ID,tgClient,LOGGER


class CustomFilters:

    async def owner_filter(self, client, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return uid == OWNER_ID

    owner = create(owner_filter)

    async def authorized_user(self, client:tgClient, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        chat_id = update.chat.id
        
        #added for auto delete files from gdrive and bot will send a message to itself
        from_bot = True if uid == 6082872684 or chat_id == 6082872684 else False

        for i in [-1001923653712,-1001964898247]:
            try:
                member = bool(await client.get_chat_member(i,uid))
                break
            except:
                member = False

        return bool(uid == OWNER_ID or 
                    (uid in user_data and (user_data[uid].get('is_auth', False) or
                    user_data[uid].get('is_sudo', False))) or 
                    (chat_id in user_data and user_data[chat_id].get('is_auth', False)) or 
                    bool(member) or 
                    from_bot)

    authorized = create(authorized_user)

    async def sudo_user(self, client, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return bool(uid == OWNER_ID or uid in user_data and user_data[uid].get('is_sudo'))

    sudo = create(sudo_user)

