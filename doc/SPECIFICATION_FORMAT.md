# Specification Format

The specification JSON file informs `comedian` of the way to identify and
prepare your media. Several different types of specifications can be described
in this file - each with their own set of named fields. Each type of
specification has its own collection of required and optional fields; no other
fields are allowed.

## Introduction

At the top-level, the JSON object contains several lists of specifications:
`physical_devices`, `raid_volumes`, and `lvm_volume_groups`. These lists are
populated with several specifications of the associated types: `PhysicalDevice`,
`RaidVolume`, and `LvmVolumeGroup`, respectively.

### Composition

Several specification types can contain one or more other specifications in
their named fields:
* `File` can contain a `LoopDevice` or a `SwapVolume`
* `Filesystem` can contain several `Directory`s and `File`s
* `GptPartitionTable` can contain several `GptPartition`s
* `LvmVolumeGroup` can contain several `LvmLogicalVolume`s
* Any block device can contain anything that can be put on a block device

### Block Devices

The following specification types are considered to be block devices:
* `CryptVolume`
* `GptPartition`
* `LoopDevice`
* `LvmLogicalVolume`
* `PhysicalDevice`
* `RaidVolume`

The following specification types can be put on a block device:
* `CryptVolume`
* `Filesystem`
* `GptPartitionTable`
* `LvmPhysicalVolume`
* `SwapVolume`

## Names and References

Every specification has a unique name within the JSON file. Some of these names
must be provided explicitly, but others are calculated by `comedian`. For
example, if a `GptPartitionTable` is put on a device named `sda`, then that
partition table is given the name `sda:gpt`. And every partition within that
table is given a name such as `sda:gpt:1`, `sda:gpt:2`, etc.

Some specifications have fields which reference other specifications. They do
this by citing the name of the referred-to specification. For example,
`RaidVolume`s span multiple devices, and must enumerate those names under their
`devices` field.

The names used in any references must exist after the entire specification JSON
has been parsed - it is okay to refer to a specification that is defined later,
as long as there is no cycle in the graph of references ("A" cannot refer to "B"
if "B" also refers to "A", etc).

## Example

```json
{
  "physical_devices": [
    {
      "name": "sda",
      "gpt_partition_table": {
        "gpt_partitions": [
          {
            "type": "primary",
            "start": "1MB",
            "end": "3MB",
            "label": "bios"
          },
          {
            "type": "primary",
            "start": "3MB",
            "end": "-1",
            "label": "root",
            "filesystem": {
              "name": "fsroot",
              "mountpoint": "/",
              "type": "ext4"
            }
          }
        ]
      }
    }
  ]
}
```

## Grammar

We can describe the layout of specification JSON object according to a grammar
with the following syntax:
* Quoted strings are the names of object keys
* `str` is the token representing the input of type string
* Any unquoted string is a token representing a type
* An asterisk (`*`) after a type indicates that the rule is repeated 0 or more
  times
* A plus (`+`) after a type indicates that the rule is repeated 1 or more times
* A carrot (`^`) after a type indicates that the rule is mutually-exclusive with
  all other carrots
* A question-mark (`?`) after a type indicates that the rule is optional

The grammar begins parsing at `Root`.

### Root

```
"physical_devices": PhysicalDevice +
"raid_volumes": RaidVolume *
"lvm_volume_groups": LvmVolumeGroup *
```

### CryptVolume

```
"name": str
"type": str
"keysize": str
"keyfile": str
"password": str ?
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`

### Directory

```
"name": str
"relative_path": str
"owner": str ?
"group": str ?
"mode": str ?
```

#### Implicit Fields

Inherits `name` and `filesystem` properties from its parent `Filesystem`.

* `filesystem`: `{parent}`
* `name`: `{filesystem}:{relative_path}`

### File

```
"name": str
"relative_path": str
"owner": str ?
"group": str ?
"mode": str ?
"size": str ?
"loop_device": LoopDevice ^ ?
"swap_volume": SwapVolume ^ ?
```

#### Implicit Fields

Inherits `name` and `filesystem` properties from its parent `Filesystem`.

* `filesystem`: `{parent}`
* `name`: `{filesystem}:{relative_path}`

### Filesystem

```
"name": str
"mountpoint": str
"type": str
"options": str *
"directories": Directory *
"files": File *
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`

### GptPartition

```
"type": str
"start": str
"end": str,
"flags": str *
"label": str ?
"unit": str ?
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `partition_table`, `number`, and `name` properties from its parent
`GptPartitionTable`.

* `partition_table`: `{parent}`
* `number`: The index of this partition within the list of partitions in the
  parent `GptPartitiontTable`; 1-indexed.
* `name`: `{partition_table}:{number}`

### GptPartitionTable

```
"glue": str ?
"gpt_partitions": GptPartition +
```

#### Implicit Fields

Inherits `name` and `device` properties from its parent specification.

* `device`: `{parent}`
* `name`: `{device}:gpt`

### LoopDevice

```
"name": str
"args": str *
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `file` properties from its parent `File`.

* `file`: `{parent}`

### LvmLogicalVolume

```
"name": str
"size": str
"args": str *
"lvm_physical_volumes": str *
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `lvm_volume_group` property from its parent `LvmVolumeGroup`.

* `lvm_volume_group`: `{parent}`

### LvmPhysicalVolume

```
"name": str
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`

### LvmVolumeGroup

```
"name": str
"lvm_physical_volumes": str +
"lvm_logical_volumes": LvmLogicalVolume +
```

### PhysicalDevice

```
"name": str
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

### RaidVolume

```
"name": str
"devices": str +
"level": str
"metadata": str
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"gpt_partition_table": GptPartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

### SwapVolume

```
"name": str
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`