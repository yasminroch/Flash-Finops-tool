from fastapi import APIRouter
from ..services.duckdb_service import get_db_service
import math

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def sanitize_value(val):
    """Convert NaN/Inf values to None for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val


def df_to_dicts(df):
    """Convert DataFrame to list of dicts with sanitized values."""
    records = df.to_dict(orient="records")
    return [
        {k: sanitize_value(v) for k, v in record.items()}
        for record in records
    ]


@router.get("/metrics")
async def get_metrics():
    """Get main dashboard metrics."""
    db = get_db_service()

    # Total and active users
    users_stats = db.execute_query("""
        SELECT 
            COUNT(*) as total_users,
            SUM(CASE WHEN is_active = 'true' THEN 1 ELSE 0 END) as active_users
        FROM dim_users
    """)

    total_users = int(users_stats.iloc[0]["total_users"])
    active_users = int(users_stats.iloc[0]["active_users"])

    # Current month cost (latest available)
    cost_current = db.execute_query("""
        SELECT valor_clean 
        FROM contract_costs 
        WHERE valor_clean > 0
        ORDER BY data_parsed DESC 
        LIMIT 1
    """)
    current_cost = float(cost_current.iloc[0]["valor_clean"]) if len(cost_current) > 0 else 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "idle_users": total_users - active_users,
        "total_cost_current_month": f"R$ {current_cost:,.2f}",
        "licenses_contracted": 610,
    }


@router.get("/cost-trend")
async def get_cost_trend():
    """Get cost trend over time."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            STRFTIME(data_parsed, '%Y-%m') as month,
            valor_clean as cost
        FROM contract_costs
        WHERE valor_clean > 0
        ORDER BY data_parsed
    """)

    return {"data": df_to_dicts(df)}


@router.get("/users-by-department")
async def get_users_by_department():
    """Get user distribution by department."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            COALESCE(NULLIF(department, 'N/A'), 'Sem departamento') as department,
            COUNT(*) as user_count,
            SUM(CASE WHEN is_active = 'true' THEN 1 ELSE 0 END) as active_count
        FROM dim_users
        GROUP BY 1
        ORDER BY user_count DESC
        LIMIT 15
    """)

    return {"data": df_to_dicts(df)}


@router.get("/users-by-cost-center")
async def get_users_by_cost_center():
    """Get user distribution by cost center."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            COALESCE(NULLIF(cost_center, 'N/A'), 'Sem CC') as cost_center,
            COUNT(*) as user_count,
            SUM(CASE WHEN is_active = 'true' THEN 1 ELSE 0 END) as active_count
        FROM dim_users
        WHERE cost_center != 'N/A'
        GROUP BY 1
        ORDER BY user_count DESC
        LIMIT 15
    """)

    return {"data": df_to_dicts(df)}


@router.get("/idle-users")
async def get_idle_users():
    """Get list of idle users (enabled but no recent activity)."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            u.metabase_user_id,
            u.department,
            u.cost_center,
            u.job_title,
            u.last_login,
            u.joined_at
        FROM dim_users u
        WHERE u.is_active = 'true'
          AND (u.last_login IS NULL OR u.last_login = '')
        ORDER BY u.joined_at
        LIMIT 30
    """)

    return {"data": df_to_dicts(df)}


@router.get("/activity-timeline")
async def get_activity_timeline():
    """Get daily activity aggregated by month."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            STRFTIME(date_parsed, '%Y-%m') as month,
            COUNT(*) as total_events,
            SUM(CAST(viewed_dashboard AS INTEGER)) as dashboard_views,
            SUM(CAST(viewed_card AS INTEGER)) as card_views,
            COUNT(DISTINCT metabase_user_id) as unique_users
        FROM user_activity
        GROUP BY 1
        ORDER BY 1
    """)

    return {"data": df_to_dicts(df)}


@router.get("/top-active-users")
async def get_top_active_users():
    """Get most active users."""
    db = get_db_service()

    df = db.execute_query("""
        SELECT 
            a.metabase_user_id,
            u.department,
            u.cost_center,
            COUNT(*) as activity_days,
            SUM(CAST(a.viewed_dashboard AS INTEGER)) as dashboards_viewed,
            SUM(CAST(a.viewed_card AS INTEGER)) as cards_viewed
        FROM user_activity a
        LEFT JOIN dim_users u ON a.metabase_user_id = u.metabase_user_id
        GROUP BY 1, 2, 3
        ORDER BY activity_days DESC
        LIMIT 20
    """)

    return {"data": df_to_dicts(df)}
