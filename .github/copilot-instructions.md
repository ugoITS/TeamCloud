# Contesto del progetto ITS Cloud

Questo repository contiene un laboratorio Docker Compose eseguito
su una VM Ubuntu.

## Architettura

Servizi:

- web1: backend NGINX principale.
- web2: backend NGINX di backup.
- loadbalancer: reverse proxy NGINX.
- attendance-api: API Flask per le presenze.
- dns-master: DNS BIND primario.
- dns-slave: DNS BIND secondario.
- dns-monitor: API che confronta stato, record e seriali DNS.

Docker Compose combina:

- compose.yaml
- compose.override.yaml

## Failover web

Il progetto usa una configurazione active-passive:

- WEB1 è il server principale.
- WEB2 è configurato come backup.
- Se WEB1 non risponde, WEB2 serve il sito.
- Quando WEB1 torna disponibile, riprende il ruolo principale.

Non trasformare il sistema in round-robin senza una richiesta esplicita.

## Persistenza

Le presenze sono gestite da attendance-api.

Il database SQLite deve rimanere nel volume Docker attendance_data.

WEB1 e WEB2 non devono salvare dati applicativi localmente.

Non eseguire o suggerire:

docker compose down -v

perché eliminerebbe i volumi persistenti.

## DNS

La zona è teamcloud.test.

- master: 172.30.0.10
- slave: 172.30.0.11

Il seriale SOA deve essere incrementato dopo ogni modifica della zona.

La ricorsione DNS deve restare disabilitata.

## Sicurezza

- Non leggere o mostrare /etc/cloud-alerts/telegram.env.
- Non inserire token Telegram nel repository.
- Non montare il socket Docker nei container applicativi.
- Non pubblicare password, chat ID o altri segreti.
- Usare nomi fittizi nelle presenze di prova.
- Non modificare firewall, VirtualBox o rete Windows senza richiesta esplicita.

## Procedura per le modifiche

Prima di modificare un file:

1. Leggere il contenuto attuale.
2. Creare un backup oppure un commit Git.
3. Proporre una modifica minima.
4. Validare la sintassi.
5. Applicare la modifica.
6. Eseguire test mirati.
7. Mostrare il risultato.

## Validazione

Dopo modifiche a Docker Compose:

docker compose config --quiet
docker compose config --services

Dopo modifiche a NGINX:

docker compose exec loadbalancer nginx -t

Dopo modifiche Python:

python3 -m py_compile PERCORSO_FILE

Dopo modifiche allo script Telegram:

sudo bash -n /usr/local/bin/its-cloud-telegram-alerts.sh

## Test applicativi

curl -fsS http://localhost/health
curl -fsS http://localhost/api/presenze
curl -fsS http://localhost/api/dns-status

## Stile delle risposte

- Rispondere in italiano.
- Procedere in piccoli passaggi verificabili.
- Fornire comandi copiabili.
- Non presumere che i comandi siano riusciti.
- Non modificare servizi non coinvolti.
