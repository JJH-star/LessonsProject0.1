from fastapi import FastAPI, Request, UploadFile, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session

from src.models.models import Task, Topic

from src.shemas import TaskCreate, TopicCreate

app = FastAPI(
    title="Message_App"
)

templates = Jinja2Templates(directory="src/templates")


@app.get("/")
def hello(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/classes")
def show_tasks(request: Request):
    # Здесь можно добавить логику для получения списка заданий или других дополнительных данных
    return templates.TemplateResponse("classes.html", {"request": request})

# FastAPI: добавляем ручку для создания задания

@app.post("/create_task/")
async def create_task(task: TaskCreate, b: AsyncSession = Depends(get_async_session)):
    try:
        db_task = Task(**task.dict())
        b.add(db_task)
        await b.commit()
        await b.refresh(db_task)
        return {"message": "Task created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await b.close()


@app.post("/topics/")
async def create_topic(topic: TopicCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        new_topic = Topic(**topic.dict())
        session.add(new_topic)
        await session.commit()
        await session.refresh(new_topic)
        return new_topic
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await session.close()

@app.get("/classes/{class_num}")
async def get_topics_for_class(request: Request, class_num: int, session: AsyncSession = Depends(get_async_session)):
    try:
        # Получаем список тем для определенного класса
        topics = await session.execute(select(Topic).filter(Topic.class_num == class_num))
        topics_list = topics.scalars().all()
        return templates.TemplateResponse("topic_class.html", {"request": request, "class_num": class_num, "topics": topics_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await session.close()

@app.get("/classes/{class_num}/{topic_id}")
async def show_tasks(request: Request, class_num: int, topic_id: int, b: AsyncSession = Depends(get_async_session)):
    try:
        tasks = await b.execute(select(Task).filter(Task.topic_id == topic_id, Task.class_num == class_num))
        result = tasks.scalars().all()
        if not result:
            raise HTTPException(status_code=404, detail="Tasks not found")
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await b.close()

@app.get("/classes/{class_num}/{topic_id}/{task_id}")
async def show_task_detail(request: Request, class_num: int, topic_id: int, b: AsyncSession = Depends(get_async_session)):
    try:
        tasks = await b.execute(select(Task).filter(Task.topic_id == topic_id, Task.class_num == class_num))
        result = tasks.scalars().all()
        print(result)
        if not result:
            raise HTTPException(status_code=404, detail="Tasks not found")
        return templates.TemplateResponse("task_detail.html", {"request": request, "task": result[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await b.close()

@app.post("/classes/{class_num}/{topic_id}/{task_id}")
async def check_answer(request: Request, task_id: int, answer: str = Form(...), b: AsyncSession = Depends(get_async_session)):
    try:
        # Получить задание из базы данных по task_id
        task = await b.execute(select(Task).filter(Task.id == task_id))
        result = task.scalars().first()
        print(answer)
        is_correct = False
        # Проверить, что задание существует
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")

        if not answer:
            response_text = "Введите ответ!"
        else:
            # Проверить ответ пользователя
            if answer == result.answer:
                response_text = "Правильный ответ!"
                is_correct = True
            else:
                response_text = "Неправильный ответ. Попробуйте еще раз."
                is_correct = False

        # Вернуть шаблон task_detail.html с результатом проверки
        return templates.TemplateResponse("task_detail.html", {"request": request, "task": result, "response_text": response_text, "is_correct": is_correct})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await b.close()