class BaseConfig(object):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


def get_network_data(data):
    from app import app
    if data == 'flights':
        if app.testing:
            return 'data/test/flights.csv'
        return 'data/flights.csv'

    if data == 'airports':
        if app.testing:
            return 'data/test/airports.csv'
        return 'data/airports.csv'

    if data == 'lines':
        return 'data/lines.csv'

    if data == 'stations':
        return 'data/stations.json'
