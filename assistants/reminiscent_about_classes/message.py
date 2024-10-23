from datetime import datetime
from dataclasses import dataclass


@dataclass
class Message:
    id: int # TODO Вынести в родителя
    row_number: int
    message_id: int
    create_moment: str # TODO Вынести в родителя
    update_moment: str # TODO Вынести в родителя

    def __post_init__(self):
        # TODO Вынести в родителя
        self.create_moment = datetime.strptime(self.create_moment, '%Y-%m-%d %H:%M:%S')
        self.update_moment = datetime.strptime(self.update_moment, '%Y-%m-%d %H:%M:%S')
