# -*- coding: utf-8 -*-
"""核对 By3Menu 和 Cursor 插件一致，并检查 Sublime 2/3/4 都能加载的写法。"""
from __future__ import print_function

import ast
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import lib.by3menu_lib as by3menu_lib
import ui_spec

PROJECT = os.path.abspath(r'E:\work\master')
BY_FILE = os.path.abspath(os.path.join(PROJECT, 'Assets', 'dev', 'by', 'Foo.lua.txt'))
XM_FILE = os.path.abspath(os.path.join(PROJECT, 'Assets', 'EmmyLuaClass', 'xm', 'Bar.lua.txt'))
PLAIN_FILE = os.path.abspath(os.path.join(PROJECT, 'readme.txt'))
OTHER_DRIVE = os.path.abspath(r'D:\notes\A.lua.txt')

CURSOR_ACTIONS = (
    'push_file', 'push_append_file', 'push_dir', 'push_append_dir', 'push',
    'update_lua_by', 'update_lua_xm', 'update_lua_all',
    'update_sheet', 'update_excel', 'decrypt', 'open_excel',
    'print_by', 'print_xm', 'print_all',
    'hot_reload', 'lua_test', 'reenter', 'refresh_fish', 'back_hall',
    'update_protocol', 'format_protocal',
    'svn_update', 'svn_log', 'svn_commit', 'svn_blame', 'svn_diff',
    'svn_update_root', 'svn_log_root', 'svn_commit_root',
    'svn_update_dir', 'svn_log_dir', 'svn_commit_dir',
    'svn_merge',
)

EDITOR_KEYS = {
    'push_file', 'push_append_file', 'hot_reload', 'lua_test',
    'svn_update', 'svn_log', 'svn_commit', 'svn_blame', 'svn_diff',
    'svn_update_dir', 'svn_log_dir', 'svn_commit_dir',
}


def fail(message):
    raise AssertionError(message)


def plan(action, project=PROJECT, file_path=BY_FILE, line=12, selection=u'hello'):
    return by3menu_lib.plan(action, project, file_path, line, selection)


def test_actions_match_cursor():
    if by3menu_lib.known_actions() != CURSOR_ACTIONS:
        fail('action list drifted from Cursor By3Menu')
    menu_actions = tuple(node['action'] for node in ui_spec.walk_commands(ui_spec.MENU))
    if set(menu_actions) != set(CURSOR_ACTIONS) or len(menu_actions) != len(set(menu_actions)):
        fail('menu actions %s' % (menu_actions,))
    key_actions = tuple(item[0] for item in ui_spec.KEYS)
    if set(key_actions) - set(CURSOR_ACTIONS):
        fail('unknown key action')
    if len(key_actions) != 20 or len(set(key_actions)) != 20:
        fail('expected 20 unique shortcuts')
    editor = set(action for action, _win, _mac, focused in ui_spec.KEYS if focused)
    if editor != EDITOR_KEYS:
        fail('editor focus shortcuts %s' % editor)


def test_names_and_paths():
    if by3menu_lib.sheet_name(BY_FILE) != 'Foo':
        fail('lua.txt sheet')
    if by3menu_lib.sheet_name(os.path.join(PROJECT, 'A.lua')) != 'A':
        fail('lua sheet')
    if by3menu_lib.sheet_name(os.path.join(PROJECT, 'Foo.LUA.TXT')) != 'Foo.LUA':
        fail('case sensitive suffix, same as vscode path.parse')
    if by3menu_lib.config_project(BY_FILE) != 'by':
        fail('by project')
    if by3menu_lib.config_project(XM_FILE) != 'xm':
        fail('xm project')
    if by3menu_lib.config_project(PLAIN_FILE) is not None:
        fail('plain file has no project')
    text, truncated = by3menu_lib.clean_selection(u'a\x00b')
    if text != u'ab' or truncated:
        fail('null selection')
    long_text = u'x' * (by3menu_lib.SELECTION_LIMIT + 5)
    text, truncated = by3menu_lib.clean_selection(long_text)
    if (not truncated) or len(text) != by3menu_lib.SELECTION_LIMIT:
        fail('selection cap')


def test_project_folder():
    root = tempfile.mkdtemp(prefix='by3menu-root-')
    nested = os.path.join(root, 'nested')
    outside = tempfile.mkdtemp(prefix='by3menu-out-')
    try:
        os.makedirs(os.path.join(root, 'tools', 'idea_tools'))
        marker = os.path.join(root, 'tools', 'idea_tools', 'push_lua_file.bat')
        with open(marker, 'w') as handle:
            handle.write('@echo off\n')
        os.makedirs(nested)
        file_path = os.path.join(nested, 'Foo.lua.txt')
        with open(file_path, 'w') as handle:
            handle.write('--\n')
        chosen = by3menu_lib.project_folder_for([nested, root], file_path)
        if os.path.normcase(chosen) != os.path.normcase(root):
            fail('should pick the folder that contains tools/idea_tools, got %s' % chosen)
        chosen = by3menu_lib.project_folder_for([root], None)
        if os.path.normcase(chosen) != os.path.normcase(os.path.abspath(root)):
            fail('no file falls back to first folder')
        chosen = by3menu_lib.project_folder_for([root], os.path.join(outside, 'Z.lua'))
        if os.path.normcase(chosen) != os.path.normcase(os.path.abspath(root)):
            fail('file outside folders uses the first folder')
        if by3menu_lib.project_folder_for([], file_path) is not None:
            fail('no folders')
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(outside, ignore_errors=True)


def test_push_and_hot_args():
    relative = os.path.join('Assets', 'dev', 'by', 'Foo.lua.txt')
    directory = os.path.join('Assets', 'dev', 'by')
    result = plan('push_file')
    if result['args'] != [relative] or result['script'] != by3menu_lib.PUSH_BAT:
        fail('push file %s' % result)
    result = plan('push_append_file')
    if result['args'] != [relative, 'append']:
        fail('push append file')
    result = plan('push_dir')
    if result['args'] != [directory]:
        fail('push dir')
    result = plan('push_append_dir')
    if result['args'] != [directory, 'append']:
        fail('push append dir')
    result = plan('push', file_path=None)
    if result['args'] != [] or result['script'][-1] != 'push.bat':
        fail('push workspace')
    result = plan('hot_reload')
    if result['args'] != ['event_name', 'reload_lua_file', 'lua_file_path', relative]:
        fail('hot reload %s' % result['args'])
    result = plan('lua_test')
    if result['args'] != ['event_name', 'lua_test_func', 'lua_file_path', relative, 'func_name', 'test']:
        fail('lua test')
    for action, event in (
        ('reenter', 'enter_new_fishing'),
        ('refresh_fish', 'refresh_fishing_fish'),
        ('back_hall', 'back_to_hall'),
    ):
        result = plan(action, file_path=None)
        if result['args'] != ['event_name', event]:
            fail(action)
    result = plan('push_file', file_path=OTHER_DRIVE)
    if result['args'] != [OTHER_DRIVE]:
        fail('other drive should stay absolute, got %s' % result['args'])


def test_lua_config_and_protocol():
    result = plan('update_lua_by', file_path=None)
    if result['args'] != [PROJECT, 'full', 'by']:
        fail('update by')
    result = plan('update_lua_xm', file_path=None)
    if result['args'] != [PROJECT, 'full', 'xm']:
        fail('update xm')
    result = plan('update_lua_all', file_path=None)
    if result['args'] != [PROJECT, 'full', 'all']:
        fail('update all')
    result = plan('update_sheet')
    if result['args'] != [PROJECT, 'sheet', 'Foo', 'by']:
        fail('sheet %s' % result['args'])
    result = plan('update_excel', file_path=XM_FILE)
    if result['args'] != [PROJECT, 'excel', 'Bar', 'xm']:
        fail('excel %s' % result['args'])
    result = plan('update_sheet', file_path=None)
    if result['message'] != by3menu_lib.MSG_NO_SHEET:
        fail('missing sheet file message')
    result = plan('update_excel', file_path=PLAIN_FILE)
    if result['message'] != by3menu_lib.MSG_NO_PROJECT_KIND:
        fail('unknown project message')
    result = plan('decrypt', file_path=None)
    if result['args'] != ['1'] or result['script'] != by3menu_lib.DECRYPT_BAT:
        fail('decrypt')
    result = plan('print_by', file_path=None)
    if result['args'] != [PROJECT, 'by']:
        fail('print by')
    result = plan('print_xm', file_path=None)
    if result['args'] != [PROJECT, 'xm']:
        fail('print xm')
    result = plan('print_all', file_path=None)
    if result['args'] != [PROJECT, 'all']:
        fail('print all')
    result = plan('open_excel', selection=u'Fish')
    if result['args'] != ['--root', PROJECT, '--file', BY_FILE]:
        fail('open excel args %s' % result['args'])
    if result['env'] != {by3menu_lib.SELECTION_ENV: u'Fish'}:
        fail('selection env')
    result = plan('open_excel', file_path=None, selection=u'')
    if result['args'] != ['--root', PROJECT]:
        fail('open excel without file')
    huge = u'y' * (by3menu_lib.SELECTION_LIMIT + 1)
    result = plan('open_excel', selection=huge)
    if result.get('notice') != by3menu_lib.MSG_TRUNCATED:
        fail('truncate notice')
    if len(result['env'][by3menu_lib.SELECTION_ENV]) != by3menu_lib.SELECTION_LIMIT:
        fail('truncate length')
    result = plan('format_protocal', file_path=None)
    if result['script'] != by3menu_lib.FORMAT_BAT or result['args'] != ['1']:
        fail('format protocal')
    result = plan('update_protocol', file_path=None)
    if result['script'] != by3menu_lib.UPDATE_PROTOCOL_BAT or result['args'] != ['1']:
        fail('update protocol')
    result = plan('push', project=None, file_path=None)
    if result.get('ok') or result['message'] != by3menu_lib.MSG_NO_PROJECT:
        fail('push without a folder must fail')
    result = plan('svn_update', project=None, file_path=None)
    if result['message'] != by3menu_lib.MSG_NO_PROJECT:
        fail('no project')
    result = plan('svn_update', file_path=None)
    if result['message'] != by3menu_lib.MSG_NO_FILE:
        fail('no file')
    result = plan('nope')
    if not result['message'].startswith(u'未知命令'):
        fail('unknown action')


def test_svn_args():
    directory = os.path.dirname(BY_FILE)
    assets = os.path.join(PROJECT, 'Assets')
    expected = {
        'svn_update': ['/command:update', '/path:' + BY_FILE, '/closeonend:2'],
        'svn_log': ['/command:log', '/path:' + BY_FILE],
        'svn_commit': ['/command:commit', '/path:' + BY_FILE],
        'svn_blame': ['/command:blame', '/path:' + BY_FILE, '/statrev:1', '/endrev:-1', '/line:12'],
        'svn_diff': ['/command:diff', '/path:' + BY_FILE],
        'svn_update_root': ['/command:update', '/path:' + PROJECT],
        'svn_log_root': ['/command:log', '/path:' + PROJECT],
        'svn_commit_root': ['/command:commit', '/path:' + PROJECT],
        'svn_update_dir': ['/command:update', '/path:' + directory, '/closeonend:2'],
        'svn_log_dir': ['/command:log', '/path:' + directory],
        'svn_commit_dir': ['/command:commit', '/path:' + directory],
        'svn_merge': ['/command:merge', '/path:' + assets],
    }
    for action, args in expected.items():
        result = plan(action)
        if result.get('kind') != 'svn' or result['args'] != args:
            fail('%s got %s' % (action, result))
    if '/closeonend:2' in plan('svn_update_root')['args']:
        fail('root update must leave the Tortoise window open, same as Cursor')
    result = plan('svn_blame', line=0)
    if result['args'][-1] != '/line:1':
        fail('line fallback')
    if by3menu_lib.action_id(u'svn_diff') != 'svn_diff' and sys.version_info[0] >= 3:
        fail('action id')


def test_path_search_and_env():
    folder = tempfile.mkdtemp(prefix='by3menu-path-')
    try:
        executable = os.path.join(folder, 'TortoiseProc.exe')
        with open(executable, 'w') as handle:
            handle.write('')
        quoted = '"' + folder + '"'
        path_value = os.pathsep.join(['', quoted, tempfile.gettempdir()])
        found = by3menu_lib.find_on_path('TortoiseProc.exe', path_value)
        if not found or os.path.normcase(found) != os.path.normcase(os.path.abspath(executable)):
            fail('PATH search failed: %s' % found)
        if by3menu_lib.find_on_path('TortoiseProc.exe', tempfile.gettempdir()):
            fail('must not find TortoiseProc outside PATH')
        saved = os.environ.pop('PYTHONIOENCODING', None)
        try:
            env = by3menu_lib.prepare_env({by3menu_lib.SELECTION_ENV: u'鱼'})
        finally:
            if saved is not None:
                os.environ['PYTHONIOENCODING'] = saved
        encoding = env.get('PYTHONIOENCODING')
        if by3menu_lib.is_windows() and encoding != 'mbcs:replace':
            fail('PYTHONIOENCODING %s' % encoding)
        if env.get(by3menu_lib.SELECTION_ENV) != u'鱼':
            fail('selection env lost')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        try:
            env = by3menu_lib.prepare_env(None)
        finally:
            if saved is None:
                os.environ.pop('PYTHONIOENCODING', None)
            else:
                os.environ['PYTHONIOENCODING'] = saved
        if env.get('PYTHONIOENCODING') != 'utf-8':
            fail('must not override PYTHONIOENCODING')
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_cmd_quoting():
    if not by3menu_lib.is_windows():
        return
    py = sys.executable
    code = 'import sys; print(chr(10).join(sys.argv[1:]))'
    command = by3menu_lib.windows_cmd_line([py, '-c', code, 'hello world', 'a&b', u'中文'])
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.read()
    code_num = proc.wait()
    text = output.decode('utf-8', 'replace').replace('\r', '')
    lines = [line for line in text.split('\n') if line]
    if code_num != 0 or lines != ['hello world', 'a&b', '中文']:
        fail('python argv via cmd %s %r' % (code_num, text))

    folder = tempfile.mkdtemp(prefix='by3 menu ')
    try:
        bat = os.path.join(folder, 'run.bat')
        with open(bat, 'w', encoding='ascii', newline='\r\n') as handle:
            handle.write('@echo off\r\necho A=%~1\r\necho B=%~2\r\n')
        command = by3menu_lib.windows_cmd_line([bat, 'hello world', u'表'])
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=folder,
            creationflags=0x08000000,
            startupinfo=startupinfo,
        )
        output = by3menu_lib.to_text(proc.stdout.read())
        code_num = proc.wait()
        lines = [line.strip() for line in output.replace('\r', '').split('\n') if line.strip()]
        if code_num != 0 or lines != ['A=hello world', u'B=表']:
            fail('bat args %s %r' % (code_num, lines))
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_surface_files():
    expected = ui_spec.rendered_files()
    for name, text in expected.items():
        path = os.path.join(ROOT, name)
        if not os.path.isfile(path):
            fail('missing %s' % name)
        with open(path, 'r', encoding='utf-8') as handle:
            actual = handle.read()
        if actual != text:
            fail('%s does not match ui_spec' % name)
    for name in ('Example.sublime-keymap',):
        with open(os.path.join(ROOT, name), 'r', encoding='utf-8') as handle:
            text = handle.read()
        if 'cmd+' in text:
            fail('Sublime uses super, not cmd, in %s' % name)
    for name in (
        'Default.sublime-keymap',
        'Default (Windows).sublime-keymap',
        'Default (Linux).sublime-keymap',
        'Default (OSX).sublime-keymap',
    ):
        if os.path.exists(os.path.join(ROOT, name)):
            fail('%s would enable shortcuts for every user' % name)
    repo_path = os.path.join(ROOT, 'repository.json')
    with open(repo_path, 'r', encoding='utf-8') as handle:
        repo = handle.read()
    if '"name": "By3Menu"' not in repo or '"sublime_text": "*"' not in repo:
        fail('repository.json must publish the name By3Menu for every Sublime version')
    if os.path.exists(os.path.join(ROOT, '.python-version')):
        fail('.python-version would pin a plugin host')
    if os.path.exists(os.path.join(ROOT, 'dependencies.json')):
        fail('dependencies.json is not needed and can restrict the install')
    with open(os.path.join(ROOT, '.gitattributes'), 'r', encoding='utf-8') as handle:
        attributes = handle.read()
    if 'tests/ export-ignore' not in attributes or 'repository.json export-ignore' not in attributes:
        fail('tests and repository.json must stay out of the installed package')
    for action in by3menu_lib.FILE_ACTIONS:
        result = plan(action, file_path=None)
        if result.get('ok'):
            fail('%s should need a file' % action)


def _command_name_py33(class_name):
    name = class_name[0].lower()
    last_upper = False
    for char in class_name[1:]:
        if char.isupper() and not last_upper:
            name += '_'
            name += char.lower()
        else:
            name += char
        last_upper = char.isupper()
    if name.endswith('_command'):
        name = name[:-8]
    return name


def _split_identifier(text):
    parts = []
    part_start = 0
    is_upper = False
    for index, char in enumerate(text):
        if index == part_start:
            is_upper = char.isupper()
        if char.isupper():
            if not is_upper:
                parts.append(text[part_start:index])
                part_start = index
                is_upper = True
        elif char.islower():
            if is_upper and index - part_start > 1:
                parts.append(text[part_start:index - 1])
                part_start = index - 1
            is_upper = False
        else:
            is_upper = False
    if part_start < len(text):
        parts.append(text[part_start:])
    return parts


def _command_name_py314(class_name):
    name = '_'.join(part.lower() for part in _split_identifier(class_name))
    if name.endswith('_command'):
        name = name[:-8]
    return name


def test_command_name_on_both_hosts():
    class_name = 'By3MenuRunCommand'
    old = _command_name_py33(class_name)
    new = _command_name_py314(class_name)
    if old != new or old != by3menu_lib.COMMAND_NAME:
        fail('command name py33=%s py314=%s' % (old, new))


def _forbid_modern_syntax(path):
    with open(path, 'r', encoding='utf-8') as handle:
        source = handle.read()
    tree = ast.parse(source, filename=path)
    banned = (
        ast.JoinedStr, ast.AsyncFunctionDef, ast.YieldFrom, ast.AnnAssign,
        ast.Nonlocal, ast.MatMult,
    )
    if hasattr(ast, 'NamedExpr'):
        banned = banned + (ast.NamedExpr,)
    for node in ast.walk(tree):
        if isinstance(node, banned):
            fail('%s uses syntax older Sublime cannot parse: %s' % (path, type(node).__name__))
        if isinstance(node, ast.Set):
            fail('%s uses a set literal' % path)
        if isinstance(node, (ast.DictComp, ast.SetComp)):
            fail('%s uses a comprehension that Python 2.6 rejects' % path)
        if isinstance(node, ast.FunctionDef):
            if getattr(node, 'returns', None) is not None:
                fail('%s annotates a return' % path)
            for arg in list(node.args.args) + list(getattr(node.args, 'kwonlyargs', []) or []):
                if getattr(arg, 'annotation', None) is not None:
                    fail('%s annotates an argument' % path)


def test_source_is_portable():
    for name in ('By3Menu.py', 'lib/by3menu_lib.py'):
        _forbid_modern_syntax(os.path.join(ROOT, name))
        with open(os.path.join(ROOT, name), 'r', encoding='utf-8') as handle:
            source = handle.read()
        if 'F:\\\\TortoiseSVN' in source or 'Program Files\\TortoiseSVN' in source:
            fail('%s hardcodes TortoiseSVN' % name)
        if not source.startswith('# -*- coding: utf-8 -*-'):
            fail('%s needs a coding cookie for Python 2' % name)


class _Region(object):
    def __init__(self, point):
        self.b = point


class _View(object):
    def file_name(self):
        return BY_FILE

    def sel(self):
        return [_Region(20)]

    def rowcol(self, point):
        return (11, 3)

    def substr(self, region):
        return u'Fish'


class _Panel(object):
    def __init__(self):
        self.chunks = []
        self.read_only = False

    def set_read_only(self, value):
        self.read_only = value

    def run_command(self, name, args):
        if name != 'append':
            fail('unexpected panel command %s' % name)
        self.chunks.append(args['characters'])

    def show(self, point):
        return None

    def size(self):
        return sum(len(chunk) for chunk in self.chunks)


class _Window(object):
    def __init__(self, view, folders):
        self.view = view
        self._folders = folders
        self.panel = _Panel()
        self.panels = []

    def active_view(self):
        return self.view

    def folders(self):
        return self._folders

    def create_output_panel(self, name):
        return self.panel

    def run_command(self, name, args=None):
        self.panels.append((name, args))


class _Proc(object):
    def __init__(self, lines, code):
        self.stdout = self
        self.stdin = self
        self._lines = list(lines)
        self._code = code

    def close(self):
        return None

    def readline(self):
        if self._lines:
            return self._lines.pop(0)
        return b''

    def wait(self):
        return self._code


def _load_plugin():
    sublime = types.ModuleType('sublime')
    plugin = types.ModuleType('sublime_plugin')

    class WindowCommand(object):
        def __init__(self, window=None):
            self.window = window

    plugin.WindowCommand = WindowCommand
    messages = []
    errors = []

    def status_message(text):
        messages.append(text)

    def error_message(text):
        errors.append(text)

    def set_timeout(callback, delay):
        callback()

    sublime.status_message = status_message
    sublime.error_message = error_message
    sublime.set_timeout = set_timeout

    class _Settings(object):
        def get(self, key, default=None):
            if key in sublime._by3_settings:
                return sublime._by3_settings[key]
            return default

    sublime._by3_settings = {'show_context_menu': False}
    sublime.load_settings = lambda name: _Settings()
    sys.modules['sublime'] = sublime
    sys.modules['sublime_plugin'] = plugin
    sys.modules.pop('By3Menu', None)
    sys.modules.pop('lib.by3menu_lib', None)
    sys.modules.pop('lib', None)
    import By3Menu
    return By3Menu, messages, errors


def test_plugin_wires_commands():
    if 'sublime' in sys.modules and not isinstance(sys.modules['sublime'], types.ModuleType):
        fail('sublime module is unexpected')
    module, messages, errors = _load_plugin()
    if module.By3MenuRunCommand.__name__ != 'By3MenuRunCommand':
        fail('class renamed')
    launched = []

    def fake_popen(argv, **kwargs):
        launched.append((argv, kwargs))
        return _Proc([b'pushed\r\n'], 0)

    real_popen = subprocess.Popen
    real_isfile = os.path.isfile
    real_thread = threading.Thread
    real_find = module.by3menu_lib.find_on_path
    subprocess.Popen = fake_popen

    def inline_thread(target=None, args=(), kwargs=None):
        class Runner(object):
            def start(self):
                target()

        return Runner()

    threading.Thread = inline_thread
    try:
        os.path.isfile = lambda path: True
        module.by3menu_lib.find_on_path = lambda name, path_value: r'C:\bin\TortoiseProc.exe'
        window = _Window(_View(), [PROJECT])
        command = module.By3MenuRunCommand(window)
        if command.is_visible(action='push_file', from_context_menu=True):
            fail('context menu stays hidden until the user enables it')
        if not command.is_visible(action='push_file'):
            fail('command palette stays available while the context menu is hidden')
        sys.modules['sublime']._by3_settings['show_context_menu'] = True
        if not command.is_visible(action='push_file', from_context_menu=True):
            fail('context item should show after the user turns it on')
        if module.By3MenuRunCommand(_Window(None, [])).is_visible(action='push_file', from_context_menu=True):
            fail('file item should hide when no file is open')
        command.run(action='svn_blame')
        if len(launched) != 1:
            fail('svn was not launched')
        argv = launched[0][0]
        if argv[0] != r'C:\bin\TortoiseProc.exe':
            fail('svn argv %s' % argv)
        if '/line:12' not in argv or '/closeonend:2' in argv:
            fail('blame argv %s' % argv)
        launched[:] = []
        module.by3menu_lib.find_on_path = lambda name, path_value: None
        command.run(action='svn_diff')
        if not errors or by3menu_lib.MSG_NO_TORTOISE not in errors[-1]:
            fail('missing tortoise message %s' % errors)
        errors[:] = []
        os.path.isfile = lambda path: False
        command.run(action='push_file')
        if not errors or u'找不到脚本' not in errors[-1]:
            fail('missing script message %s' % errors)
        errors[:] = []
        os.path.isfile = lambda path: True
        command.run(action='push_file')
        if not launched:
            fail('bat was not started')
        command_line = launched[-1][0]
        if 'push_lua_file.bat' not in command_line or ' /S /C "' not in command_line:
            fail('bat command %s' % command_line)
        if u'pushed' not in u''.join(window.panel.chunks):
            fail('bat output was not shown')
        real_is_windows = module.by3menu_lib.is_windows
        module.by3menu_lib.is_windows = lambda: False
        command.run(action='push')
        module.by3menu_lib.is_windows = real_is_windows
        if not errors or by3menu_lib.MSG_WINDOWS not in errors[-1]:
            fail('non-windows message')
        empty = module.By3MenuRunCommand(_Window(None, []))
        empty.run(action='back_hall')
        if not messages or messages[-1] != by3menu_lib.MSG_NO_PROJECT:
            fail('no project status %s' % messages)
    finally:
        subprocess.Popen = real_popen
        os.path.isfile = real_isfile
        threading.Thread = real_thread
        module.by3menu_lib.find_on_path = real_find


def test_no_hardcoded_paths_in_repo():
    for name in ('By3Menu.py', 'lib/by3menu_lib.py', 'README.md'):
        with open(os.path.join(ROOT, name), 'r', encoding='utf-8') as handle:
            text = handle.read()
        if 'F:\\TortoiseSVN' in text or 'C:\\Program Files\\TortoiseSVN' in text:
            fail('hardcoded tortoise in %s' % name)


def write_surfaces():
    for name, text in ui_spec.rendered_files().items():
        path = os.path.join(ROOT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)


def main():
    if '--write' in sys.argv:
        write_surfaces()
    tests = [
        test_actions_match_cursor,
        test_names_and_paths,
        test_project_folder,
        test_push_and_hot_args,
        test_lua_config_and_protocol,
        test_svn_args,
        test_path_search_and_env,
        test_cmd_quoting,
        test_surface_files,
        test_command_name_on_both_hosts,
        test_source_is_portable,
        test_plugin_wires_commands,
        test_no_hardcoded_paths_in_repo,
    ]
    for test in tests:
        test()
        print('ok', test.__name__)
    print('all passed')


if __name__ == '__main__':
    main()
