import enum
import typing as ty

class FSNodeType(enum.Enum):
	FILE = enum.auto()
	DIRECTORY = enum.auto()

class FSNodeEntry(ty.Generic[ty.AnyStr], ty.NamedTuple):
	type: FSNodeType
	path: ty.AnyStr
	relpath: ty.AnyStr
	name: ty.AnyStr
	parentfd: ty.Optional[int]