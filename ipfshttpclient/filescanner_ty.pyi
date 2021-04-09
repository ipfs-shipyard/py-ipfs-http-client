import enum
import typing as ty

AnyStr = ty.TypeVar('AnyStr', bytes, str)

class FSNodeType(enum.Enum):
	FILE = enum.auto()
	DIRECTORY = enum.auto()

class FSNodeEntry(ty.Generic[AnyStr], ty.NamedTuple):
	type: FSNodeType
	path: AnyStr
	relpath: AnyStr
	name: AnyStr
	parentfd: ty.Optional[int]
