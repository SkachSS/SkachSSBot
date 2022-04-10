# -*- coding: utf-8 -*-
#
#  SkachSSBot - Database.
#  Created by Sergey Skachkov at 9/4/22
#
import logging
from typing import Literal, Optional, Dict

import aiosqlite


class Database:
    SQLS = [
        'CREATE TABLE IF NOT EXISTS "memes" ("uid" INTEGER PRIMARY KEY, "photo" BLOB, "uri" TEXT, "likes" INTEGER DEFAULT 0, "dislikes" INTEGER DEFAULT 0)',
        'CREATE TABLE IF NOT EXISTS "users_likes" ("meme_uid" INTEGER, "user_id" INTEGER, "like" INTEGER DEFAULT 0, "dislike" INTEGER DEFAULT 0)'
    ]

    def __init__(self, db_name: str = 'bot.db') -> None:
        self.db_name = db_name
        self.tables_initialized = False
        self.log = logging.getLogger('skachssbot')

    async def _create_tables(self) -> None:
        '''Создаёт таблицы и файл БД, если их нету.
        '''
        self.log.debug('Creating DB tables.')
        if not self.tables_initialized:
            async with aiosqlite.connect(self.db_name) as db:
                for sql in self.SQLS:
                    await db.execute(sql)
                await db.commit()
            self.tables_initialized = True

    async def add_photo(self, photo: Optional[bytes] = None, uri: Optional[str] = None) -> int:
        '''Добавляет мем в БД.

        Args:
            photo (Optional[bytes], optional): Байтовое представление файла. Defaults to None.
            uri (Optional[str], optional): VK URI фотографии. Defaults to None.

        Returns:
            int: UID мема.
        '''
        self.log.debug(f'Called with args ({len(photo) if photo else 0}, {uri})')
        async with aiosqlite.connect(self.db_name) as db:
            if photo:
                con = await db.execute('INSERT INTO "memes" (photo) VALUES (?)', (photo,))
                await db.commit()
            else:
                con = await db.execute('INSERT INTO "memes" (uri) VALUES (?)', (uri,))
                await db.commit()
            return con.lastrowid

    async def add_photo_like(self, uid: int) -> Literal[True]:
        '''Добавляет лайк мему.

        Args:
            uid (int): UID мема.

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE "memes" SET likes=likes+1 WHERE uid=?', (uid,))
            await db.commit()
        return True

    async def add_photo_dislike(self, uid: int) -> Literal[True]:
        '''Добавляет дизлайк мему.

        Args:
            uid (int): UID мема.

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE "memes" SET dislikes=dislikes+1 WHERE uid=?', (uid,))
            await db.commit()
        return True

    async def remove_photo_like(self, uid: int) -> Literal[True]:
        '''Убирает лайк с мема.

        Args:
            uid (int): UID мема.

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE "memes" SET like=like-1 WHERE uid=?', (uid,))
            await db.commit()
        return True

    async def remove_photo_dislike(self, uid: int) -> Literal[True]:
        '''Убирает дизлайк с мема.

        Args:
            uid (int): UID мема.

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE "memes" SET dislike=dislike-1 WHERE uid=?', (uid,))
            await db.commit()
        return True

    async def add_photo_uri(self, uid: int, uri: str) -> Literal[True]:
        '''Запоминаем URI мема загруженного в сообщество ВК. Побережём сервера ВК.

        Args:
            uid (int): UID мема.
            uri (str): URI мема типа "<type><owner_id>_<media_id>_<access_key>".

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid}, {uri})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE memes SET uri=? WHERE uid=?', (uri, uid))
            await db.commit()
        return True

    async def get_photo(self, uid: int) -> Optional[dict]:
        '''Возвращает мем из БД. Если есть.

        Args:
            uid (int): UID мема.

        Returns:
            Optional[dict]: Информация о меме.
        '''
        self.log.debug(f'Called with args ({uid})')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM memes WHERE uid=?', (uid,)) as cur:
                fetch = await cur.fetchone()
                if fetch:
                    return dict(fetch)
        return None

    async def add_user_action_for_photo(self, uid: int, user_id: int, is_like: bool) -> Literal[True]:
        '''Добавляет user_id в список лайков/дизлайков мемов.

        Args:
            uid (int): UID мема.
            user_id (int): VK user_id.
            is_like (bool): Пользователь поставил лайк?

        Returns:
            Literal[True]: Всегда True.
        '''
        self.log.debug(f'Called with args ({uid}, {user_id}, {is_like})')
        async with aiosqlite.connect(self.db_name) as db:
            attrs = (uid, user_id, int(is_like), int(not is_like))
            await db.execute('INSERT INTO users_likes VALUES (?,?,?,?)', attrs)
            await db.commit()
        return True

    async def is_user_like_photo(self, uid: int, user_id: int) -> bool:
        '''Пользователь лайкал/дизлайкал мем?

        Args:
            uid (int): UID мема.
            user_id (int): VK user_id.

        Returns:
            bool: Булевое значение.
        '''
        self.log.debug(f'Called with args ({uid}, {user_id})')
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users_likes WHERE meme_uid=? AND user_id=?', (uid, user_id)) as cur:
                fetch = await cur.fetchone()
                return bool(fetch)

    async def get_all_photo_uids(self) -> list:
        '''Возвращает UID'ы мемов из БД.

        Returns:
            list: Список UID мемов.
        '''
        self.log.debug('Called.')
        memes = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT uid FROM memes') as cur:
                async for row in cur:
                    memes.append(row[0])
        return memes

    async def get_private_stat(self, user_id: int) -> Dict[str, int]:
        '''Возвращает статистику лайков/дизлайков пользователя.

        Args:
            user_id (int): VK user_id.

        Returns:
            Dict[str, int]: Статистика вида {'likes': int, 'dislikes': int}
        '''
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT sum(like) as likes, sum(dislike) as dislikes FROM users_likes WHERE user_id=?', (user_id,)) as cur:
                fetch = await cur.fetchone()
                if fetch:
                    return dict(fetch)
        return {'likes': 0, 'dislikes': 0}

    async def get_public_stat(self) -> Dict[str, int]:
        '''Возвращает суммарное кол-во лайков/дизлайков.

        Returns:
            Dict[str, int]: Статистика вида {'likes': int, 'dislikes': int}
        '''
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT sum(like) as likes, sum(dislike) as dislikes FROM users_likes') as cur:
                fetch = await cur.fetchone()
                if fetch:
                    return dict(fetch)
        return {'likes': 0, 'dislikes': 0}

    async def get_top_9_memes(self) -> list:
        '''Возвращает топ 9 самых залайкненных мемов.

        Returns:
            list: Список мемов.
        '''
        memes = []
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM memes ORDER BY likes DESC LIMIT 9') as cur:
                async for row in cur:
                    memes.append(dict(row))
        return memes
