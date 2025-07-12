from fastapi import APIRouter, Depends, Query
from middleware.auth_middleware import get_current_user
from handler.analytic_handler import get_analytic, get_concept_performance, get_overall_statistic
from typing import Optional

router = APIRouter()

@router.get("/api/v1/analytic/dashboard")
async def get_dashboard_analytic(current_user=Depends(get_current_user)):
    return await get_analytic(current_user)

@router.get("/api/v1/analytic/concept-performance")
async def get_concept_performance_route(
    current_user=Depends(get_current_user),
    themes: Optional[str] = Query(None, description="Comma-separated list of themes to filter"),
    time_unit: Optional[str] = Query(None, description="Time unit: 'week' or 'month'"),
    num_periods: Optional[int] = Query(None, description="Number of time units to look back"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    return await get_concept_performance(
        current_user,
        themes=themes,
        time_unit=time_unit,
        num_periods=num_periods,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/api/v1/analytic/overall-statistics")
async def get_overall_statistics_route(current_user=Depends(get_current_user)):
    return await get_overall_statistic(current_user)