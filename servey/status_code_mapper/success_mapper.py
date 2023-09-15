from servey.status_code_mapper.status_code_mapper_abc import StatusCodeMapperABC, T


class SuccessMapper(StatusCodeMapperABC[T]):
    @property
    def status_code(self) -> int:
        pass

    def match(self, result: T) -> bool:
        return True

    def description(self) -> str:
        pass
