class __Debug__:
    def __str__(self):
        fields = ""
        for key, value in self.__dict__.items():
            if fields:
                fields += ", "
            fields += f"{key}={str(value)}"
        return f"{self.__class__.__name__}({fields})"

    def __repr__(self):
        return self.__str__()


class __Eq__:
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__
