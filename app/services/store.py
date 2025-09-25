import threading
import uuid
from typing import Dict, List

from ..models import Idea, IdeaCreate


class InMemoryIdeaStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._ideas: Dict[str, Idea] = {}

    def create(self, payload: IdeaCreate) -> Idea:
        with self._lock:
            idea_id = str(uuid.uuid4())
            idea = Idea(id=idea_id, **payload.model_dump())
            self._ideas[idea_id] = idea
            return idea

    def list(self) -> List[Idea]:
        with self._lock:
            return list(self._ideas.values())

    def get(self, idea_id: str) -> Idea | None:
        with self._lock:
            return self._ideas.get(idea_id)


store = InMemoryIdeaStore()

