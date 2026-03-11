from ninja import Router

from server.apps.stantions.logic import functions as domain_functions
from server.apps.stantions.logic.request_schemas import (
    AcceptStantionTaskRequest,
    CreateStantionHeartBeatRequest,
    PullStantionTaskRequest,
)
from server.apps.stantions.logic.response_schemas import StantionTaskInfo

router = Router()


@router.post("/pull-stantion-task", response=StantionTaskInfo)
def pull_stantion_task(request, data: PullStantionTaskRequest) -> StantionTaskInfo:
    """
    Метод для получения задач станцией. Станция шлет запрос, а мы ей в ответ отдаем задачу, которую она должна выполнить (например, выдать батарейку на определенный слот). Пока что просто заглушка, которая всегда отдает одну и ту же задачу. В реальной жизни тут бы была логика по выбору задачи для конкретной станции из очереди задач.
    """
    return StantionTaskInfo.from_db_instance(domain_functions.pull_stantion_task(data))


@router.post("/accept-stantion-task", response=StantionTaskInfo)
def accept_stantion_task(request, data: AcceptStantionTaskRequest):
    """
    Метод для принятия задачи станцией. Станция шлет запрос с id задачи, которую она приняла в работу, а мы меняем статус этой задачи на "принята". Если задача не найдена или уже была принята другой станцией, то возвращаем ошибку.
    """
    return StantionTaskInfo.from_db_instance(
        domain_functions.accept_stantion_task(data)
    )


@router.post("/create-stantion-heartbeat")
def create_stantion_heartbeat(request, data: CreateStantionHeartBeatRequest):
    """
    Метод для создания или обновления heartbeat от станции. Станция шлет запрос с информацией о себе (id, модель, местоположение) и состоянием своих слотов (какие батарейки сейчас в них находятся). На основе этого запроса мы создаем или обновляем запись о станции в базе данных, а также создаем запись о новом heartbeat от этой станции. Также на основе информации о слотах станции мы можем создавать задачи для этой станции (например, если мы видим, что в одном из слотов закончилась батарейка, то можем создать задачу на выдачу новой батарейки в этот слот).
    """
    domain_functions.create_stantion_hearbeat(data)
