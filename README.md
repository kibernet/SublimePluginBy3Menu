# 快捷键和右键菜单默认关闭

# Key bindings and the context menu are OFF by default

安装后**不会**自动占用快捷键，也**不会**自动加入右键菜单。命令面板搜索 **By3Menu** 可以直接运行全部命令。

需要开启时，请用 Sublime **顶部菜单**，不是 Package Control：

**Preferences → Package Settings → By3Menu**

- **Example Context Menu**：左边是右键菜单示例。把左边整段复制到右边，保存后右键才会出现。
- **Example Key Bindings**：左边是快捷键示例。右边已经是你自己的快捷键文件，只复制要用的几条，不要整段覆盖。

To turn them on, use Sublime's top menu, not Package Control: **Preferences → Package Settings → By3Menu**. Copy **Example Context Menu** into the right-hand file to enable the right-click menu. Copy only the key bindings you want from **Example Key Bindings** into your existing user keymap. Do not replace that file.

# By3Menu

Sublime Text 命令：Push、热更、Lua 配置、协议，以及当前文件的 TortoiseSVN。快捷键与 Cursor / VS Code 的 By3Menu 相同，但默认不启用。

Commands for Push, hot reload, Lua config, protocol scripts, and TortoiseSVN on the current file. The shortcut list matches the Cursor / VS Code By3Menu plugin. Those shortcuts are not installed automatically.

安装后在 Package Control 里搜索 **By3Menu**。不限制 Sublime Text 版本。

## 安装

Package Control：Add Repository，填入：

```text
https://raw.githubusercontent.com/kibernet/SublimePluginBy3Menu/main/repository.json
```

然后 Install Package，搜索 `By3Menu`。

这个地址要等本仓库推送到 GitHub，并且打过版本标签（例如 `1.0.0`）之后才能装到。标签不要写成 `st4-` 这种带版本前缀的名字，否则会把一部分 Sublime 排除掉。

本机调试可以把这个目录放到 Sublime 的 Packages 里，文件夹名用 `By3Menu`：

```text
%AppData%\Sublime Text\Packages\By3Menu
```

## 依赖

菜单里的 Push、热更、导表、协议会运行当前工程里的 bat，例如 `tools/idea_tools`、`tools/format_protocal`、`pack/windows`。请用工程根目录作为 Sublime 打开的文件夹。

SVN 只从环境变量 Path 里找 `TortoiseProc.exe`，不写死安装路径。找不到时会提示把 TortoiseSVN 的 bin 目录加入 Path，然后重新启动 Sublime Text。

## 快捷键列表

下面这些键默认不生效。开启方法见本文第一段。

| 命令 | Windows / Linux | macOS |
|---|---|---|
| PushFile | Ctrl+Shift+P | Command+Shift+P |
| PushAppendFile | Ctrl+Shift+A | Command+Shift+A |
| HotReloadLuaFile | Ctrl+Shift+L | Command+Shift+L |
| LuaModelFuncTest | Ctrl+Shift+T | Command+Shift+T |
| ReEnterFishing | Ctrl+Shift+I | Command+Shift+I |
| RefreshFishingFish | Ctrl+Shift+S | Command+Shift+S |
| BackToHall | Ctrl+Shift+H | Command+Shift+H |
| OpenExcelSheetConfig | Ctrl+Shift+O | Ctrl+Shift+O |
| SvnUpdate | Alt+U | Alt+U |
| SvnLog | Alt+L | Alt+L |
| SvnCommit | Alt+C | Alt+C |
| SvnBlame | Alt+B | Alt+B |
| SvnDiff | Alt+D | Alt+D |
| SvnUpdateRoot | Alt+Shift+U | Alt+Shift+U |
| SvnLogRoot | Alt+Shift+L | Alt+Shift+L |
| SvnCommitRoot | Alt+Shift+C | Alt+Shift+C |
| SvnUpdateDir | Ctrl+Alt+U | Ctrl+Alt+U |
| SvnLogDir | Ctrl+Alt+L | Ctrl+Alt+L |
| SvnCommitDir | Ctrl+Alt+C | Ctrl+Alt+C |
| SvnMerge | Alt+M | Alt+M |

其余命令在命令面板里搜索 `By3Menu`。右键菜单要按第一段自己打开后才会有。
