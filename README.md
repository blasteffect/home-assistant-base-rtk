# Base RTK (Home Assistant)

Custom integration that polls `http://<host>/status` and exposes sensors.

## Install (HACS)
- Add this repository as a *custom repository* (category: Integration)
- Install, then restart Home Assistant
- Add integration: Settings → Devices & services → Add integration → Base RTK

## API expected
GET `http://<host>/status` returns JSON like:
```json
{
  "rtcmSent": 72318,
  "crcErrors": 39878,
  "heap": 222032,
  "bootTime": "2026-01-06 12:35:59",
  "resetReason": "Alimentation"
}
```
