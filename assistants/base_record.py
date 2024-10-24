from datetime import datetime
from dataclasses import dataclass

@dataclass
class BaseRecord:
    id: int
    create_moment: str
    update_moment: str
    is_actual: bool

    def __post_init__(self):
        self.create_moment = datetime.strptime(self.create_moment, '%Y-%m-%d %H:%M:%S')
        self.update_moment = datetime.strptime(self.update_moment, '%Y-%m-%d %H:%M:%S')