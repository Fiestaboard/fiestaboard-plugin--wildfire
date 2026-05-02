"""Display active wildfire incidents from the National Interagency Fire Center (NIFC)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/CY_WildlandFire_Perimeters_ToDate/FeatureServer/0/query"
USER_AGENT = "FiestaBoard Wildfire Tracker Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--wildfire)"


class WildfirePlugin(PluginBase):
    """Wildfire Tracker plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "wildfire"

    def fetch_data(self) -> PluginResult:
        try:
            state_filter = (self.config.get("state") or "").upper().strip()

            params = {
                "where": "1=1",
                "outFields": "IncidentName,POOState,GISAcres,PercentContained,ModifiedOnDateTime_dt",
                "orderByFields": "GISAcres DESC",
                "resultRecordCount": 20,
                "f": "json",
            }
            if state_filter:
                params["where"] = f"POOState='{state_filter}'"

            response = requests.get(
                API_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            active_count = len(features)

            if active_count == 0:
                return PluginResult(
                    available=True,
                    data={
                        "fire_name": "No active fires",
                        "state": "",
                        "acres": "0",
                        "containment": "N/A",
                        "active_count": 0,
                    },
                )

            top_attr = features[0].get("attributes", {})
            fire_name = str(top_attr.get("IncidentName", "Unknown"))[:20]
            state = str(top_attr.get("POOState", ""))[:3]
            raw_acres = top_attr.get("GISAcres", 0) or 0
            acres = f"{int(raw_acres):,}"
            pct = top_attr.get("PercentContained", 0) or 0
            containment = f"{int(pct)}%"

            return PluginResult(
                available=True,
                data={
                    "fire_name": fire_name,
                    "state": state,
                    "acres": acres,
                    "containment": containment,
                    "active_count": active_count,
                },
            )
        except Exception as e:
            logger.exception("Error fetching wildfire data")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        return []

    def cleanup(self) -> None:
        pass
