"""Tests for the wildfire plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.wildfire import WildfirePlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "wildfire",
    "name": "Wildfire Tracker",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "state": {
                "type": "string",
                "title": "US State Filter",
                "description": "Two-letter state code to filter by (leave empty for nationwide).",
                "default": ""
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to fetch wildfire data.",
                "default": 1800,
                "minimum": 900
            }
        },
        "required": []
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "features": [
        {
            "attributes": {
                "IncidentName": "Caldor Fire",
                "POOState": "CA",
                "GISAcres": 28000,
                "PercentContained": 42,
                "ModifiedOnDateTime_dt": 1746000000000
            }
        },
        {
            "attributes": {
                "IncidentName": "Tamarack Fire",
                "POOState": "CA",
                "GISAcres": 15000,
                "PercentContained": 80,
                "ModifiedOnDateTime_dt": 1745990000000
            }
        }
    ]
}
""")


@pytest.fixture
def plugin():
    return WildfirePlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = WildfirePlugin(MANIFEST)
    p.config = json.loads("""
{
    "state": ""
}
""")
    return p


class TestWildfirePlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "wildfire"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.wildfire.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "fire_name" in result.data, "missing variable: fire_name"
        assert "state" in result.data, "missing variable: state"
        assert "acres" in result.data, "missing variable: acres"
        assert "containment" in result.data, "missing variable: containment"
        assert "active_count" in result.data, "missing variable: active_count"

    @patch("plugins.wildfire.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.wildfire.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

