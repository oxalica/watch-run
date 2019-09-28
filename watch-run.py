import pyinotify
import sys
import queue
import traceback
import subprocess
import glob
from os import path
from threading import Thread

def monitor(dir_path, handler):
    wm = pyinotify.WatchManager() 
    EVENTS = pyinotify.IN_CLOSE_WRITE | \
        pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO | \
        pyinotify.IN_CREATE | pyinotify.IN_DELETE
    wm.add_watch(dir_path, EVENTS, rec=True) 

    class EventHandler(pyinotify.ProcessEvent):
        def process_default(self, event):
            handler(event.pathname)
    
    notifier = pyinotify.Notifier(wm, EventHandler())
    notifier.loop()

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def main():
    args = sys.argv[1:]
    try:
        delay, immediate, dir_path, excludes, cmds = None, False, None, [], None
        i = 0
        while i < len(args):
            if args[i] == '-t':
                i += 1
                delay = float(args[i])
            elif args[i] == '--':
                cmds = args[i + 1:]
                break
            elif args[i] == '--exclude':
                i += 1
                excludes.append(args[i])
            elif args[i] == '--immediate':
                immediate = True
            else:
                assert dir_path is None, 'Multiple path is not supported'
                dir_path = args[i]
            i += 1

        assert delay is not None, 'Missing -t'
        assert dir_path is not None, 'Missing path'
        assert cmds, 'Missing commands'
    except (ValueError, IndexError, AssertionError) as e:
        eprint(e)
        self_name = path.basename(sys.argv[0])
        eprint(f"Usage: {sys.argv[0]} -t <delay> [--exclude <relpath>...] <dir_path> -- <command...>")
        sys.exit(1)

    excludes = [path.abspath(path.join(dir_path, rel)) for rel in excludes]

    q = queue.Queue()

    def runner():
        trigger = immediate
        while True:
            try:
                if q.get(timeout=delay) is None:
                    return
                trigger = True
                print('File changed')
            except queue.Empty:
                if trigger:
                    trigger = False
                    try:
                        eprint(f'Run: {cmds}')
                        subprocess.run(cmds).check_returncode()
                    except Exception as e:
                        traceback.print_exc()
                        sys.exit(1)

    def handler(abs_path):
        if all(not abs_path.startswith(exc) for exc in excludes):
            q.put(())

    Thread(target=runner, daemon=True).start()
    try:
        eprint('Watching...')
        monitor(dir_path, handler)
    finally:
        q.put(None)

if __name__ == '__main__':
    main()

