# Specification Format

The specification JSON file informs `comedian` of the way to identify and
prepare your media. Several different types of specifications can be described
in this file - each with their own set of named fields. Each type of
specification has its own collection of required and optional fields; no other
fields are allowed.

## Defining Specifications

At the top-level, the JSON object contains several lists of specifications. The
`physical_devices` specification list is required, and all others are optional.
The order of specification lists does not matter, as the graph will be resolved
in dependency order.

### Composition

Several specification types can contain one or more other specifications in
their named fields:
* `File` can contain a `LoopDevice`, `CryptVolume`, or a `SwapVolume`
* `Filesystem` can contain several `Directory`s and `File`s
* `PartitionTable` can contain several `Partition`s
* `LvmVolumeGroup` can contain several `LvmLogicalVolume`s
* Any block device can contain anything that can be put on a block device

### Block Devices

The following specification types are considered to be block devices:
* `CryptVolume`
* `Partition`
* `LoopDevice`
* `LvmLogicalVolume`
* `PhysicalDevice`
* `RaidVolume`

The following specification types can be put on a block device:
* `CryptVolume`
* `Filesystem`
* `PartitionTable`
* `LvmPhysicalVolume`
* `SwapVolume`

## Names and References

Every specification has a unique name within the JSON file. Some of these names
must be provided explicitly, but others are calculated by `comedian`. For
example, if a `PartitionTable` is put on a device named `sda`, then that
partition table is given the name `sda:pt`. And every partition within that
table is given a name such as `sda:pt:1`, `sda:pt:2`, etc.

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
      "partition_table": {
        "type": "gpt",
        "partitions": [
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
* An ampersand (`&`) after a type indicates that the rule is mutually-inclusive
  with all other ampersands
* A question-mark (`?`) after a type indicates that the rule is optional

The grammar begins parsing at `Root`.

### Root

```
"physical_devices": PhysicalDevice +
"crypt_volumes": CryptVolume *
"directories": Directory *
"files": File *
"filesystems": Filesystem *
"links": Link *
"loop_devices": LoopDevice *
"lvm_logical_volumes": LvmLogicalVolume *
"lvm_physical_volumes": LvmPhysicalVolume *
"lvm_volume_groups": LvmVolumeGroup *
"mounts": Mount *
"partition_tables": PartitionTable *
"raid_volumes": RaidVolume *
"swap_volumes": SwapVolume *
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
"partition_table": PartitionTable ^
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
"crypt_volume": CryptVolume ^ ?
"swap_volume": SwapVolume ^ ?
```

#### Implicit Fields

Inherits `name` and `filesystem` properties from its parent `Filesystem`.

* `filesystem`: `{parent}`
* `name`: `{filesystem}:{relative_path}`

### Filesystem

```
"name": str
"type": str
"options": str *
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`

### Mount

```
"name": str
"mountpoint": str
"options": str *
"dump_frequency": int ?
"fsck_order": int ?
"directories": Directory *
"files": File *
"links": Link *
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`

### Link

```
"name": str
"relative_path": str
"owner": str ?
"group": str ?
"mode": str ?
"symbolic": bool ?
```

#### Implicit Fields

Inherits `name` and `filesystem` properties from its parent `Filesystem`.

* `filesystem`: `{parent}`
* `name`: `{filesystem}:{relative_path}`

### LoopDevice

```
"name": str
"args": str *
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"partition_table": PartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `file` properties from its parent `File`.

* `file`: `{parent}`

### LvmLogicalVolume

```
"name": str
"size": str ^1
"extents": str ^1
"type": str ?
"args": str *
"lvm_volume_group": str,
"lvm_physical_volumes": str *
"lvm_poolmetadata_volume": str ^2 ?
"lvm_cachepool_volume": str ^2 ?
"lvm_thinpool_volume": str ^2 ?
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"partition_table": PartitionTable ^
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

### Partition

```
"align": str ?
"type": str
"start": str
"end": str,
"flags": str *
"label": str ?
"unit": str ?
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"partition_table": PartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

#### Implicit Fields

Inherits `partition_table`, `number`, and `name` properties from its parent
`PartitionTable`.

* `partition_table`: `{parent}`
* `number`: The index of this partition within the list of partitions in the
  parent `PartitiontTable`; 1-indexed.
* `name`: `{partition_table}:{number}`

### PartitionTable

```
"type": str
"glue": str ?
"partitions": Partition +
```

#### Implicit Fields

Inherits `name` and `device` properties from its parent specification.

* `device`: `{parent}`
* `name`: `{device}:pt`

### PhysicalDevice

```
"name": str
"crypt_volume": CryptVolume ^
"filesystem": Filesystem ^
"partition_table": PartitionTable ^
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
"partition_table": PartitionTable ^
"lvm_physical_volume": LvmPhysicalVolume ^
"swap_volume": SwapVolume ^
```

### SwapVolume

```
"name": str
"label": str ?
"pagesize": str ?
"uuid": str ?
```

#### Implicit Fields

Inherits `device` properties from its parent specification.

* `device`: `{parent}`
