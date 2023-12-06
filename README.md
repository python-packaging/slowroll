# slowroll

Let's say you want to roll out a feature flag, or something that selects a
canary version.  Put a json config up somewhere, decide how you're hashing your
users, and use SlowrollConfig:

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
            "new": true
        }
    }
}
```

Note that the values for "stable" and "new" can be any valid json.  Here they
are bools, but could just as easily be strings that represent versions of a
Python project.  `start_time` is not explicitly specified, but calculated from
the duration.

There are few restrictions on the http server, namely that it _must_ provide
etags, but you can override the fetch callback if you need to use a requests
Session, for example.

This is early code, and most robust error handling, fallbacks, and caching will
come later.

# License

slowroll is copyright [Tim Hatch](https://timhatch.com/), and licensed under
the MIT license.  I am providing code in this repository to you under an open
source license.  This is my personal repository; the license you receive to
my code is from me and not from my employer. See the `LICENSE` file for details.
