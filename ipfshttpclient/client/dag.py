import typing as ty

from . import base

from .. import multipart


class Section(base.SectionBase):
	@base.returns_single_item(base.ResponseBase)
	def get(self, cid: str, **kwargs: base.CommonArgs):
		args = (str(cid),)
		return self._client.request('/dag/get', args, decoder='json', **kwargs)

	@base.returns_single_item(base.ResponseBase)
	def put(self, data: ty.IO, **kwargs: base.CommonArgs):
		body, headers = multipart.stream_files(data, chunk_size=self.chunk_size)
		return self._client.request('/dag/put', decoder='json', data=body,
		                            headers=headers, **kwargs)

	@base.returns_single_item(base.ResponseBase)
	def resolve(self, cid: str, **kwargs: base.CommonArgs):
		args = (str(cid),)
		return self._client.request('/dag/resolve', args, decoder='json', **kwargs)

	@base.returns_single_item(base.ResponseBase)
	def imprt(self, data: ty.IO, **kwargs: base.CommonArgs):
		body, headers = multipart.stream_files(data, chunk_size=self.chunk_size)
		return self._client.request('/dag/import', decoder='json', data=body,
		                            headers=headers, **kwargs)

	def export(self, cid: str, **kwargs: base.CommonArgs):
		args = (str(cid),)
		return self._client.request('/dag/export', args, **kwargs)
