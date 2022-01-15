import aioxmpp.structs

from . import xso


async def get_external_services(client, peer: aioxmpp.structs.JID) -> xso.Services:
    req = aioxmpp.stanza.IQ(
        type_=aioxmpp.structs.IQType.GET,
        to=peer,
        payload=xso.Services(),
    )
    return await client.send(req)
