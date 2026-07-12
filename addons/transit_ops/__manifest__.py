{
    "name": "TransitOps",
    "version": "17.0.1.0.0",
    "summary": "Fleet management, trip lifecycle, and driver operations",
    "description": """
        TransitOps — End-to-end transit operations management.

        Features:
        - Vehicle registry with status tracking and ROI calculation
        - Driver profiles with license expiry validation
        - Trip lifecycle: Draft → Dispatched → In Transit → Completed
        - Maintenance logs with cost tracking
        - Automated status transitions and business validations
        - Fleet dashboard with pivot tables and graphs
        - PDF trip reports
        - Role-based access control
    """,
    "author": "TransitOps Team",
    "category": "Fleet",
    "license": "MIT",
    "depends": [
        "base",
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
