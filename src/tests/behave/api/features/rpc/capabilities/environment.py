"""
environment.py

This file is required by Behave to be in the same directory as where the
feature file is being run.

Because we want to be able to reuse the settings in an environment file,
it is also defined in the parent directory.

Each new service will have a it's own environment file which would wildcard
import the methods from the parent file.

see: https://media.readthedocs.org/pdf/behave/latest/behave.pdf
"""
from src.tests.behave.api.features.environment import (  # noqa # pylint: disable=unused-import
    before_all,
    after_all,
    before_feature,
    after_feature,
    before_scenario,
    after_scenario,
    before_step,
    after_step,
)
