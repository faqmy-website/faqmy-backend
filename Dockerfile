FROM python:3.11.2-slim-buster

ENV\
 # system settings
 PATH="/app/.local/bin:/app/.venv/bin:$PATH"\
 DEBIAN_FRONTEND=noninteractive\
 # python settings
 PYTHONFAULTHANDLER=1\
 PYTHONUNBUFFERED=1\
 PYTHONHASHSEED=random\
 PYTHONDONTWRITEBYTECODE=1\
 # pip settings
 PIP_NO_CACHE_DIR=off\
 PIP_DISABLE_PIP_VERSION_CHECK=on\
 PIP_DEFAULT_TIMEOUT=100\
 # poetry settings
 POETRY_VERSION=1.3.2\
 POETRY_NO_INTERACTION=1\
 POETRY_VIRTUALENVS_CREATE=true\
 POETRY_VIRTUALENVS_IN_PROJECT=true\
 POETRY_CACHE_DIR='/app/.cache/pypoetry'\
 POETRY_INSTALLER_MAX_WORKERS=10\
 # app settings
 TIMEOUT=10\
 PORT=8000\
 USERNAME=faqmy
RUN\
 apt-get update -y &&\
 apt-get install -y\
  libgl1 \
  libglib2.0-0

RUN mkdir /app
WORKDIR /app

RUN \
  groupadd -r $USERNAME && \
  useradd -d /app -r -g $USERNAME $USERNAME && \
  chown $USERNAME:$USERNAME -R /app

COPY --chown=$USERNAME:$USERNAME \
 poetry.lock pyproject.toml \
 src alembic.ini README.md \
 pytest.ini \
 /app/
COPY --chown=$USERNAME:$USERNAME alembic /app/alembic

RUN rm -rf /var/cache/apt

USER $USERNAME
RUN\
 python -m pip install --upgrade pip setuptools wheel --user &&\
 python -m pip install poetry==$POETRY_VERSION --user

RUN poetry config virtualenvs.create true
RUN poetry config installer.max-workers 10
RUN poetry install\
  --only main\
  --no-interaction\
  --no-ansi\
  --no-root

RUN rm -rf "${POETRY_CACHE_DIR}"
RUN rm -rf /app/.cache/pip


CMD gunicorn faqmy_backend.app.asgi:app\
 -b 0.0.0.0:${PORT}\
 -k uvicorn.workers.UvicornWorker\
 --access-logfile=-
