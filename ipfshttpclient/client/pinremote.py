from . import base


class Section(base.SectionBase):
    def service_add(self, service: str, endpoint: str,
                    key: str,
                    **kwargs: base.CommonArgs):
        args = (service, endpoint, key)
        return self._client.request('/pin/remote/service/add',
                                    args, **kwargs)

    @base.returns_single_item(base.ResponseBase)
    def service_ls(self, stat: bool = False, **kwargs: base.CommonArgs):
        kwargs.setdefault('opts', {'stat': stat})

        return self._client.request('/pin/remote/service/ls', (),
                                    decoder='json', **kwargs)

    def service_rm(self, service: str, **kwargs: base.CommonArgs):
        args = (service,)
        return self._client.request('/pin/remote/service/rm', args, **kwargs)

    @base.returns_single_item(base.ResponseBase)
    def add(self, service: str, path: base.cid_t,
            name: str = None, background = False,
            **kwargs: base.CommonArgs):
        opts = {
            'service': service,
            'arg': path,
            'background': background
        }
        if name:
            opts['name'] = name

        kwargs.setdefault('opts', opts)

        return self._client.request('/pin/remote/add', (),
                                    decoder='json', **kwargs)

    @base.returns_multiple_items(base.ResponseBase)
    def ls(self, service: str,
           name: str = None, cid: list = [],
           status: list = ['pinned'],
            **kwargs: base.CommonArgs):
        opts = {
            'service': service,
            'status': status
        }

        if len(cid) > 0:
            opts['cid'] = cid

        if name:
            opts['name'] = name

        kwargs.setdefault('opts', opts)

        return self._client.request('/pin/remote/ls', (),
                                    decoder='json', **kwargs)

    def rm(self, service: str,
           name: str = None, cid: list = [],
           status: list = ['pinned'],
           force: bool = False,
            **kwargs: base.CommonArgs):
        opts = {
            'service': service,
            'cid': cid,
            'status': status,
            'force': force
        }

        if len(cid) > 0:
            opts['cid'] = cid

        if name is not None:
            opts['name'] = name

        kwargs.setdefault('opts', opts)

        return self._client.request('/pin/remote/rm', (), **kwargs)
