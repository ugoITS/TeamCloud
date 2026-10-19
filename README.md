# Progetto ITS Cloud

Progetto didattico di infrastrutture e cloud realizzato in 96 ore.

## Obiettivo

Realizzare un servizio web containerizzato con:

- WEB1 come nodo principale;
- WEB2 come nodo di backup;
- NGINX come load balancer;
- failover automatico;
- DNS master e DNS slave;
- monitoraggio della replica DNS;
- Attendance API sviluppata con Flask;
- database SQLite persistente;
- notifiche Telegram sugli eventi dei backend.

## Architettura

Browser → NGINX Load Balancer → WEB1 / WEB2

Il load balancer inoltra inoltre:

- `/api/presenze` verso Attendance API;
- `/api/dns-status` verso DNS Monitor.

## Tecnologie

- Ubuntu Linux
- Docker
- Docker Compose
- NGINX
- BIND9
- Python
- Flask
- SQLite
- HTML, CSS e JavaScript
- Bash e systemd
- Telegram Bot API

## Avvio

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

## Test del failover

Arresto del nodo principale:

```bash
docker stop cloud_web1
```

Il load balancer utilizzerà WEB2 come backend di backup.

Ripristino del nodo principale:

```bash
docker start cloud_web1
```

## Persistenza delle presenze

Le presenze vengono gestite dalla Attendance API e salvate nel database:

```text
/data/presenze.db
```

La directory `/data` è collegata al volume Docker persistente `attendance_data`.

## Monitoraggio DNS

Il servizio DNS Monitor controlla:

- disponibilità di master e slave;
- seriale SOA;
- record DNS di prova;
- sincronizzazione della zona.

## Notifiche Telegram

Uno script Bash osserva gli eventi Docker di WEB1 e WEB2 e invia notifiche di arresto e ripristino.

Il token e il Chat ID non sono inclusi nel repository.

## Autore

Damiano Funari  
Progetto ITS Infrastrutture e Cloud