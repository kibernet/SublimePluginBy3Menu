# -*- coding: utf-8 -*-
"""右键菜单、命令面板、快捷键的唯一描述。测试用它生成并核对 Sublime 文件。"""
import json

COMMAND = 'by3_menu_run'

EDITOR_CONTEXT = [
    {'key': 'setting.is_widget', 'operator': 'equal', 'operand': False},
    {'key': 'overlay_visible', 'operator': 'equal', 'operand': False},
]
GLOBAL_CONTEXT = [
    {'key': 'overlay_visible', 'operator': 'equal', 'operand': False},
]


def cmd(caption, action, palette=None):
    return {
        'type': 'cmd',
        'caption': caption,
        'action': action,
        'palette': palette or ('By3Menu: ' + caption),
    }


def sep():
    return {'type': 'sep'}


def group(caption, children):
    return {'type': 'group', 'caption': caption, 'children': children}


MENU = [
    sep(),
    group('PushFile', [
        cmd('PushFile', 'push_file'),
        cmd('PushAppendFile', 'push_append_file'),
        sep(),
        cmd('PushDir', 'push_dir'),
        cmd('PushAppendDir', 'push_append_dir'),
        sep(),
        cmd('Push', 'push'),
    ]),
    group('HotReload', [
        cmd('HotReloadLuaFile', 'hot_reload'),
        cmd('LuaModelFuncTest', 'lua_test'),
        sep(),
        cmd('ReEnterFishing', 'reenter'),
        cmd('RefreshFishingFish', 'refresh_fish'),
        sep(),
        cmd('BackToHall', 'back_hall'),
    ]),
    group('LuaConfig', [
        group('UpdateLuaConfig', [
            cmd('by', 'update_lua_by', 'By3Menu: UpdateLuaConfig by'),
            cmd('xm', 'update_lua_xm', 'By3Menu: UpdateLuaConfig xm'),
            cmd('all', 'update_lua_all', 'By3Menu: UpdateLuaConfig all'),
        ]),
        cmd('UpdateSheetLuaConfig', 'update_sheet'),
        cmd('UpdateExcelLuaConfig', 'update_excel'),
        cmd('DecryptCacheLuaConfig', 'decrypt'),
        cmd('OpenExcelSheetConfig', 'open_excel'),
        group('PrintExcelSheetName', [
            cmd('by', 'print_by', 'By3Menu: PrintExcelSheetName by'),
            cmd('xm', 'print_xm', 'By3Menu: PrintExcelSheetName xm'),
            cmd('all', 'print_all', 'By3Menu: PrintExcelSheetName all'),
        ]),
    ]),
    group('Protocal', [
        cmd('UpdateProtocol', 'update_protocol'),
        cmd('FormatProtocal', 'format_protocal'),
    ]),
    group('Svn', [
        cmd('SvnUpdate', 'svn_update'),
        cmd('SvnLog', 'svn_log'),
        cmd('SvnCommit', 'svn_commit'),
        cmd('SvnBlame', 'svn_blame'),
        cmd('SvnDiff', 'svn_diff'),
        sep(),
        cmd('SvnUpdateRoot', 'svn_update_root'),
        cmd('SvnLogRoot', 'svn_log_root'),
        cmd('SvnCommitRoot', 'svn_commit_root'),
        sep(),
        cmd('SvnUpdateDir', 'svn_update_dir'),
        cmd('SvnLogDir', 'svn_log_dir'),
        cmd('SvnCommitDir', 'svn_commit_dir'),
        sep(),
        cmd('SvnMerge', 'svn_merge'),
    ]),
    sep(),
]

# win_key, mac_key, editor_focus。mac 与 Cursor 的 package.json 一致：
# Ctrl+Shift 的那几条在 mac 上是 Command+Shift，OpenExcel 和 Ctrl+Alt 保持 Ctrl。
KEYS = [
    ('push_file', 'ctrl+shift+p', 'super+shift+p', True),
    ('push_append_file', 'ctrl+shift+a', 'super+shift+a', True),
    ('hot_reload', 'ctrl+shift+l', 'super+shift+l', True),
    ('lua_test', 'ctrl+shift+t', 'super+shift+t', True),
    ('reenter', 'ctrl+shift+i', 'super+shift+i', False),
    ('refresh_fish', 'ctrl+shift+s', 'super+shift+s', False),
    ('back_hall', 'ctrl+shift+h', 'super+shift+h', False),
    ('svn_update', 'alt+u', 'alt+u', True),
    ('svn_log', 'alt+l', 'alt+l', True),
    ('svn_commit', 'alt+c', 'alt+c', True),
    ('svn_blame', 'alt+b', 'alt+b', True),
    ('svn_diff', 'alt+d', 'alt+d', True),
    ('svn_update_root', 'alt+shift+u', 'alt+shift+u', False),
    ('svn_log_root', 'alt+shift+l', 'alt+shift+l', False),
    ('svn_commit_root', 'alt+shift+c', 'alt+shift+c', False),
    ('svn_update_dir', 'ctrl+alt+u', 'ctrl+alt+u', True),
    ('svn_log_dir', 'ctrl+alt+l', 'ctrl+alt+l', True),
    ('svn_commit_dir', 'ctrl+alt+c', 'ctrl+alt+c', True),
    ('svn_merge', 'alt+m', 'alt+m', False),
    ('open_excel', 'ctrl+shift+o', 'ctrl+shift+o', False),
]


def walk_commands(nodes):
    found = []
    for node in nodes:
        kind = node['type']
        if kind == 'sep':
            continue
        if kind == 'group':
            found.extend(walk_commands(node['children']))
            continue
        found.append(node)
    return found


def _menu_node(node):
    if node['type'] == 'sep':
        return {'caption': '-'}
    if node['type'] == 'group':
        return {
            'caption': node['caption'],
            'children': [_menu_node(child) for child in node['children']],
        }
    return {
        'caption': node['caption'],
        'command': COMMAND,
        'args': {'action': node['action'], 'from_context_menu': True},
    }


def render_menu():
    return json.dumps([_menu_node(node) for node in MENU], indent=2, ensure_ascii=True) + '\n'


def preference_commands():
    return [
        {
            'caption': 'Preferences: By3Menu Settings',
            'command': 'edit_settings',
            'args': {
                'base_file': '${packages}/By3Menu/By3Menu.sublime-settings',
                'default': '{\n\t"show_context_menu": true\n}\n',
            },
        },
        {
            'caption': 'Preferences: By3Menu Key Bindings',
            'command': 'edit_settings',
            'args': {
                'base_file': '${packages}/By3Menu/Default (${platform}).sublime-keymap',
                'default': '[\n\t$0\n]\n',
            },
        },
    ]


def render_commands():
    entries = []
    for node in walk_commands(MENU):
        entries.append({
            'caption': node['palette'],
            'command': COMMAND,
            'args': {'action': node['action']},
        })
    entries.extend(preference_commands())
    return json.dumps(entries, indent=2, ensure_ascii=True) + '\n'


def render_main_menu():
    prefs = preference_commands()
    menu = [{
        'caption': 'Preferences',
        'mnemonic': 'n',
        'id': 'preferences',
        'children': [{
            'caption': 'Package Settings',
            'mnemonic': 'P',
            'id': 'package-settings',
            'children': [{
                'caption': 'By3Menu',
                'children': [
                    {
                        'caption': 'Settings',
                        'command': prefs[0]['command'],
                        'args': prefs[0]['args'],
                    },
                    {
                        'caption': 'Key Bindings',
                        'command': prefs[1]['command'],
                        'args': prefs[1]['args'],
                    },
                ],
            }],
        }],
    }]
    return json.dumps(menu, indent=2, ensure_ascii=True) + '\n'


def _binding(action, keys, editor_focus):
    return {
        'keys': [keys],
        'command': COMMAND,
        'args': {'action': action},
        'context': EDITOR_CONTEXT if editor_focus else GLOBAL_CONTEXT,
    }


def render_keymap(mac):
    bindings = []
    for action, win_key, mac_key, editor_focus in KEYS:
        bindings.append(_binding(action, mac_key if mac else win_key, editor_focus))
    return json.dumps(bindings, indent=2, ensure_ascii=True) + '\n'


def rendered_files():
    return {
        'Context.sublime-menu': render_menu(),
        'Default.sublime-commands': render_commands(),
        'Default (Windows).sublime-keymap': render_keymap(False),
        'Default (Linux).sublime-keymap': render_keymap(False),
        'Default (OSX).sublime-keymap': render_keymap(True),
        'Main.sublime-menu': render_main_menu(),
    }
