from fastapi import HTTPException, Query
from collections import defaultdict
from models.book import Book
from datetime import datetime, timedelta, timezone
from typing import Optional, List

async def get_analytic(current_user):
    user_id = current_user.get("id")
    books = await Book.find(Book.user_id == user_id).to_list()

    if not books:
        raise HTTPException(status_code= 404, detail= f"user doesn't have book, please create one")

    books_dict = [book.dict() for book in books]

    child_analytic = _aggregate_child_analytic(books_dict)
    
    concept_performance = child_analytic.get("concept_performance")
    weekly_timeline = child_analytic.get("weekly_timeline")
    overall_stats = child_analytic.get("overall_stats")
    
    return {
        "data": {
            "child_info": {
                "user_id": user_id,
                "age_group": "8-10",
                "last_active": "2025-01-15T14:20:00Z"
            },
            "recent_status": {
                "active_story": {
                    "title": "Celengan Si Kecil",
                    "current_scene": 3,
                    "total_scenes": 8,
                    "started_at": "2025-01-15T14:00:00Z"
                },
                "today_minutes": 25,
                "this_week_minutes": 120
            },
            "concept_performance": concept_performance,
            "weekly_timeline": weekly_timeline,
            "overall_stats": overall_stats
        }
    }

def _aggregate_child_analytic(books: list) -> dict:
    concept_performance = defaultdict(lambda: {
        "total_decisions": 0,
        "correct_decisions": 0,
        "first_encounter": None,
        "last_encounter": None
    })
    weekly_timeline = defaultdict(lambda: {
        "total_minutes_played": 0,
        "stories_completed": 0,
        "successes": 0,
        "total_choices": 0,
        "concepts_encountered": set(),
        "active_days": set(),
        "session_durations": []
    })
    overall_stats = {
        "total_stories_completed": 0,
        "total_learning_time_seconds": 0,
        "total_correct_choices": 0,
        "total_choices": 0,
        "account_created": None
    }
    
    for book in books:
        themes = book.get("tema", []) or book.get("theme", [])
        user_story = book.get("user_story", {})
        choices = user_story.get("choices", [])
        created_at = book.get("created_at")
        finished_at = book.get("finished_at")
        
        for theme in themes:
            theme_data = concept_performance[theme]
            theme_data["total_decisions"] += len(choices)
            theme_data["correct_decisions"] += sum(1 for c in choices if c.get("choice") == "baik")
            
            if created_at:
                if not theme_data["first_encounter"] or created_at < theme_data["first_encounter"]:
                    theme_data["first_encounter"] = created_at
            if finished_at:
                if not theme_data["last_encounter"] or finished_at > theme_data["last_encounter"]:
                    theme_data["last_encounter"] = finished_at
        
        if book.get("status") == "finished":
            overall_stats["total_stories_completed"] += 1
            if "user_story" in book and "finished_time" in book["user_story"]:
                overall_stats["total_learning_time_seconds"] += book["user_story"]["finished_time"]
        
        overall_stats["total_choices"] += len(choices)
        overall_stats["total_correct_choices"] += sum(1 for c in choices if c.get("choice") == "baik")
        
        if created_at:
            if not overall_stats["account_created"] or created_at < overall_stats["account_created"]:
                overall_stats["account_created"] = created_at
    
    for book in books:
        created_at = book.get("created_at")
        if not created_at:
            continue
            
        week_start = (created_at - timedelta(days=created_at.weekday())).date()
        week_start_str = week_start.isoformat()
        
        week_data = weekly_timeline[week_start_str]
        
        if "user_story" in book and "finished_time" in book["user_story"]:
            minutes = book["user_story"]["finished_time"] / 60
            week_data["total_minutes_played"] += minutes
            week_data["session_durations"].append(minutes)

        if book.get("status") == "finished":
            week_data["stories_completed"] += 1

        choices = book.get("user_story", {}).get("choices", [])
        correct_choices = sum(1 for c in choices if c.get("choice") == "baik")
        week_data["successes"] += correct_choices
        week_data["total_choices"] += len(choices)
        
        themes = book.get("tema", []) or book.get("theme", [])
        week_data["concepts_encountered"].update(themes)
        week_data["active_days"].add(created_at.date())
    
    for theme, data in concept_performance.items():
        total = data["total_decisions"]
        correct = data["correct_decisions"]
        data["success_rate"] = round((correct / total) * 100, 1) if total > 0 else 0.0
    
    final_weekly_timeline = []
    for week_start, data in weekly_timeline.items():
        total_choices = data["total_choices"]
        success_rate = round((data["successes"] / total_choices) * 100, 1) if total_choices > 0 else 0.0
        
        avg_session = (
            sum(data["session_durations"]) / len(data["session_durations"])
            if data["session_durations"] else 0.0
        )
        
        final_weekly_timeline.append({
            "week": week_start,
            "metrics": {
                "total_minutes_played": round(data["total_minutes_played"], 1),
                "stories_completed": data["stories_completed"],
                "success_rate": success_rate,
                "concepts_encountered": list(data["concepts_encountered"]),
                "active_days": len(data["active_days"]),
                "average_session_duration": round(avg_session, 1)
            }
        })
    
    final_weekly_timeline.sort(key=lambda x: x["week"], reverse=True)
    
    total_choices = overall_stats["total_choices"]
    overall_success = (
        round((overall_stats["total_correct_choices"] / total_choices) * 100, 1)
        if total_choices > 0 else 0.0
    )
    
    concepts_mastered = []
    concepts_learning = []
    concepts_struggling = []
    
    for theme, data in concept_performance.items():
        if data["success_rate"] > 80:
            concepts_mastered.append(theme)
        elif data["success_rate"] >= 60:
            concepts_learning.append(theme)
        else:
            concepts_struggling.append(theme)
    
    return {
        "concept_performance": dict(concept_performance),
        "weekly_timeline": final_weekly_timeline,
        "overall_stats": {
            "total_stories_completed": overall_stats["total_stories_completed"],
            "total_learning_time_hours": round(overall_stats["total_learning_time_seconds"] / 3600, 1),
            "overall_success_rate": overall_success,
            "concepts_mastered": concepts_mastered,
            "concepts_learning": concepts_learning,
            "concepts_struggling": concepts_struggling,
            "account_created": overall_stats["account_created"]
        }
    }

def _filter_books_by_time(
        books: list,
        time_unit: Optional[str] = None,
        num_periods: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> list:
    """Filter books based on time parameters"""
    if not any([time_unit, num_periods, start_date, end_date]):
        return books

    now = datetime.now(timezone.utc)
    filtered_books = []

    for book in books:
        created_at = book.get("created_at")
        if not created_at:
            continue
            
        # FIX: Ensure created_at is offset-aware before comparison
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        # Handle different time filter cases
        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if start <= created_at <= end:
                filtered_books.append(book)

        elif start_date and not end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if start <= created_at <= now:
                filtered_books.append(book)

        elif num_periods and time_unit:
            if time_unit == "week":
                delta = timedelta(weeks=num_periods)
            elif time_unit == "month":
                delta = timedelta(days=30 * num_periods)  # Approximate
            else:
                delta = timedelta(days=0)
            
            start = now - delta
            if created_at >= start:
                filtered_books.append(book)
                
    return filtered_books

# New helper for concept performance aggregation
def _aggregate_concept_performance(books: list, themes: Optional[List[str]] = None) -> dict:
    """Aggregate concept performance from books"""
    concept_performance = defaultdict(lambda: {
        "total_decisions": 0,
        "correct_decisions": 0,
        "first_encounter": None,
        "last_encounter": None
    })
    
    for book in books:
        book_themes = book.get("tema", []) or book.get("theme", [])
        user_story = book.get("user_story", {})
        choices = user_story.get("choices", [])
        created_at = book.get("created_at")
        finished_at = book.get("finished_at")
        
        for theme in book_themes:
            # Skip if theme filtering is applied and this theme isn't in the list
            if themes and theme not in themes:
                continue
                
            theme_data = concept_performance[theme]
            theme_data["total_decisions"] += len(choices)
            theme_data["correct_decisions"] += sum(1 for c in choices if c.get("choice") == "baik")
            
            # Update first/last encounter timestamps
            if created_at:
                if not theme_data["first_encounter"] or created_at < theme_data["first_encounter"]:
                    theme_data["first_encounter"] = created_at
            if finished_at:
                if not theme_data["last_encounter"] or finished_at > theme_data["last_encounter"]:
                    theme_data["last_encounter"] = finished_at
    
    # Calculate success rates
    for theme, data in concept_performance.items():
        total = data["total_decisions"]
        correct = data["correct_decisions"]
        data["success_rate"] = round((correct / total) * 100, 1) if total > 0 else 0.0
    
    return dict(concept_performance)

# Concept performance endpoint handler
async def get_concept_performance(
    current_user,
    themes: Optional[str] = Query(None, description="Comma-separated list of themes to filter"),
    time_unit: Optional[str] = Query(None, description="Time unit: 'week' or 'month'"),
    num_periods: Optional[int] = Query(None, description="Number of time units to look back"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    user_id = current_user.get("id")
    books = await Book.find(Book.user_id == user_id).to_list()
    
    if not books:
        raise HTTPException(status_code=404, detail="User doesn't have any books")
    
    # Convert to list of dictionaries
    books_dict = [book.dict() for book in books]
    
    # Apply time filtering
    filtered_books = _filter_books_by_time(
        books_dict, time_unit, num_periods, start_date, end_date
    )
    
    # Parse theme filter if provided
    theme_list = themes
    
    # Aggregate concept performance
    concept_performance = _aggregate_concept_performance(filtered_books, theme_list)
    
    return {"concept_performance": concept_performance}

# Overall statistics endpoint handler
async def get_overall_statistic(current_user):
    user_id = current_user.get("id")    
    books = await Book.find(Book.user_id == user_id).to_list()
    
    if not books:
        raise HTTPException(status_code=404, detail="User doesn't have any books")
    
    books_dict = [book.dict() for book in books]
    
    child_analytic = _aggregate_child_analytic(books_dict)
    return child_analytic["overall_stats"]