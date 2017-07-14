class RasError(Exception):
    status_code = 500

    def to_dict(self):
        return {'errors': [str(self)]}


class RasDatabaseError(RasError):
    pass
