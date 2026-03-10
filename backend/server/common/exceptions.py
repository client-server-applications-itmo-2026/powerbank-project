class DomainError(Exception):

    def __init__(self, msg: str, **context) -> None:
        super().__init__(msg)
        self.context = context

    def get_details(self) -> dict[str, Any] | None:
        return None
