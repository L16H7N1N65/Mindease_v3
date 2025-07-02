# -*- coding: utf-8 -*-
import pytest
import importlib
import pkgutil

from sqlalchemy.orm import configure_mappers
from app.db.models.base import Base      # your declarative base

# 1) import every sub-module under app.db.models  ---------------------------
def import_all_models():
    import app.db.models as models_pkg
    package_path = models_pkg.__path__
    prefix       = models_pkg.__name__ + "."

    for _, modname, _ in pkgutil.walk_packages(package_path, prefix):
        importlib.import_module(modname)

# 2) force mapper configuration, will raise immediately on errors ----------
def test_mapper_configuration():
    import_all_models()
    # will raise sqlalchemy.exc.InvalidRequestError on any inconsistency
    configure_mappers()