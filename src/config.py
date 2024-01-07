import os
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)05d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s' , datefmt='%FY%T')

class ApplicationConfiguration:

    RECONNECT_WAIT_TIME: int = 1
    RETRY_NUMBER: int = 10
    ENVIRONMENT: str = "DEV"
    VERSION: str = "0.8.0"
    DEBUG: bool = False

    # Authentication Configuration values
    JWT_KEY_LOCATION: str = "/temp/jwt_token"
    USER_DB_HOST: str = "10.0.0.5"
    USER_DB_PORT: str = "4430"
    TOKEN_TIME_PERIOD: int = 15

    # DB Configuration values
    AUTH_DB_CREDENTIALS_LOCATION: str = "/temp/postgres_credentials/postgres_credentials.json"
    
    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("Start App")

        self.extract_env_variables()
        

    def extract_env_variables(self):
        for attr, attr_type in self.__annotations__.items(): # pylint: disable=E1101
            try:
                self.__setattr__(attr, (attr_type)(os.environ[attr]))
            except Exception as err:
                self.logger.warning(f"Couldn't find {attr} in environment. Run with default value")
        
app_config = ApplicationConfiguration()