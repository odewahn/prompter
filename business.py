from db import DatabaseManager


class BusinessLogic:
    def __init__(self, db_manager):
        self.db_manager = db_manager
import os
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT

class BusinessLogic:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def load_files(self, files, tag):
        block_group_id = await self.db_manager.create_block_group(tag)
        for file in files:
            if file.endswith(".epub"):
                await self._load_epub(file, block_group_id)
            else:
                await self._load_text_file(file, block_group_id)

    async def _load_epub(self, file, block_group_id):
        book = epub.read_epub(file, {"ignore_ncx": True})
        for item in book.get_items():
            if item.get_type() == ebooklib_ITEM_DOCUMENT:
                content = item.get_content().decode("utf-8")
                await self.db_manager.add_block(block_group_id, content, item.get_name())

    async def _load_text_file(self, file, block_group_id):
        with open(file, "r") as f:
            content = f.read()
            await self.db_manager.add_block(block_group_id, content, os.path.basename(file))
