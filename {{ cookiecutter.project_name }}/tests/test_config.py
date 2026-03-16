"""Tests for application configuration classes."""

import pytest
from flask import Flask

from {{ cookiecutter.package_name }}.app import create_app
from {{ cookiecutter.package_name }}.config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)


@pytest.mark.unit
class TestConfig:
    def test_debug_is_false(self) -> None:
        assert Config.DEBUG is False

    def test_testing_is_false(self) -> None:
        assert Config.TESTING is False

    def test_sqlalchemy_engines_default(self) -> None:
        assert Config.SQLALCHEMY_ENGINES == {"default": "sqlite:///default.sqlite"}


@pytest.mark.unit
class TestDevelopmentConfig:
    def test_inherits_from_base(self) -> None:
        assert issubclass(DevelopmentConfig, Config)

    def test_debug_is_true(self) -> None:
        assert DevelopmentConfig.DEBUG is True

    def test_testing_is_false(self) -> None:
        assert DevelopmentConfig.TESTING is False


@pytest.mark.unit
class TestTestingConfig:
    def test_inherits_from_base(self) -> None:
        assert issubclass(TestingConfig, Config)

    def test_testing_is_true(self) -> None:
        assert TestingConfig.TESTING is True

    def test_debug_is_false(self) -> None:
        assert TestingConfig.DEBUG is False

    def test_uses_in_memory_database(self) -> None:
        assert TestingConfig.SQLALCHEMY_ENGINES == {"default": "sqlite://"}


@pytest.mark.unit
class TestProductionConfig:
    def test_inherits_from_base(self) -> None:
        assert issubclass(ProductionConfig, Config)

    def test_debug_is_false(self) -> None:
        assert ProductionConfig.DEBUG is False

    def test_testing_is_false(self) -> None:
        assert ProductionConfig.TESTING is False


@pytest.mark.unit
class TestCreateAppWithConfig:
    def test_testing_config_sets_testing_flag(self) -> None:
        app = create_app(TestingConfig)
        assert app.testing is True

    def test_development_config_sets_debug_flag(self) -> None:
        app = create_app(DevelopmentConfig)
        assert app.debug is True

    def test_default_config_is_development(self) -> None:
        app = create_app()
        assert app.debug is True

    def test_testing_config_uses_in_memory_db(self) -> None:
        app = create_app(TestingConfig)
        assert app.config["SQLALCHEMY_ENGINES"] == {"default": "sqlite://"}

    def test_app_is_flask_instance(self) -> None:
        app = create_app(TestingConfig)
        assert isinstance(app, Flask)


@pytest.mark.unit
class TestProductionSecretKeyValidation:
    """Tests that create_app rejects insecure SECRET_KEY in production."""

    def test_raises_with_default_insecure_key(self) -> None:
        with pytest.raises(
            ValueError, match="SECRET_KEY must be set to a secure value"
        ):
            create_app(ProductionConfig)

    def test_raises_with_empty_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "")
        with pytest.raises(
            ValueError, match="SECRET_KEY must be set to a secure value"
        ):
            create_app(ProductionConfig)

    def test_accepts_real_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            ProductionConfig, "SECRET_KEY", "a-real-production-secret-key"
        )
        app = create_app(ProductionConfig)
        assert app.config["SECRET_KEY"] == "a-real-production-secret-key"
