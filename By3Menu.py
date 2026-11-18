# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import threading

import sublime
import sublime_plugin


def _import_lib():
    try:
        from .lib import by3menu_lib
        return by3menu_lib
    except (ImportError, ValueError):
        import lib.by3menu_lib as by3menu_lib
        return by3menu_lib


def _reload_lib(module):
    try:
        from importlib import reload as reload_mod
    except ImportError:
        try:
            from imp import reload as reload_mod
        except ImportError:
            reload_mod = reload
    return reload_mod(module)


by3menu_lib = _reload_lib(_import_lib())

_PANEL = 'By3Menu'
_CREATE_NO_WINDOW = 0x08000000
_DETACHED_PROCESS = 0x00000008
_CREATE_NEW_PROCESS_GROUP = 0x00000200


def _ui(callback):
    sublime.set_timeout(callback, 0)


def _status(text):
    sublime.status_message(by3menu_lib.to_text(text))


def _error(text):
    sublime.error_message(u'By3Menu\n' + by3menu_lib.to_text(text))


def _append_panel(window, text):
    def append():
        try:
            panel = window.create_output_panel(_PANEL)
            panel.set_read_only(False)
            panel.run_command('append', {'characters': by3menu_lib.to_text(text)})
            panel.show(panel.size())
            panel.set_read_only(True)
        except Exception:
            pass

    _ui(append)


def _show_panel(window, text):
    def show():
        try:
            panel = window.create_output_panel(_PANEL)
            panel.set_read_only(False)
            panel.run_command('append', {'characters': by3menu_lib.to_text(text)})
            panel.show(panel.size())
            panel.set_read_only(True)
            window.run_command('show_panel', {'panel': 'output.' + _PANEL})
        except Exception:
            pass

    _ui(show)


def _active_file(window):
    view = window.active_view()
    if view is None:
        return None, 1, u''
    file_path = view.file_name()
    line = 1
    selection = u''
    regions = view.sel()
    if regions:
        region = regions[0]
        row, _column = view.rowcol(region.b)
        line = row + 1
        selection = view.substr(region)
    return file_path, line, selection


def _run_bat(window, project, result):
    parts = result['script']
    path = by3menu_lib.script_path(project, parts)
    if not os.path.isfile(path):
        _error(by3menu_lib.MSG_NO_SCRIPT % by3menu_lib.to_text(path))
        return
    header = u'\n[By3Menu] %s\n' % result['title']
    notice = result.get('notice')
    if notice:
        header += notice + u'\n'
    _show_panel(window, header)
    command = by3menu_lib.windows_cmd_line([path] + result['args'])
    env = by3menu_lib.prepare_env(result.get('env'))
    cwd = by3menu_lib.to_native(project)

    def worker():
        try:
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'stdin': subprocess.PIPE,
                'cwd': cwd,
                'env': env,
                'bufsize': 0,
            }
            if by3menu_lib.is_windows():
                kwargs['creationflags'] = _CREATE_NO_WINDOW
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                kwargs['startupinfo'] = startupinfo
            proc = subprocess.Popen(command, **kwargs)
            proc.stdin.close()
            while True:
                chunk = proc.stdout.readline()
                if not chunk:
                    break
                text = by3menu_lib.to_text(chunk).replace(u'\r\n', u'\n').replace(u'\r', u'\n')
                _append_panel(window, text)
            code = proc.wait()
            if code != 0:
                _append_panel(window, u'[By3Menu] 退出码 %s\n' % code)
        except Exception as exc:
            _append_panel(window, u'[By3Menu] %s\n' % by3menu_lib.exc_text(exc))

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()


def _run_svn(window, project, result):
    path_value = os.environ.get('PATH', '')
    executable = by3menu_lib.find_on_path(by3menu_lib.TORTOISE_EXE, path_value)
    if not executable:
        _error(by3menu_lib.MSG_NO_TORTOISE)
        return
    argv = [executable] + result['args']
    native_argv = [by3menu_lib.to_native(item) for item in argv]
    cwd = by3menu_lib.to_native(project)

    def launch():
        try:
            kwargs = {'cwd': cwd}
            if by3menu_lib.is_windows():
                kwargs['creationflags'] = _DETACHED_PROCESS | _CREATE_NEW_PROCESS_GROUP
                if sys.version_info[0] >= 3:
                    kwargs['close_fds'] = True
            else:
                kwargs['close_fds'] = True
            subprocess.Popen(native_argv, **kwargs)
        except Exception as exc:
            _error(by3menu_lib.exc_text(exc))

    _ui(launch)


class By3MenuRunCommand(sublime_plugin.WindowCommand):
    def run(self, action=None, **kwargs):
        try:
            self._run(action)
        except Exception as exc:
            _error(by3menu_lib.exc_text(exc))

    def _run(self, action):
        if not by3menu_lib.is_windows():
            _error(by3menu_lib.MSG_WINDOWS)
            return
        file_path, line, selection = _active_file(self.window)
        folders = self.window.folders() or []
        project = by3menu_lib.project_folder_for(folders, file_path)
        result = by3menu_lib.plan(action, project, file_path, line, selection)
        if not result.get('ok'):
            _status(result.get('message') or by3menu_lib.MSG_UNKNOWN % u'')
            return
        if result['kind'] == 'svn':
            _run_svn(self.window, project, result)
            return
        _run_bat(self.window, project, result)
