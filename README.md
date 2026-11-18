# By3Menu

Editor context menu for one game project. It runs the project's push, hot-reload, Lua config, and protocol scripts, and opens TortoiseSVN for the current file. Shortcuts match the Cursor / VS Code By3Menu plugin.

Sublime Text 右键菜单，和 Cursor / VS Code 里的 By3Menu 一致：PushFile、HotReload、LuaConfig、Protocal、Svn。

安装后在 Package Control 里搜索 **By3Menu**。`repository.json` 的 `sublime_text` 是 `*`，不限制 Sublime Text 版本。

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

## 快捷键示例

这些快捷键和 Cursor 里的 By3Menu 相同，但安装后不会自动生效。从上面的 Example Key Bindings 复制到自己的快捷键文件后才会生效。命令面板搜索 `By3Menu` 可以直接运行命令。

编辑器里的快捷键默认不生效，避免盖住 Sublime 自己的快捷键。打开 Preferences → Package Settings → By3Menu → Example Key Bindings，左边是示例，右边是你自己的快捷键文件，把要用的几条复制过去即可。右键菜单一直都在。把 `show_context_menu` 设为 `false` 会藏起右键菜单。

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

其余命令在右键菜单和命令面板里，搜索 `By3Menu`。
