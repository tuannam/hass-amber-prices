# Amber Prices — Home Assistant Custom Integration

Fetches Amber Electric prices for a given postcode as Home Assistant sensors.

## Example Lovelace Card

To display Amber Prices history, add this to your dashboard:

```yaml
type: history-graph
title: Amber Prices (Last 24h)
hours_to_show: 24
entities:
	- sensor.amber_price_now
	- sensor.amber_feed_in_now
```
