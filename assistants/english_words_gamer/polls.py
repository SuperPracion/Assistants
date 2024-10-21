from datetime import datetime
from dataclasses import dataclass

@dataclass
class Poll:
    id: int
    word_id: int
    correct_option_id: int
    chat_id: int
    poll_id: int
    create_moment: str
    update_moment: str

    def __post_init__(self):
        # TODO Вынести в родителя
        self.create_moment = datetime.strptime(self.create_moment, '%Y-%m-%d %H:%M:%S')
        self.update_moment = datetime.strptime(self.update_moment, '%Y-%m-%d %H:%M:%S')