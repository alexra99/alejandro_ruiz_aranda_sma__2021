import aioxmpp.xso
import aioxmpp.stanza

from aioxmpp.utils import namespaces

namespaces.xep0215_v2 = "urn:xmpp:extdisco:2"


class Service(aioxmpp.xso.XSO):
    TAG = namespaces.xep0215_v2, "service"

    host = aioxmpp.xso.Attr("host")
    password = aioxmpp.xso.Attr("password", default=None)
    port = aioxmpp.xso.Attr("port", default=None, type_=aioxmpp.xso.Integer())
    transport = aioxmpp.xso.Attr("transport", default=None)
    type_ = aioxmpp.xso.Attr("type")
    username = aioxmpp.xso.Attr("username", default=None)


@aioxmpp.stanza.IQ.as_payload_class
class Services(aioxmpp.xso.XSO):
    TAG = namespaces.xep0215_v2, "services"

    services = aioxmpp.xso.ChildList([Service])

