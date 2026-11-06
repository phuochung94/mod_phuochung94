# Privacy requirement

Do not add, retain, enable or restore collection or transmission of user data
without the user's explicit prior consent. This applies to upstream code and
third-party dependencies. Disclosure alone is not consent. There is currently
no consent for telemetry, analytics or reporting player/account/server details.

ArmorShotAnalyzer's runtime telemetry logger and HTTP reporting have been removed.
The runtime uses shot/collision data locally for the requested overlay; it does
not send player names, server details or usage statistics. Do not initialize
the original reference mod or import its logger to obtain its calculations.

Audit the current runtime with res/development/audit_privacy.py via inspect_client.py.
Development-only upstream references and historical backups may contain the old
logger; they must remain excluded from installable mod packages.

The currently installed OpenWG 1.2.2 package was scanned for the old telemetry
endpoint and common HTTP/player-name markers with no matches. This limited
static scan is not a guarantee about every possible behavior of a dependency.
Review dependencies again when their versions change.
