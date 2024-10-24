from dataclasses import dataclass
from assistants.base_record import BaseRecord

@dataclass
class Poll(BaseRecord):
    word_id: int
    correct_option_id: int
    chat_id: int
    poll_id: int