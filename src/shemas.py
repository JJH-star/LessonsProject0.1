from pydantic import BaseModel
# Pydantic: создаем модель для запроса задания
class TaskCreate(BaseModel):
    class_num: int
    title: str
    original_text: bytes
    answer: str
    topic_id: int

class TopicCreate(BaseModel):
    class_num: int
    name: str
    description: bytes