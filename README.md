# TransitOps

Fleet management, trip lifecycle, and driver operations — built on **Odoo 17**.

We built TransitOps to handle the day-to-day headaches of running a transit fleet: tracking which vehicles are where, knowing when a driver's license is about to expire, and figuring out if a truck is actually making money or just burning fuel.

## What You Get

**Vehicle Management** — See your whole fleet at a glance. Know which trucks are on the road, which are in the shop, and how much each one has cost you versus what it's brought in.

**Driver Profiles** — Every driver's license is tracked with automatic expiry warnings. No more finding out a license expired after assigning a trip.

**Trip Lifecycle** — Draft a trip, dispatch it, track it in transit, and mark it done. The system automatically updates vehicle and driver availability as trips progress. Try to assign too much cargo or a driver with an expired license? The system won't let you.

**Maintenance Logs** — When a truck goes in for service, it gets marked as "In Shop" automatically. Once maintenance is complete and there's nothing else pending, it goes back to available.

**ROI Dashboard** — Built-in analytics show fleet utilization (pie chart), revenue by vehicle (bar chart), fuel efficiency, and cost breakdowns in pivot tables. The ROI formula: `(Revenue - Maintenance - Fuel) / Acquisition Cost`.

**License Expiry Alerts** — A daily cron job checks for licenses expiring within 30 days and emails the fleet manager. Expired licenses get flagged too.

**PDF Reports** — Print trip reports with cargo details, financials, and route info.

**Role-Based Access** — Fleet Managers get full control. Drivers see what they need. Financial Analysts get the dashboards and read access to everything.

## Quick Start

### Prerequisites
- Docker + Docker Compose

### Run Locally

```bash
git clone https://github.com/DunkelBit/odoo-transitops.git
cd odoo-transitops
docker compose up -d
```

Open `http://localhost:8069`, create a database, then install the TransitOps app from the Apps menu.

### Deploy to Render

Connect your GitHub repo to [Render.com](https://render.com) — the `render.yaml` blueprint handles the rest (Odoo web service + PostgreSQL database).

## Configuration

**Fuel price** used for ROI calculations is a system parameter you can change under Settings > Technical > Parameters. Look for `transitops.fuel_price_per_litre` (defaults to 1.50).

## Tech

| What | With What |
|------|-----------|
| Backend & UI | Odoo 17 Community |
| Language | Python 3 |
| Database | PostgreSQL 15 |
| Containers | Docker + Docker Compose |
| Hosting | Render.com (Blueprints) |

## Roles

| Role | Vehicles | Drivers | Trips | Reports |
|------|----------|---------|-------|---------|
| Fleet Manager | Everything | Everything | Everything | Everything |
| Driver | View | View (own) | Read/Write (own) | No |
| Financial Analyst | View | View | View | Everything |

## License

MIT

---

Built for Odoo Hackathon 2026.
