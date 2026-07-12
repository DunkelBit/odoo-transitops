{
    "name": "TransitOps",
    "version": "17.0.1.0.0",
    "summary": "Fleet management, trip lifecycle, and driver operations",
    "description": """
        TransitOps — Manage your fleet, drivers, trips and maintenance in one place.

        What it does:
        - Track vehicles (trucks, vans, trailers) with status and cost info
        - Manage drivers with automatic license expiry tracking
        - Full trip lifecycle from draft to completion with cargo checks
        - Maintenance logging that updates vehicle availability
        - ROI calculations per vehicle (revenue vs costs)
        - Dashboard with charts and pivot tables for analytics
        - PDF trip reports and automated license expiry email alerts
    """,
    "author": "TransitOps Team",
    "category": "Fleet",
    "license": "MIT",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/vehicle_views.xml",
        "views/driver_views.xml",
        "views/trip_views.xml",
        "views/maintenance_views.xml",
        "views/dashboard_views.xml",
        "views/menu.xml",
        "data/cron_jobs.xml",
        "reports/trip_report.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
