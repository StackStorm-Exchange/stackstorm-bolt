# Change Log

## v0.1.4

* Fix bug where non-string parameters such as `connection_timeout` and `concurrency` were
  causing errors when running the `bolt` command. Non-string parameters will now be
  cast to a string so that the command invocation library can handle them properly.
  
  Contributed by Nick Maludy (Encore Technologies).

## v0.1.3

* Fix bug with passing empty params_obj variable

## v0.1.2

* Fix bug with passing params through params_obj variable

## v0.1.1

* Fix bug with credentials lookup

## v0.1.0

* Initial Revision
