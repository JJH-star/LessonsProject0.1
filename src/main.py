from fastapi import FastAPI, Request, UploadFile, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session

from src.models.models import Task
from src.filters import form_data
from src.shemas import TaskCreate

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


# FastAPI: добавляем ручку для отображения заданий по классам
@app.get("/classes/{class_num}")
async def show_tasks_for_class(request: Request, class_num: int, session: AsyncSession = Depends(get_async_session)):
    tasks = await session.execute(select(Task).filter(Task.class_num == class_num))
    return templates.TemplateResponse("task_class.html", {"request": request, "class_num": class_num, "tasks": tasks.scalars().all()})


@app.get("/classes/{class_num}/{task_id}")
async def show_task_detail(request: Request, class_num: int, task_id: int, b: AsyncSession = Depends(get_async_session)):
    try:
        task = await b.execute(select(Task).filter(Task.id == task_id, Task.class_num == class_num))
        result = task.scalars().all()
        # print(task.first())
        # print(result.first())
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return templates.TemplateResponse("task_detail.html", {"request": request, "task": result[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await b.close()
