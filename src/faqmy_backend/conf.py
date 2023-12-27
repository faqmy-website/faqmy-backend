import enum

import pydantic


class LogLevels(str, enum.Enum):
    info = "info"
    debug = "debug"
    warning = "warning"


class AppSettings(pydantic.BaseSettings):
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: LogLevels = LogLevels.info


class DatabaseSettings(pydantic.BaseSettings):
    url: pydantic.PostgresDsn
    echo: bool = False

    class Config:
        env_prefix = "DATABASE_"


class UserSettings(pydantic.BaseSettings):
    cookie_max_age: int = 3600
    bearer_token_url: str = "/v1/auth/jwt/login"
    jwt_lifetime_seconds: int = 3600
    jwt_secret: str = "XXXXXXXXXXXXXX"

    reset_password_token_secret: str = "XXXXXXXXXXXXXX"
    verification_token_secret: str = "XXXXXXXXXXXXXX"

    class Config:
        env_prefix = "USER_"


class BotSettings(pydantic.BaseSettings):
    url: str

    class Config:
        env_prefix = "BOT_"


class StripeSettings(pydantic.BaseSettings):
    key: str = "sk_test_feijoa"
    customer_portal_url: str = "https://billing.stripe.com/p/login/test_azazazaz"
    pricing_table_id: str = "prctbl_totototototo"
    publishable_key: str = "pk_test_amamama"

    class Config:
        env_prefix = "STRIPE_"


class SmtpSettings(pydantic.BaseSettings):
    server: str = "smtp-relay.sendinblue.com"
    port: int = 587
    login: str = ""
    key: str = ""
    default_from_email: str = "Faq My Website <noreply@faqmy.website>"

    class Config:
        env_prefix = "SMTP_"


class Settings(pydantic.BaseSettings):
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    users: UserSettings = UserSettings()
    bot: BotSettings = BotSettings()
    smtp: SmtpSettings = SmtpSettings()
    stripe: StripeSettings = StripeSettings()


settings = Settings()
