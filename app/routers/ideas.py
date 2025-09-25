from fastapi import APIRouter, HTTPException

from ..models import Idea, IdeaCreate
from ..services.store import store


router = APIRouter(prefix="/ideas")


@router.post("", response_model=Idea)
def create_idea(payload: IdeaCreate) -> Idea:
    return store.create(payload)


@router.get("", response_model=list[Idea])
def list_ideas() -> list[Idea]:
    return store.list()


@router.get("/{idea_id}", response_model=Idea)
def get_idea(idea_id: str) -> Idea:
    idea = store.get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

