from ninja import Query, Router, responses

from server.apps.stantions.logic import functions as domain_functions
from server.apps.stantions.logic.request_schemas import (
    AcceptStantionTaskRequest,
    CreateStantionHeartBeatRequest,
    CreateStantionTaskResultRequest,
    PullStantionTaskRequest,
    RegisterStantionRequest,
    RetrieveNearestStantionsQueryParams,
)
from server.apps.stantions.logic.response_schemas import (
    RetrieveNearestStantionsResponse,
    StantionTaskInfo,
)

router = Router()


# Мне показалось использование RPC-like методов тут более уместно чем крудовая логика
@router.post("/pull-stantion-task", response=StantionTaskInfo, tags=["tasks"])
def pull_stantion_task(request, data: PullStantionTaskRequest) -> StantionTaskInfo:
    """
    Метод для получения задач станцией. Станция шлет запрос, а мы ей в ответ
    отдаем задачу, которую она должна выполнить.
    """
    return StantionTaskInfo.from_db_instance(domain_functions.pull_stantion_task(data))


@router.post("/accept-stantion-task", response=StantionTaskInfo, tags=["tasks"])
def accept_stantion_task(request, data: AcceptStantionTaskRequest):
    """
    Метод для принятия задачи станцией. Станция шлет запрос с id задачи, которую
    она приняла в работу, а мы меняем статус этой задачи на "принята". Если задача
    не найдена или уже была принята другой станцией, то возвращаем ошибку.
    """
    return StantionTaskInfo.from_db_instance(
        domain_functions.accept_stantion_task(data)
    )


@router.post("/create-stantion-task-result", response=StantionTaskInfo, tags=["tasks"])
def create_stantion_task_result(request, data: CreateStantionTaskResultRequest):
    """
    Метод для создания результата выполнения задачи станцией. Станция шлет запрос
    с id задачи, которую она выполнила, и результатом выполнения (успех или ошибка),
    а мы сохраняем этот результат в базе данных и меняем статус задачи на
    "выполнена". Если задача не найдена или не была принята этой станцией, то
    возвращаем ошибку.
    """
    return StantionTaskInfo.from_db_instance(
        domain_functions.complete_stantion_task(data)
    )


@router.post(
    "/create-stantion-heartbeat", response={204: None}, tags=["stantions-lifecycle"]
)
def create_stantion_heartbeat(request, data: CreateStantionHeartBeatRequest):
    """
    Метод для создания или обновления heartbeat от станции. Станция шлет запрос с
    информацией о себе (id, модель, местоположение) и состоянием своих слотов
    (какие батарейки сейчас в них находятся). На основе этого запроса мы создаем
    или обновляем запись о станции в базе данных, а также создаем запись о новом
    heartbeat от этой станции. Также на основе информации о слотах станции мы
    можем создавать задачи для этой станции (например, если мы видим, что в одном
    из слотов закончилась батарейка, то можем создать задачу на выдачу новой
    батарейки в этот слот).
    """
    domain_functions.create_stantion_hearbeat(data)
    return responses.Response(status=204, data=None)


@router.post("/register-stantion", response={204: None}, tags=["stantions-lifecycle"])
def register_stantion(request, data: RegisterStantionRequest):
    """
    Метод для регистрации новой станции. Станция шлет запрос с информацией о себе
    (id, модель, местоположение), а мы создаем запись о ней в базе данных. Если
    станция с таким id уже существует, то возвращаем ошибку.
    """
    domain_functions.register_stantion(data)
    return responses.Response(status=204, data=None)


@router.get("/stantions", response=RetrieveNearestStantionsResponse, tags=["stantions"])
def retrieve_stantions(
    request, filters: Query[RetrieveNearestStantionsQueryParams]
) -> RetrieveNearestStantionsResponse:
    """
    Метод для получения списка станций, отсортированных по удаленности от
    переданной точки. Станция шлет запрос с координатами точки, а мы возвращаем
    список станций, отсортированных по удаленности от этой точки. Также в ответе
    мы указываем количество свободных слотов и количество доступных батареек в
    каждой станции.
    """
    return domain_functions.get_nearest_stantions(filters.as_request())
