# slowroll

Let's say you want to roll out a feature flag, or something that selects a
canary version.  Put a json config up somewhere, decide how you're hashing your
users, and use `SlowrollConfig`:

```py
from slowroll import SlowrollConfig

sc = SlowrollConfig("https://example.com/config.json", "app_features")
if sc.get_value("features", "install_to_opt_foo", socket.gethostname()):
    ...
```

The config for this would look like

```json
{
    "features": {
        "install_to_opt_foo": {
            "end_time": "2025-01-01 00:00Z",
            "duration": "14d",
            "stable": false,
            "new": true,
            "early_adopters": ["canary-host"],
        }
    }
}
```

Note that the values for "stable" and "new" can be any valid json.  Here they
are bools, but could just as easily be strings that represent versions of a
Python project.  `start_time` is not explicitly specified, but calculated from
the duration.

There are few restrictions on the http server, namely that it _must_ provide
etags using the default implementation, but you can provide your own that takes
an opaque url and an opaque value that you can use to store any etag-esque
metadata.

As in semver, expect no compatibility guarantees until this reaches 1.0.  Both
the API and config format are expected to change.

# Extensibility

* What if I want to store the config in zookeeper?  Sure, provide a custom
  callback that returns the latest version you know of.

# Future Work

* Ability to locally lock a value (either old or new)
* Example using a requests session
* Retries/fallback
* More testing on `_pct` values
* Config validator
* Interpolation of numeric values
* Regex `early_adopters`
* Rollbacks that count down

# License

slowroll is copyright [Tim Hatch](https://timhatch.com/), and licensed under
the MIT license.  I am providing code in this repository to you under an open
source license.  This is my personal repository; the license you receive to
my code is from me and not from my employer. See the `LICENSE` file for details.
