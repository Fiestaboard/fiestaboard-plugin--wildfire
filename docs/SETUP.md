# Wildfire Tracker Setup Guide

Display active wildfire incidents from the National Interagency Fire Center (NIFC).

## Overview

The Wildfire Tracker plugin queries the NIFC ArcGIS REST API for active wildfire incidents in the United States. It shows the largest or most recently updated incident, including acreage and containment percentage. No API key required.

- API reference: https://www.nifc.gov/fire-information/nfn

### Prerequisites

No API key required. US-only data.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Wildfire Tracker**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `wildfire` plugin variables:
   ```
   {{{ wildfire.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `wildfire.fire_name` | Name of the largest active fire | `Caldor Fire` |
| `wildfire.state` | State where the fire is located | `CA` |
| `wildfire.acres` | Acres burned (most recent estimate) | `28,000` |
| `wildfire.containment` | Percent containment | `42%` |
| `wildfire.active_count` | Total number of active fires in the query result | `15` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `state` | US State Filter | Two-letter state code to filter by (leave empty for nationwide). | `` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to fetch wildfire data. | `1800` |

## Troubleshooting

- **No fires shown** — if there are no active fires in the query area, the plugin shows 'No active fires'.
- **Wrong state** — state codes are two-letter USPS abbreviations (CA, OR, WA, etc.).
- **Slow response** — the ArcGIS API can be slow; the timeout is 15 seconds.

