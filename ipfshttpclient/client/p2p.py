import typing as ty

from . import base


class Section(base.SectionBase):
    @base.returns_no_item
    def forward(self, protocol: str, peer_id: str, port: str, **kwargs: base.CommonArgs):
        """Forward connections to libp2p service

        Forward connections made to the specified port to another IPFS node.

        .. code-block:: python

                # forwards connections made to port 8888 to 'QmHash' as protocol '/x/testproto'
                >>> client.p2p.forward('/x/testproto', 'QmHash', 8888)
                []

        Parameters
        ----------
        protocol
                specifies the libp2p protocol name to use for libp2p connections and/or handlers. It must be prefixed with '/x/'.
        PeerID
                Target endpoint
        port
                Listening endpoint

        Returns
        -------
        list
                An empty list
        """
        args = (protocol, peer_id, port)
        return self._client.request('/p2p/forward', args, decoder='json', **kwargs)

    @base.returns_no_item
    def listen(self, protocol: str, port: str, **kwargs: base.CommonArgs):
        """Create libp2p service to forward IPFS connections to port

        Creates a libp2p service that forwards IPFS connections to it
        to the specified port on the local computer.


        .. code-block:: python

            # listens for connections of protocol '/x/testproto' and forwards them to port 8888
            >>> client.p2p.listen('/x/testproto', 8888)
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
        """Stop listening for new connections to forward.

        Stops all forwarding and listening libp2p services that match the input arguments.

        .. code-block:: python

            # Close listening and forwarding connections of protocol '/x/testproto' and port 8888.
            >>> client.p2p.close(protocol='/x/testproto', port='8888')
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

