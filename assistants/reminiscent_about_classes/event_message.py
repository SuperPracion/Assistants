from dataclasses import dataclass
from assistants.base_record import BaseRecord

@dataclass
class EventMessage(BaseRecord):
    row_number: int
    message_id: int