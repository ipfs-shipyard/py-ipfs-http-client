
import enum
import typing as ty

AnyStr = ty.TypeVar('AnyStr', bytes, str)


class FSNodeType(enum.Enum):
	FILE = enum.auto()
	DIRECTORY = enum.auto()


class FSNodeEntry(ty.Generic[AnyStr]):
	type: FSNodeType
	path: AnyStr
	relpath: AnyStr
	name: AnyStr
	parentfd: ty.Optional[int]

	def __init__(
			self,
			type: FSNodeType,
			path: AnyStr,
			relpath: AnyStr,
			name: AnyStr,
			parentfd: ty.Optional[int]) -> None:
		self.type = type
		self.path = path
		self.relpath = relpath
		self.name = name
		self.parentfd = parentfd

	def __repr__(self) -> str:
		return (
			f'FSNodeEntry('
			f'type={self.type!r}, '
			f'path={self.path!r}, '
			f'relpath={self.relpath!r}, '
			f'name={self.name!r}, '
			f'parentfd={self.parentfd!r}'
			f')'
		)

	def __str__(self) -> str:
		return str(self.path)
