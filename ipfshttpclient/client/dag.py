import typing as ty

from . import base

from .. import multipart
from .. import utils



class Section(base.SectionBase):
    def export(self, cid: str):
        pass

    def get(self, ref: str):
        pass

    def import_(self, file: ty.IO, pin: bool = True):
        pass

    def put(self, data: ty.IO, format: str = 'cbor', encoding: str = 'json',
            pin: bool = True, hash: str = '.'):
        pass

    def resolve(self, ref: str):
        pass
