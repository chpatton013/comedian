from typing import List, Optional


class Declaration:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        fields = ""
        for key, value in self.__dict__.items():
            if fields:
                fields += ", "
            fields += f"{key}={str(value)}"
        return f"{self.__class__.__name__}({fields})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.__dict__.values())


class PhysicalDeviceDeclaration(Declaration):
    def __init__(self, name: str):
        super().__init__(name)


class GptPartitionTableDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name)
        self.device = device


class GptPartitionDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        partition_table: str,
        number: int,
        start: str,
        end: str,
        flags: List[str],
    ):
        super().__init__(name)
        self.partition_table = partition_table
        self.number = number
        self.start = start
        self.end = end
        self.flags = flags


class RaidVolumeDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        devices: List[str],
        level: str,
        metadata: str,
    ):
        super().__init__(name)
        self.devices = devices
        self.level = level
        self.metadata = metadata


class CryptVolumeDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        device: str,
        type: str,
        keysize: Optional[str],
        password: Optional[str],
    ):
        super().__init__(name)
        self.device = device
        self.type = type
        self.keysize = keysize
        self.password = password


class LvmPhysicalVolumeDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name)
        self.device = device


class LvmVolumeGroupDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        lvm_physical_volumes: List[str],
    ):
        super().__init__(name)
        self.lvm_physical_volumes = lvm_physical_volumes


class LvmLogicalVolumeDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        lvm_volume_group: str,
        size: str,
        args: List[str],
    ):
        super().__init__(name)
        self.lvm_volume_group = lvm_volume_group
        self.size = size
        self.args = args


class FilesystemDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        device: str,
        mountpoint: str,
        type: str,
        options: List[str],
    ):
        super().__init__(name)
        self.device = device
        self.mountpoint = mountpoint
        self.type = type
        self.options = options


class DirectoryDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
    ):
        super().__init__(name)
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode


class FileDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
        size: Optional[str],
    ):
        super().__init__(name)
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode
        self.size = size


class LoopDeviceDeclaration(Declaration):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(name)
        self.file = file
        self.args = args


class SwapVolumeDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name)
        self.device = device
