from datetime import datetime
from dataclasses import dataclass


@dataclass
class Word:
    id: int
    word: str
    abbreviation: str
    translation: str
    total_answers: int
    correct_answers: int
    part_of_speech: str
    create_moment: str
    update_moment: str

    def __post_init__(self):
        # TOOD Вынест в родителя
        self.create_moment = datetime.strptime(self.create_moment, '%Y-%m-%d %H:%M:%S')
        self.update_moment = datetime.strptime(self.update_moment, '%Y-%m-%d %H:%M:%S')