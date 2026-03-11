from ninja import Schema


class PaginatedResponse[T](Schema):
    count: int
    results: list[T]
