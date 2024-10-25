from db import DatabaseManager


class BusinessLogic:
    def __init__(self, db_manager):
        self.db_manager = db_manager
