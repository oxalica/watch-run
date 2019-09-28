# watch-run - Watch a directory and run command.

Requires: Python3, `pyinotify`

Usage: `python3 watch-run -t <delay> [--exclude <relpath>...] <dir_path> -- <command...>`

Inotify Events will be debounced by `<delay>`, and then run command with arguments supplied. Events on excluded paths will be ignored.
