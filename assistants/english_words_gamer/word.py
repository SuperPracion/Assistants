from dataclasses import dataclass
from assistants.base_record import BaseRecord

@dataclass
class Word(BaseRecord):
    word: str
    abbreviation: str
    translation: str
    total_answers: int
    correct_answers: int
    part_of_speech: str