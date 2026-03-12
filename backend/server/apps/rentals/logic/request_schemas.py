from ninja import Schema


class StartRentalRequest(Schema):
    stantion_id: str
    tariff_id: int


class CompleteRentalRequest(Schema):
    rental_id: int
    stantion_id: str
