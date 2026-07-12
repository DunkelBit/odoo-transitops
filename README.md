# TransitOps

> Fleet management, trip lifecycle, and driver operations platform built on **Odoo 17**.

TransitOps is a custom Odoo module that provides end-to-end transit operations management —
from vehicle registry and driver licensing to trip dispatch, cargo validation, maintenance tracking,
and real-time KPI dashboards with ROI calculations.

## Features

### Core
- **Vehicle Registry** — Track fleet status (Available / On Trip / In Shop), acquisition costs, and odometer readings
- **Driver Management** — License tracking with automatic expiry detection (valid / expiring soon / expired)
- **Trip Lifecycle** — Full state machine: Draft → Dispatched → In Transit → Completed / Cancelled
- **Maintenance Logs** — Preventive, corrective, and emergency maintenance with cost tracking

### Business Logic
- **Automated Status Transitions** — Dispatching a trip automatically sets vehicle and driver to "On Trip"; completing it reverts both to "Available"
- **Cargo Weight Validation** — Prevents dispatching if cargo exceeds the vehicle's maximum load capacity
- **License Expiry Checks** — Blocks trip assignment to drivers with expired licenses
- **Vehicle ROI Calculation** — `(Revenue - (Maintenance + Fuel)) / Acquisition Cost` computed in real time

### Analytics & Dashboard
- **Fleet Utilization** — Pie chart showing Available vs. On Trip vs. In Shop vehicles
- **Trip Revenue** — Bar chart comparing revenue across vehicles and destinations
- **Fuel Efficiency** — Distance vs. fuel consumption analysis
- **Pivot Tables** — Multi-dimensional analysis by vehicle, driver, status, and time period

### Bonus
- **PDF Trip Reports** — QWeb-templated printable reports with trip details, cargo, and financials
- **Automated License Alerts** — Cron job sends email notifications for licenses expiring within 30 days
- **Role-Based Access Control** — Fleet Manager, Driver, and Financial Analyst roles with scoped permissions
- **Demo Data** — Pre-loaded vehicles, drivers, and trips for immediate dashboard visibility

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Odoo 17 (Community Edition) |
| Language | Python 3 |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |
| Deployment | Render.com (Blueprints) |
| Version Control | GitHub |

## Project Structure

```
odoo-transitops/
├── addons/
│   └── transit_ops/
│       ├── models/
│       │   ├── vehicle.py          # Vehicle registry and ROI logic
│       │   ├── driver.py           # Driver profiles and license validation
│       │   ├── trip.py             # Trip lifecycle and cargo constraints
│       │   └── maintenance.py      # Maintenance logs and status triggers
│       ├── views/                  # XML views (Kanban, Form, List, Graph, Pivot)
│       ├── security/               # RBAC groups and access control lists
│       ├── data/                   # Cron jobs for automated checks
│       ├── reports/                # QWeb PDF templates
│       └── demo/                   # Demo data for immediate testing
├── config/
│   └── odoo.conf                   # Odoo server configuration
├── Dockerfile                      # Odoo 17 image + custom addons
├── docker-compose.yml              # Odoo + PostgreSQL stack
├── render.yaml                     # Render.com deployment blueprint
└── README.md
```

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- GitHub account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/odoo-transitops.git
   cd odoo-transitops
   ```

2. **Start the stack**
   ```bash
   docker compose up -d
   ```

3. **Access Odoo** at `http://localhost:8069`
   - Create a new database
   - Go to **Apps** → search for **TransitOps** → Install

4. **Load demo data** (optional)
   - The module includes demo vehicles, drivers, and trips
   - Enable **Developer Mode** → Apps → check **Load demo data** before installing

### Deploy to Render.com

1. Push this repository to GitHub
2. Connect your GitHub repo to Render.com
3. Render detects `render.yaml` and provisions:
   - A **PostgreSQL** database
   - A **Docker web service** running Odoo
4. Access your live instance at `https://your-app.onrender.com`

## Configuration

### Fuel Price
The fuel cost per litre used in ROI calculations is stored as an Odoo system parameter:

| Key | Default | Description |
|-----|---------|-------------|
| `transitops.fuel_price_per_litre` | `1.50` | Configurable via **Settings → Technical → Parameters** |

### Environment Variables (Render)

| Variable | Source | Description |
|----------|--------|-------------|
| `HOST` | Database | PostgreSQL host (auto-linked) |
| `USER` | Database | PostgreSQL user (auto-linked) |
| `PASSWORD` | Database | PostgreSQL password (auto-linked) |
| `ODOO_ADMIN_PASSWD` | Manual | Master database password |

## Roles & Permissions

| Role | Vehicles | Drivers | Trips | Dashboard | Reports |
|------|:--------:|:-------:|:-----:|:---------:|:-------:|
| Fleet Manager | Full CRUD | Full CRUD | Full CRUD | Full | Full |
| Driver | Read | Read (self) | Read/Write (own) | — | — |
| Financial Analyst | Read | Read | Read | Full | Full |

## License

MIT

## Built For

Odoo Hackathon 2026 — Exceeding expectations in 8 hours.
