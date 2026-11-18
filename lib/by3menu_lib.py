# -*- coding: utf-8 -*-
"""By3Menu 的纯逻辑。不 import sublime，方便在 Sublime 外对一下 Cursor 插件的行为。"""
import os
import sys

VERSION = '1.0.7'
COMMAND_NAME = 'by3_menu_run'
TORTOISE_EXE = 'TortoiseProc.exe'
SELECTION_ENV = 'BY3MENU_SELECTION'
SELECTION_LIMIT = 30000

MSG_NO_PROJECT = u'请先打开工作区'
MSG_NO_FILE = u'请先打开一个文件'
MSG_NO_SHEET = u'请先打开一个配置 lua 文件'
MSG_NO_PROJECT_KIND = u'无法从路径判断项目，请打开 dev/by 或 dev/xm 下的配置 lua 文件'
MSG_NO_TORTOISE = u'找不到 TortoiseProc.exe。请把 TortoiseSVN 的 bin 目录加入环境变量 Path，然后重新启动 Sublime Text。'
MSG_NO_SCRIPT = u'找不到脚本：%s'
MSG_WINDOWS = u'By3Menu 的脚本和 TortoiseSVN 需要在 Windows 上运行。'
MSG_UNKNOWN = u'未知命令：%s'
MSG_TRUNCATED = u'选中文本过长，已截断后传给 OpenExcelSheetConfig。'

PUSH_BAT = ('tools', 'idea_tools', 'push_lua_file.bat')
UPDATE_BAT = ('tools', 'idea_tools', 'update_lua_config.bat')
PRINT_BAT = ('tools', 'idea_tools', 'print_sheet_excel_name.bat')
OPEN_BAT = ('tools', 'idea_tools', 'open_excel_sheet.bat')
HOT_BAT = ('tools', 'idea_tools', 'hot_reload_lua_file.bat')
DECRYPT_BAT = ('pack', 'windows', 'decrypt_cache_lua_config.bat')
FORMAT_BAT = ('tools', 'format_protocal', 'format_protocal.bat')
UPDATE_PROTOCOL_BAT = ('tools', 'format_protocal', 'update_protocal.bat')
SCRIPT_MARK = ('tools', 'idea_tools', 'push_lua_file.bat')


def is_windows():
    return os.name == 'nt'


def to_text(value):
    if value is None:
        return u''
    if isinstance(value, type(u'')):
        return value
    if isinstance(value, bytes):
        encodings = ('mbcs', 'gbk', 'utf-8') if is_windows() else ('utf-8',)
        for encoding in encodings:
            try:
                return value.decode(encoding)
            except Exception:
                continue
        return value.decode('utf-8', 'replace')
    return type(u'')(value)


def to_native(value):
    """subprocess 在 Python 2 的 Windows 上要字节串，Python 3 要 str。"""
    if value is None:
        value = u''
    if sys.version_info[0] >= 3:
        if isinstance(value, bytes):
            return to_text(value)
        return value
    if isinstance(value, type(u'')):
        encoding = 'mbcs' if is_windows() else 'utf-8'
        return value.encode(encoding, 'replace')
    return value


def exc_text(exc):
    try:
        return to_text(str(exc))
    except Exception:
        return u'unknown error'


def sheet_name(file_path):
    file_name = os.path.basename(file_path)
    if file_name.endswith('.lua.txt'):
        return file_name[:-len('.lua.txt')]
    if file_name.endswith('.lua'):
        return file_name[:-len('.lua')]
    root, _ext = os.path.splitext(file_name)
    return root


def config_project(file_path):
    normalized = file_path.replace('\\', '/').lower()
    if '/dev/by/' in normalized or '/emmyluaclass/by/' in normalized:
        return 'by'
    if '/dev/xm/' in normalized or '/emmyluaclass/xm/' in normalized:
        return 'xm'
    return None


def clean_selection(selection):
    text = to_text(selection).replace(u'\x00', u'')
    if len(text) > SELECTION_LIMIT:
        return text[:SELECTION_LIMIT], True
    return text, False


def _realpath(path):
    return os.path.normcase(os.path.normpath(os.path.realpath(path)))


def _is_inside(child, parent):
    child_path = _realpath(child)
    parent_path = _realpath(parent)
    if child_path == parent_path:
        return True
    prefix = parent_path if parent_path.endswith(os.sep) else parent_path + os.sep
    return child_path.startswith(prefix)


def _has_scripts(folder):
    return os.path.isfile(os.path.join(folder, *SCRIPT_MARK))


def discover_project(file_path):
    """没把文件夹加进 Sublime 时，从当前文件向上找带 tools/idea_tools 的工程根。"""
    if not file_path:
        return None
    directory = os.path.dirname(os.path.abspath(file_path))
    previous = None
    while directory and directory != previous:
        if _has_scripts(directory):
            return directory
        previous = directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def project_folder_for(folders, file_path):
    """选出工程根目录。多目录时优先带 tools/idea_tools 的最外层目录。"""
    if not folders:
        return None
    opened = []
    for folder in folders:
        if folder:
            opened.append(os.path.abspath(folder))
    if not opened:
        return None
    containing = []
    if file_path:
        for folder in opened:
            if _is_inside(file_path, folder):
                containing.append(folder)
    if not containing:
        return opened[0]
    with_scripts = [folder for folder in containing if _has_scripts(folder)]
    pool = with_scripts or containing
    pool.sort(key=len)
    return pool[0]


def _rel(project, path):
    project_abs = os.path.abspath(project)
    path_abs = os.path.abspath(path)
    try:
        relative = os.path.relpath(path_abs, project_abs)
    except ValueError:
        return path_abs
    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        return path_abs
    return relative


def script_path(project, parts):
    return os.path.normpath(os.path.join(project, *parts))


def _err(message):
    return {'ok': False, 'message': message}


def _bat(title, parts, args, env=None, notice=None):
    result = {
        'ok': True,
        'kind': 'bat',
        'title': title,
        'script': parts,
        'args': list(args),
        'env': env,
    }
    if notice:
        result['notice'] = notice
    return result


def _svn(title, args):
    return {
        'ok': True,
        'kind': 'svn',
        'title': title,
        'args': list(args),
    }


def _need_project(project):
    if not project:
        return _err(MSG_NO_PROJECT)
    return None


def _need_file(project, file_path, message=None):
    error = _need_project(project)
    if error:
        return error
    if not file_path:
        return _err(message or MSG_NO_FILE)
    return None


def _line_text(line):
    try:
        number = int(line)
    except (TypeError, ValueError):
        number = 1
    if number < 1:
        number = 1
    return str(number)


def action_id(action):
    """Python 2 下 Sublime 可能传入 unicode，字典键是 byte str。"""
    text = to_text(action).strip()
    if sys.version_info[0] < 3 and isinstance(text, type(u'')):
        try:
            return text.encode('ascii')
        except Exception:
            return text
    return text


def plan(action, project, file_path, line, selection):
    if project:
        project = os.path.abspath(project)
    if file_path:
        file_path = os.path.abspath(file_path)
    handler = HANDLERS.get(action_id(action))
    if handler is None:
        return _err(MSG_UNKNOWN % to_text(action))
    return handler(project, file_path, line, selection)


def _push_file(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _bat(u'PushFile', PUSH_BAT, [_rel(project, file_path)])


def _push_append_file(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _bat(u'PushAppendFile', PUSH_BAT, [_rel(project, file_path), 'append'])


def _push_dir(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _bat(u'PushDir', PUSH_BAT, [_rel(project, os.path.dirname(file_path))])


def _push_append_dir(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _bat(u'PushAppendDir', PUSH_BAT, [_rel(project, os.path.dirname(file_path)), 'append'])


def _push(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'Push', ('tools', 'idea_tools', 'push.bat'), [])


def _update_lua(project, file_path, line, selection, name):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'UpdateLuaConfig ' + name, UPDATE_BAT, [project, 'full', name])


def _update_lua_by(project, file_path, line, selection):
    return _update_lua(project, file_path, line, selection, 'by')


def _update_lua_xm(project, file_path, line, selection):
    return _update_lua(project, file_path, line, selection, 'xm')


def _update_lua_all(project, file_path, line, selection):
    return _update_lua(project, file_path, line, selection, 'all')


def _update_named(project, file_path, line, selection, mode, title):
    error = _need_file(project, file_path, MSG_NO_SHEET)
    if error:
        return error
    kind = config_project(file_path)
    if not kind:
        return _err(MSG_NO_PROJECT_KIND)
    return _bat(title, UPDATE_BAT, [project, mode, sheet_name(file_path), kind])


def _update_sheet(project, file_path, line, selection):
    return _update_named(project, file_path, line, selection, 'sheet', u'UpdateSheetLuaConfig')


def _update_excel(project, file_path, line, selection):
    return _update_named(project, file_path, line, selection, 'excel', u'UpdateExcelLuaConfig')


def _decrypt(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'DecryptCacheLuaConfig', DECRYPT_BAT, ['1'])


def _open_excel(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    text, truncated = clean_selection(selection)
    args = ['--root', project]
    if file_path:
        args.extend(['--file', file_path])
    return _bat(
        u'OpenExcelSheetConfig',
        OPEN_BAT,
        args,
        {SELECTION_ENV: text},
        MSG_TRUNCATED if truncated else None,
    )


def _print_name(project, file_path, line, selection, name):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'PrintExcelSheetName ' + name, PRINT_BAT, [project, name])


def _print_by(project, file_path, line, selection):
    return _print_name(project, file_path, line, selection, 'by')


def _print_xm(project, file_path, line, selection):
    return _print_name(project, file_path, line, selection, 'xm')


def _print_all(project, file_path, line, selection):
    return _print_name(project, file_path, line, selection, 'all')


def _hot(project, file_path, line, selection, title, args):
    error = _need_file(project, file_path)
    if error:
        return error
    return _bat(title, HOT_BAT, args)


def _hot_reload(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _hot(
        project, file_path, line, selection, u'HotReloadLuaFile',
        ['event_name', 'reload_lua_file', 'lua_file_path', _rel(project, file_path)],
    )


def _lua_test(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _hot(
        project, file_path, line, selection, u'LuaModelFuncTest',
        ['event_name', 'lua_test_func', 'lua_file_path', _rel(project, file_path), 'func_name', 'test'],
    )


def _hot_event(project, file_path, line, selection, title, event):
    error = _need_project(project)
    if error:
        return error
    return _bat(title, HOT_BAT, ['event_name', event])


def _reenter(project, file_path, line, selection):
    return _hot_event(project, file_path, line, selection, u'ReEnterFishing', 'enter_new_fishing')


def _refresh_fish(project, file_path, line, selection):
    return _hot_event(project, file_path, line, selection, u'RefreshFishingFish', 'refresh_fishing_fish')


def _back_hall(project, file_path, line, selection):
    return _hot_event(project, file_path, line, selection, u'BackToHall', 'back_to_hall')


def _format_protocal(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'FormatProtocal', FORMAT_BAT, ['1'])


def _update_protocol(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _bat(u'UpdateProtocol', UPDATE_PROTOCOL_BAT, ['1'])


def _svn_update(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnUpdate', ['/command:update', '/path:' + file_path, '/closeonend:2'])


def _svn_log(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnLog', ['/command:log', '/path:' + file_path])


def _svn_commit(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnCommit', ['/command:commit', '/path:' + file_path])


def _svn_blame(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnBlame', [
        '/command:blame', '/path:' + file_path, '/statrev:1', '/endrev:-1', '/line:' + _line_text(line),
    ])


def _svn_diff(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnDiff', ['/command:diff', '/path:' + file_path])


def _svn_update_root(project, file_path, line, selection):
    # Cursor 的根目录更新不带 /closeonend，更新窗口会留着。
    error = _need_project(project)
    if error:
        return error
    return _svn(u'SvnUpdateRoot', ['/command:update', '/path:' + project])


def _svn_log_root(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _svn(u'SvnLogRoot', ['/command:log', '/path:' + project])


def _svn_commit_root(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _svn(u'SvnCommitRoot', ['/command:commit', '/path:' + project])


def _svn_update_dir(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnUpdateDir', ['/command:update', '/path:' + os.path.dirname(file_path), '/closeonend:2'])


def _svn_log_dir(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnLogDir', ['/command:log', '/path:' + os.path.dirname(file_path)])


def _svn_commit_dir(project, file_path, line, selection):
    error = _need_file(project, file_path)
    if error:
        return error
    return _svn(u'SvnCommitDir', ['/command:commit', '/path:' + os.path.dirname(file_path)])


def _svn_merge(project, file_path, line, selection):
    error = _need_project(project)
    if error:
        return error
    return _svn(u'SvnMerge', ['/command:merge', '/path:' + os.path.join(project, 'Assets')])


def _register(pairs):
    handlers = {}
    order = []
    for action, handler in pairs:
        if action in handlers:
            raise RuntimeError('duplicate action ' + action)
        handlers[action] = handler
        order.append(action)
    return handlers, tuple(order)


HANDLERS, ACTION_ORDER = _register((
    ('push_file', _push_file),
    ('push_append_file', _push_append_file),
    ('push_dir', _push_dir),
    ('push_append_dir', _push_append_dir),
    ('push', _push),
    ('update_lua_by', _update_lua_by),
    ('update_lua_xm', _update_lua_xm),
    ('update_lua_all', _update_lua_all),
    ('update_sheet', _update_sheet),
    ('update_excel', _update_excel),
    ('decrypt', _decrypt),
    ('open_excel', _open_excel),
    ('print_by', _print_by),
    ('print_xm', _print_xm),
    ('print_all', _print_all),
    ('hot_reload', _hot_reload),
    ('lua_test', _lua_test),
    ('reenter', _reenter),
    ('refresh_fish', _refresh_fish),
    ('back_hall', _back_hall),
    ('update_protocol', _update_protocol),
    ('format_protocal', _format_protocal),
    ('svn_update', _svn_update),
    ('svn_log', _svn_log),
    ('svn_commit', _svn_commit),
    ('svn_blame', _svn_blame),
    ('svn_diff', _svn_diff),
    ('svn_update_root', _svn_update_root),
    ('svn_log_root', _svn_log_root),
    ('svn_commit_root', _svn_commit_root),
    ('svn_update_dir', _svn_update_dir),
    ('svn_log_dir', _svn_log_dir),
    ('svn_commit_dir', _svn_commit_dir),
    ('svn_merge', _svn_merge),
))


FILE_ACTIONS = (
    'push_file',
    'push_append_file',
    'push_dir',
    'push_append_dir',
    'update_sheet',
    'update_excel',
    'hot_reload',
    'lua_test',
    'svn_update',
    'svn_log',
    'svn_commit',
    'svn_blame',
    'svn_diff',
    'svn_update_dir',
    'svn_log_dir',
    'svn_commit_dir',
)


def known_actions():
    return ACTION_ORDER


def find_on_path(file_name, path_value):
    """只在 PATH 里找可执行文件，不写死盘符。"""
    if not path_value or not file_name:
        return None
    for directory in path_value.split(os.pathsep):
        directory = directory.strip().strip('"')
        if not directory:
            continue
        candidate = os.path.join(directory, file_name)
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


def windows_cmd_line(args, comspec=None):
    """每个参数都加引号，再交给 cmd /S /C。

    /S 会剥掉最外层一对引号。list2cmdline 不会给 & 加引号，cmd 会把它当成命令分隔符。
    """
    pieces = [_quote_cmd_arg(arg) for arg in args]
    if sys.version_info[0] < 3:
        inner = b' '.join(to_native(piece) for piece in pieces)
    else:
        inner = ' '.join(pieces)
    spec = comspec or os.environ.get('COMSPEC') or 'cmd.exe'
    spec = to_native(spec)
    if b' ' in spec if isinstance(spec, bytes) else (' ' in spec):
        if isinstance(spec, bytes):
            spec = b'"' + spec + b'"'
        else:
            spec = '"' + spec + '"'
    if isinstance(spec, bytes):
        return spec + b' /S /C "' + inner + b'"'
    return spec + ' /S /C "' + inner + '"'


def _quote_cmd_arg(arg):
    text = to_text(arg).replace(u'"', u'""')
    quoted = u'"' + text + u'"'
    return to_native(quoted) if sys.version_info[0] < 3 else quoted


def prepare_env(extra):
    env = {}
    for key, value in os.environ.items():
        env[to_native(key)] = to_native(value)
    # cmd.exe 的输出是系统 ANSI 代码页。管道不是控制台时，Python 可能改用 UTF-8，
    # 和 bat 里的 echo 混在一起就会乱码。没人指定时，让子进程跟 cmd 用同一套编码。
    if is_windows() and not _env_has(env, 'PYTHONIOENCODING'):
        env[to_native('PYTHONIOENCODING')] = to_native('mbcs:replace')
    if extra:
        for key, value in extra.items():
            env[to_native(key)] = to_native(value)
    return env


def _env_has(env, name):
    if name in env:
        return True
    native = to_native(name)
    if native in env:
        return True
    return False
