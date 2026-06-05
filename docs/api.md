# GripMind API v1

Base URL:

```text
https://gripmind.onrender.com/api/v1
```

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "GripMind API v1"
}
```

## Get Device Records

```http
GET /devices/{device_id}/records
```

Optional query:

```text
?limit=20
```

Response:

```json
{
  "device_id": "device_demo_001",
  "count": 2,
  "records": [
    {
      "device_id": "device_demo_001",
      "grip": 3.2,
      "timestamp": "20260605 09:30:00"
    }
  ]
}
```

## Get Device Summary

```http
GET /devices/{device_id}/summary
```

Response:

```json
{
  "device_id": "device_demo_001",
  "target_weight": 3.5,
  "latest_record": {
    "device_id": "device_demo_001",
    "grip": 3.8,
    "timestamp": "20260605 18:10:00"
  },
  "today": {
    "count": 2,
    "max_grip": 3.8,
    "average_grip": 3.5,
    "goal_reached": true
  },
  "total_records": 2
}
```

## Get Device Profile

```http
GET /devices/{device_id}/profile
```

## Update Target Weight

```http
PATCH /devices/{device_id}/target
Content-Type: application/json
```

Request:

```json
{
  "target_weight": 4.0
}
```

## Generate Training Suggestion

```http
POST /devices/{device_id}/analysis
```

Response:

```json
{
  "device_id": "device_demo_001",
  "suggestion": "最近握力表現穩定，建議您維持目前訓練頻率...",
  "disclaimer": "This suggestion is for training feedback only and is not a medical diagnosis."
}
```

