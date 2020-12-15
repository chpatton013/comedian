from typing import Any, Iterator


class FieldsMixin:
    def __fields__(self) -> Iterator[str]:
        yield from self.__dict__.keys()


class DebugMixin(FieldsMixin):
    def __str__(self):
        fields_str = ""
        for field in self.__fields__():
            value = self.__dict__[field]
            if fields_str:
                fields_str += ", "
            fields_str += f"{field}={str(value)}"
        return f"{self.__class__.__name__}({fields_str})"

    def __repr__(self):
        return self.__str__()


class EqMixin(FieldsMixin):
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return all(
            self.__dict__[field] == other.__dict__[field] for field in self.__fields__()
        )
