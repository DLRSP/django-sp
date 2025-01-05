import user_sessions.middleware


class UserSessionsMiddleware(
    user_sessions.middleware.SessionMiddleware,
):
    pass
