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

    @base.returns_single_item(base.ResponseBase)
    def put(self, data: ty.IO, **kwargs: base.CommonArgs):
        body, headers = multipart .stream_files(data, chunk_size=self.chunk_size)
        return self._client .request('/dag/put', decoder='json', data=body,
                                     headers=headers, **kwargs)

    def resolve(self, ref: str):
        pass
