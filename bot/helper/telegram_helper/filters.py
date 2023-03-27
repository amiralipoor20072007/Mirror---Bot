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
        try:
            member = bool(await client.get_chat_member(-1001923653712,uid))
        except:
            member = False
        LOGGER.info(f"{uid} : {member}")
        return bool(uid == OWNER_ID or (uid in user_data and (user_data[uid].get('is_auth', False) or
              user_data[uid].get('is_sudo', False))) or (chat_id in user_data and user_data[chat_id].get('is_auth', False)) or 
              bool(member))

    authorized = create(authorized_user)

    async def sudo_user(self, client, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return bool(uid == OWNER_ID or uid in user_data and user_data[uid].get('is_sudo'))

    sudo = create(sudo_user)

