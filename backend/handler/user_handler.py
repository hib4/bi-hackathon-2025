from models import User

async def get_user_profile(current_user):
    user = await User.get(current_user.get("id"))
    return {
        "data": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "auth": user.auth,
            "google_id": user.google_id
        }
    }