import typing as ty

from . import base


class Section(base.SectionBase):
    @base.returns_no_item
    def forward(self, protocol: str, peer_id: str, port: str, **kwargs: base.CommonArgs):
        """Forward connections to libp2p service

        Forward connections made to <listen-address> to <target-address>.

        .. code-block:: python

                # forwards connections made to 'port' to 'QmHash'
                >>> client.p2p.forward('protocol', 'port', 'QmHash')
                []

        Parameters
        ----------
        protocol
                specifies the libp2p protocol name to use for libp2p connections and/or handlers. It must be prefixed with '/x/'.
        port
                Listening endpoint
PeerID
                Target endpoint

        Returns
        -------
                list
                        An empty list
        """
        args = (protocol, peer_id, port)
        return self._client.request('/p2p/forward', args, decoder='json', **kwargs)

    @base.returns_no_item
    def listen(self, protocol: str, port: str, **kwargs: base.CommonArgs):
        """Create libp2p service


        .. code-block:: python

                Create libp2p service and forward IPFS connections to 'port'
                >>> client.p2p.listen('protocol', 'port')
                []

        Parameters
        ----------
        protocol
                specifies the libp2p handler name. It must be prefixed with '/x/'.
        port
                Listener port to which to forward incoming connections


        Returns
        -------
                list
                        An empty list
        """
        args = (protocol, port)
        return self._client.request('/p2p/listen', args, decoder='json', **kwargs)

    # @base.returns_single_item(base.ResponseBase)
    def close(self, all: bool = False, protocol: str = None, listenaddress: str = None, targetaddress: str = None, **kwargs: base.CommonArgs):
        """Create libp2p service


        .. code-block:: python

                Create libp2p service and forward IPFS connections to 'port'
                >>> client.p2p.listen('protocol', 'port')
                []

        Parameters
        ----------
        protocol
                specifies the libp2p handler name. It must be prefixed with '/x/'.
        port
                Listener port to which to forward incoming connections


        Returns
        -------
                list
                        An empty list
        """

        opts = {}
        if all is not None:
            opts.update({"all": all})
        if protocol is not None:
            opts.update({"protocol": str(protocol)})
        if listenaddress is not None:
            opts.update({"listen-address": str(listenaddress)})
        if targetaddress is not None:
            opts.update({"target-address": str(targetaddress)})

        kwargs.setdefault("opts", {}).update(opts)
        args = (all,)  # if all is not None else ()
        return self._client.request('/p2p/close', decoder='json', **kwargs)
