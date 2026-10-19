import socket

from flask import Flask, jsonify
import dns.message
import dns.query
import dns.rdatatype


app = Flask(__name__)

ZONE = "teamcloud.test"
CHECK_RECORD = "test.teamcloud.test"

MASTER = "dns-master"
SLAVE = "dns-slave"


def get_ip(host):
    return socket.gethostbyname(host)


def get_serial(host):
    ip = get_ip(host)

    richiesta = dns.message.make_query(
        ZONE,
        dns.rdatatype.SOA
    )

    risposta = dns.query.udp(
        richiesta,
        ip,
        timeout=2
    )

    for record_set in risposta.answer:
        if record_set.rdtype == dns.rdatatype.SOA:
            return int(record_set[0].serial)

    return None


def get_record(host):
    ip = get_ip(host)

    richiesta = dns.message.make_query(
        CHECK_RECORD,
        dns.rdatatype.A
    )

    risposta = dns.query.udp(
        richiesta,
        ip,
        timeout=2
    )

    risultati = []

    for record_set in risposta.answer:
        if record_set.rdtype == dns.rdatatype.A:
            for record in record_set:
                risultati.append(record.address)

    return risultati


def controlla_dns(host):
    try:
        return {
            "online": True,
            "serial": get_serial(host),
            "record": CHECK_RECORD,
            "values": get_record(host)
        }

    except Exception as errore:
        return {
            "online": False,
            "serial": None,
            "record": CHECK_RECORD,
            "values": [],
            "error": str(errore)
        }


@app.route("/health")
def health():
    return "dns-monitor-ok\n"


@app.route("/api/dns-status")
def dns_status():

    master = controlla_dns(MASTER)
    slave = controlla_dns(SLAVE)

    sincronizzati = (
        master["online"]
        and slave["online"]
        and master["serial"] == slave["serial"]
        and master["values"] == slave["values"]
    )

    if not master["online"] or not slave["online"]:
        stato = "offline"

    elif sincronizzati:
        stato = "synced"

    else:
        stato = "updating"

    return jsonify({
        "master": master,
        "slave": slave,
        "synced": sincronizzati,
        "state": stato
    })


app.run(
    host="0.0.0.0",
    port=5000
)
