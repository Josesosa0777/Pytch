def rollback_on_exception(func):
    def inner(self, session, *args, **kwargs):
        try:
            return func(self, session, *args, **kwargs)
        except Exception:
            self.logger.error('Unhandled exception caught, discarding changes...')
            session.rollback()
            session.commit()
            raise
    return inner
