from typing import Iterator


class __Debug__:
    def __str__(self):
        fields_str = ""
        for field in self.debug_fields():
            value = self.__dict__[field]
            if fields_str:
                fields_str += ", "
            fields_str += f"{field}={str(value)}"
        return f"{self.__class__.__name__}({fields_str})"

    def __repr__(self):
        return self.__str__()

    def debug_fields(self) -> Iterator[str]:
        yield from self.__dict__.keys()


class __Eq__:
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return all(
            self.__dict__[field] == other.__dict__[field]
            for field in self.eq_fields()
        )

    def eq_fields(self) -> Iterator[str]:
        yield from self.__dict__.keys()
