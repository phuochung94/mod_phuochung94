# Review fixes — 2026-11-06

## Removed telemetry

Deleted runtime armorshotanalyzer_logger.pyc and its package import. There is
no garage telemetry event subscription, HTTP request, player-name/server
collection, opt-in setting or network reporting in the replacement runtime.
Historical upstream and backup copies remain development-only and are excluded
from both installable packages. audit_privacy.py scans all current package code
objects for the removed network APIs, endpoint and event, and verifies maintained
source matches its compiled bytecode.

## Preserved client results

core/__init__.py is inert. armorshotanalyzer_hooks.py no longer contains copied
default/modern-HE algorithms. The loader explicitly installs:

- Thin wrappers around the active client's two shot-result methods. The original
  executes first, once, with identical inputs, including the original collision
  object. Return values and original exceptions are preserved. No list conversion
  precedes the call. Analysis runs afterward only on plain list/tuple collision
  sequences; iterators and unsupported data omit the overlay.
- Presentation-only wrappers around getShotResult and activatePostmortem, keeping
  results/arguments intact and hiding overlay when required.

The mod never restores native functions by loading copied bytecode or removing
other mods' hooks. It captures the methods active at installation; an already
hooked third-party chain remains intact. A full client restart is required when
upgrading from the rejected version so its old hooks/subscriptions are discarded.

## Unload cleanup

Loader exports idempotent init()/fini(). fini removes this mod's player-event
subscriptions, closes its window and restores saved method descriptors when the
mod still owns those attributes. Inherited descriptors are restored by removing
the local override. Later hooks from another mod are not overwritten. Retained
old wrappers have session guards and remain inert after unload/reload. Partial
installation rolls back through cleanup.

## Validation

- 56 source and 56 compiled-bytecode tests pass using the installed client's
  Python 2.7 DLL.
- Differential regression executes the current client's actual default and
  modern-HE function code extracted from scripts.pkg with controlled collision
  helpers/globals. It exercises exhausted penetration and nonzero HE explosion
  absorption, comparing baseline and wrapped return values. This is stronger
  than the prior sentinel-only tests, but remains an isolated test environment.
- Tests cover identical argument/return objects, untouched iterators, original
  exceptions, failing overlay/error cleanup, repeat install/uninstall, restored
  descriptors, event removal, partial-install rollback, full loader fini, and
  not overwriting another mod's later hook.
- Privacy, no-menu and namespace audits pass. Unchanged base modules remain
  checked against the rename backup; reviewed hooks/core are now maintained
  source instead of frozen upstream bytecode.

No in-game trial or reviewer submission was performed. Existing overlay estimates
and native settings preview retain their documented limitations.

Backup before fixes: backups/before_review_fixes_2026-11-06.zip.
Restore point 2028 remains untouched.
