from typing import List, Optional

from .traits import __Debug__, __Eq__


class Declaration(__Debug__, __Eq__):
    def __init__(self, name: str, dependencies: List[str]):
        self.name = name
        self.dependencies = dependencies


class PhysicalDeviceDeclaration(Declaration):
    def __init__(self, name: str):
        super().__init__(name, [])


class GptPartitionTableDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
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
        super().__init__(name, [partition_table])
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
        super().__init__(name, devices)
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
        super().__init__(name, [device])
        self.device = device
        self.type = type
        self.keysize = keysize
        self.password = password


class LvmPhysicalVolumeDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
        self.device = device


class LvmVolumeGroupDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        lvm_physical_volumes: List[str],
    ):
        super().__init__(name, lvm_physical_volumes)
        self.lvm_physical_volumes = lvm_physical_volumes


class LvmLogicalVolumeDeclaration(Declaration):
    def __init__(
        self,
        name: str,
        lvm_volume_group: str,
        size: str,
        args: List[str],
    ):
        super().__init__(name, [lvm_volume_group])
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
        super().__init__(name, [device, mountpoint])
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
        super().__init__(name, [filesystem])
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
        super().__init__(name, [filesystem])
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode
        self.size = size


class LoopDeviceDeclaration(Declaration):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(name, [file])
        self.file = file
        self.args = args


class SwapVolumeDeclaration(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
        self.device = device
