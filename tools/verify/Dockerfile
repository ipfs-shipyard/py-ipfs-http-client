ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim

RUN pip install --upgrade pip
RUN pip install tox

# Mount the source code here, instead of to /usr/src/app.
# Otherwise, tox will fail due to folder being read-only.
# Mount only the source code; avoid mounting working folders.

RUN mkdir /source
ADD entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
