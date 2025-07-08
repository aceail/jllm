USER_COLORS = [
    "text-red-600",
    "text-blue-600",
    "text-green-600",
    "text-purple-600",
    "text-orange-600",
]


def get_user_color(username: str) -> str:
    """Return a stable color class for the given username."""
    return USER_COLORS[hash(username) % len(USER_COLORS)]
