"""Read-only API smoke check; never print the bundled application id or URL query."""
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from build_asia import ROOT, parse

_, config = parse((ROOT / 'res/scripts/client/moe_calculator/build_config.pyc').read_bytes())
keys = [c.decode('ascii') for c in config['consts']
        if isinstance(c, bytes) and len(c) == 32 and all(x in b'0123456789abcdef' for x in c)]
if len(keys) != 1:
    raise SystemExit('Cannot uniquely locate bundled application id; no request made.')
endpoint = 'https://api.worldoftanks.asia/wot/tanks/mastery/'
query = urllib.parse.urlencode(dict(application_id=keys[0], distribution='damage',
                                   percentile='20,40,55,65,75,85,95,100', tank_id='1'))
try:
    req = urllib.request.Request(endpoint + '?' + query,
                                 headers={'User-Agent': 'MoE-Calculator-ASIA-compatibility-check'})
    with urllib.request.urlopen(req, timeout=20) as response:
        status = response.status
        data = json.load(response)
    result = {'http_status': status, 'api_status': data.get('status'),
              'data_fields': sorted(data.get('data', {}).keys()) if isinstance(data.get('data'), dict) else [],
              'error_code': data.get('error', {}).get('code'),
              'error_message': data.get('error', {}).get('message')}
except Exception as exc:
    # Exception strings can contain the complete request URL and application id.
    result = {'api_status': 'request_failed', 'exception_type': type(exc).__name__}
result['checked_at_utc'] = datetime.now(timezone.utc).isoformat()
(ROOT / 'dist/api-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
