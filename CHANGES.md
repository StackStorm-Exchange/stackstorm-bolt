# Change Log

## v2.1.0

* Added new `project` option that replaces `boltdir`.

  Contributed by Nick Maludy (Encore Technologies).

## v2.0.0

* Drop Python 2.7 support

## v1.0.0

* Changed pack to use 'targets' instead of 'nodes' for all bolt commands as 'nodes' is deprecated.

  Contributed by Bradley Bishop (Encore Technologies).

## v0.2.2

* Updated the pack's icon to be the new, official, Bolt icon.

  Contributed by Nick Maludy (Encore Technologies).

## v0.2.1

* Fix bug where non-string parameters such as `connection_timeout` and `concurrency` were
  causing errors when running the `bolt` command. Non-string parameters will now be
  cast to a string so that the command invocation library can handle them properly.

  Contributed by Nick Maludy (Encore Technologies).

## v0.2.0

* Add `color` as an option for this pack's config and a parameter to all actions.
  By default, color output is `false` (disabled) to make it easier to parse Bolt's output.
  This can be changed globally in the pack's config, or on any individual action when
  invoking it.

* Previously, this pack would always try to parse the `stdout` of every Bolt run as if it
  had JSON data in it. This caused false exceptions when the user passed in `format='human'`.
  This pack now skips JSON parsing of `stdout` if `format='human'`.

* Added a new action `bolt.apply` that applies a Puppet manifest file (`.pp`) on a set of nodes.

* Added a new action `bolt.puppetfile_show_modules` that lists all modules available to Bolt.

* Added a new action `bolt.version` that returns the version of Bolt that is installed.

## v0.1.3

* Fix bug with passing empty params_obj variable

## v0.1.2

* Fix bug with passing params through params_obj variable

## v0.1.1

* Fix bug with credentials lookup

## v0.1.0

* Initial Revision
