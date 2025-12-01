#!/usr/bin/env python3
"""
DeepSeek V3.2-Speciale CLI
临时测试版本，有效期至 2025-12-15
"""

import os
import sys
import json
import select
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: pip install openai")
    sys.exit(1)

# V3.2-Speciale 专用配置
BASE_URL = "https://api.deepseek.com/v3.2_speciale_expires_on_20251215"
MODEL = "deepseek-reasoner"

HISTORY_DIR = Path.home() / ".local" / "share" / "deepseek-speciale" / "sessions"
CONFIG_FILE = Path.home() / ".config" / "deepseek-speciale" / "config.json"

class Colors:
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

LANG = {
    "zh": {
        "title": "DeepSeek V3.2-Speciale",
        "subtitle": "临时测试版 | 有效期至 2025-12-15",
        "new_chat": "新建对话",
        "history": "历史对话",
        "delete": "删除历史",
        "select": "请选择",
        "invalid": "无效选择",
        "new_created": "新对话已创建",
        "loaded": "已加载 ({n} 条消息)",
        "help_hint": "输入 'help' 查看命令",
        "goodbye": "再见!",
        "saved": "已保存",
        "cleared": "已清空",
        "thinking_on": "思考显示: 开",
        "thinking_off": "思考显示: 关",
        "no_thinking": "暂无思考记录",
        "thinking": "思考中...",
        "answer": "回答",
        "error": "错误",
        "enter_api_key": "请输入 DeepSeek API Key",
        "get_key_hint": "获取: https://platform.deepseek.com",
        "config_saved": "已保存!",
        "today": "今天",
        "yesterday": "昨天",
        "messages": "条",
        "commands": "命令",
        "lang_switched": "已切换为中文",
        "paste_tip": "支持直接粘贴多行文本",
        "file_loaded": "已读取文件",
        "file_not_found": "文件不存在",
    },
    "en": {
        "title": "DeepSeek V3.2-Speciale",
        "subtitle": "Temporary | Expires 2025-12-15",
        "new_chat": "New Chat",
        "history": "History",
        "delete": "Delete",
        "select": "Select",
        "invalid": "Invalid",
        "new_created": "New chat created",
        "loaded": "Loaded ({n} messages)",
        "help_hint": "Type 'help' for commands",
        "goodbye": "Goodbye!",
        "saved": "Saved",
        "cleared": "Cleared",
        "thinking_on": "Thinking: ON",
        "thinking_off": "Thinking: OFF",
        "no_thinking": "No thinking record",
        "thinking": "Thinking...",
        "answer": "Answer",
        "error": "Error",
        "enter_api_key": "Enter DeepSeek API Key",
        "get_key_hint": "Get it: https://platform.deepseek.com",
        "config_saved": "Saved!",
        "today": "Today",
        "yesterday": "Yesterday",
        "messages": "msgs",
        "commands": "Commands",
        "lang_switched": "Switched to English",
        "paste_tip": "Multi-line paste supported",
        "file_loaded": "File loaded",
        "file_not_found": "File not found",
    }
}

current_lang = "zh"

def t(key):
    return LANG[current_lang].get(key, key)

def p(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

def read_all_input(first_line):
    """读取所有粘贴的内容（自动检测多行粘贴）"""
    lines = [first_line]
    while True:
        if select.select([sys.stdin], [], [], 0.03)[0]:
            try:
                line = sys.stdin.readline()
                if line:
                    lines.append(line.rstrip('\n'))
                else:
                    break
            except:
                break
        else:
            break

    # 如果检测到多行，等待用户确认或继续输入
    if len(lines) > 1:
        print(f"{Colors.DIM}已读取 {len(lines)} 行，按 Enter 发送或继续输入...{Colors.RESET}")
        while True:
            if select.select([sys.stdin], [], [], 0.05)[0]:
                try:
                    line = sys.stdin.readline().rstrip('\n')
                    if line:
                        lines.append(line)
                    else:
                        break
                except:
                    break
            else:
                try:
                    line = input().rstrip('\n')
                    if line:
                        lines.append(line)
                    else:
                        break
                except:
                    break

    return '\n'.join(lines)

def load_config():
    config = {"api_key": os.environ.get("DEEPSEEK_API_KEY", ""), "lang": "zh"}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                fc = json.load(f)
                if not config["api_key"]:
                    config["api_key"] = fc.get("api_key", "")
                config["lang"] = fc.get("lang", "zh")
        except: pass
    return config

def save_config(config):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def get_sessions():
    ensure_dir()
    files = list(HISTORY_DIR.glob("*.json"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files

def load_session(fp):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            d = json.load(f)
            return d.get('messages', []), d.get('title', '')
    except: return [], ''

def save_session(fp, msgs, title=None):
    ensure_dir()
    if not title:
        for m in msgs:
            if m['role'] == 'user':
                title = m['content'][:30] + ('...' if len(m['content']) > 30 else '')
                break
    data = {'title': title or t('new_chat'), 'updated_at': datetime.now().isoformat(), 'messages': msgs}
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_time(ts):
    try:
        dt = datetime.fromisoformat(ts)
        now = datetime.now()
        if dt.date() == now.date(): return f"{t('today')} {dt.strftime('%H:%M')}"
        elif (now - dt).days == 1: return f"{t('yesterday')} {dt.strftime('%H:%M')}"
        else: return dt.strftime('%m-%d %H:%M')
    except: return ""

def menu(config):
    files = get_sessions()
    p("=" * 50, Colors.CYAN)
    p(f"  {t('title')}", Colors.CYAN + Colors.BOLD)
    p(f"  {t('subtitle')}", Colors.YELLOW)
    p("=" * 50, Colors.CYAN)
    print()
    p(f"  [0] {t('new_chat')}", Colors.GREEN)

    if files:
        p(f"\n  {t('history')}:", Colors.CYAN)
        for i, f in enumerate(files[:9], 1):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    d = json.load(fp)
                    title = d.get('title', '')[:35]
                    time_str = format_time(d.get('updated_at', ''))
                    n = len(d.get('messages', []))
                    print(f"  {Colors.YELLOW}[{i}]{Colors.RESET} {title}")
                    print(f"      {Colors.DIM}{time_str} | {n}{t('messages')}{Colors.RESET}")
            except:
                print(f"  {Colors.YELLOW}[{i}]{Colors.RESET} {f.stem}")

    print()
    p(f"  [d] {t('delete')}", Colors.DIM)
    print()

    while True:
        try:
            c = input(f"{Colors.GREEN}{t('select')} [0-{min(len(files),9)}]: {Colors.RESET}").strip()
            if c in ['0', '']:
                fp = HISTORY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                return fp, [], True
            if c.lower() == 'd':
                if files:
                    p("Enter numbers (space separated) or 'all':", Colors.YELLOW)
                    dc = input(f"{Colors.RED}> {Colors.RESET}").strip()
                    if dc.lower() == 'all':
                        for f in files: f.unlink()
                    else:
                        for i in [int(x) for x in dc.split() if x.isdigit()]:
                            if 1 <= i <= len(files): files[i-1].unlink()
                return menu(config)
            idx = int(c)
            if 1 <= idx <= min(len(files), 9):
                fp = files[idx-1]
                msgs, _ = load_session(fp)
                return fp, msgs, False
            p(t('invalid'), Colors.RED)
        except ValueError:
            p(t('invalid'), Colors.RED)
        except (KeyboardInterrupt, EOFError):
            print(); sys.exit(0)

def help_cmd():
    p(f"{t('commands')}:", Colors.CYAN)
    cmds = [
        ("q/exit", "Exit"), ("clear", "Clear chat"), ("think", "Toggle thinking"),
        ("show", "Show thinking"), ("new", "New chat"), ("sessions", "Session menu"),
        ("lang", "Switch language"), ("file <path>", "Send file content"), ("help", "Help")
    ]
    for c, d in cmds:
        p(f"  {c:12} {d}", Colors.DIM)
    print()

def main():
    global current_lang
    config = load_config()
    current_lang = config.get("lang", "zh")

    if not config["api_key"]:
        p("=" * 50, Colors.CYAN)
        p(f"  {t('title')}", Colors.CYAN)
        p("=" * 50, Colors.CYAN)
        print()
        p(t('enter_api_key'), Colors.YELLOW)
        p(t('get_key_hint'), Colors.DIM)
        print()
        try:
            key = input(f"{Colors.GREEN}API Key: {Colors.RESET}").strip()
            if key:
                config["api_key"] = key
                save_config(config)
                p(t('config_saved'), Colors.GREEN)
            else:
                sys.exit(1)
        except: sys.exit(0)

    cf, msgs, is_new = menu(config)
    print()
    p("=" * 50, Colors.CYAN)
    p(f"  {t('new_created') if is_new else t('loaded').format(n=len(msgs))}", Colors.GREEN)
    p("=" * 50, Colors.CYAN)
    p(f"  {t('help_hint')}", Colors.DIM)
    p(f"  {t('paste_tip')}", Colors.YELLOW)
    print()

    client = OpenAI(api_key=config["api_key"], base_url=BASE_URL)
    show_think = False
    last_think = ""

    while True:
        try:
            first_line = input(f"{Colors.GREEN}> {Colors.RESET}").strip()
            if not first_line: continue

            # 自动检测多行粘贴
            inp = read_all_input(first_line)

            cmd = inp.split('\n')[0].lower()  # 命令只看第一行
            if cmd in ['q', 'exit', 'quit']:
                if msgs: save_session(cf, msgs); p(t('saved'), Colors.DIM)
                p(t('goodbye'), Colors.CYAN); break
            if cmd == 'help': help_cmd(); continue
            if cmd == 'lang':
                current_lang = 'en' if current_lang == 'zh' else 'zh'
                config['lang'] = current_lang; save_config(config)
                p(t('lang_switched'), Colors.YELLOW); continue
            if cmd == 'clear': msgs = []; last_think = ""; p(t('cleared'), Colors.YELLOW); continue
            if cmd == 'think':
                show_think = not show_think
                p(t('thinking_on') if show_think else t('thinking_off'), Colors.YELLOW); continue
            if cmd == 'show':
                if last_think: p(f"💭 {last_think}", Colors.DIM)
                else: p(t('no_thinking'), Colors.YELLOW)
                continue
            if cmd == 'new':
                if msgs: save_session(cf, msgs)
                cf = HISTORY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                msgs = []; last_think = ""; p(t('new_created'), Colors.GREEN); continue
            if cmd == 'sessions':
                if msgs: save_session(cf, msgs)
                cf, msgs, is_new = menu(config)
                p(t('new_created') if is_new else t('loaded').format(n=len(msgs)), Colors.GREEN); continue

            # 文件输入: file <path>
            if inp.lower().startswith('file '):
                fpath = inp[5:].strip()
                fpath = os.path.expanduser(fpath)  # 支持 ~/
                if os.path.exists(fpath):
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            inp = f.read()
                        p(f"{t('file_loaded')}: {len(inp)} chars", Colors.GREEN)
                    except Exception as e:
                        p(f"{t('error')}: {e}", Colors.RED)
                        continue
                else:
                    p(f"{t('file_not_found')}: {fpath}", Colors.RED)
                    continue

            msgs.append({"role": "user", "content": inp})
            print()
            think_buf = ""
            ans_buf = ""
            thinking = False
            answering = False

            try:
                stream = client.chat.completions.create(model=MODEL, messages=msgs, stream=True)
                for chunk in stream:
                    if not chunk.choices: continue
                    ch = chunk.choices[0]
                    if ch.finish_reason: break
                    d = ch.delta

                    if not answering and hasattr(d, 'reasoning_content') and d.reasoning_content:
                        if not thinking:
                            if show_think: p(f"💭 {t('thinking')}", Colors.DIM)
                            else: print(f"{Colors.DIM}💭 {t('thinking')}{Colors.RESET}", end="\r", flush=True)
                            thinking = True
                        think_buf += d.reasoning_content
                        if show_think: print(f"{Colors.DIM}{d.reasoning_content}{Colors.RESET}", end="", flush=True)

                    if hasattr(d, 'content') and d.content:
                        if not answering:
                            if thinking and show_think: print()
                            print()
                            p(f"💬 {t('answer')}:", Colors.MAGENTA)
                            answering = True
                        ans_buf += d.content
                        print(d.content, end="", flush=True)

                try: stream.close()
                except: pass
                print("\n")

                if think_buf: last_think = think_buf
                if ans_buf:
                    msgs.append({"role": "assistant", "content": ans_buf})
                    save_session(cf, msgs)

            except Exception as e:
                p(f"{t('error')}: {e}", Colors.RED)
                if msgs and msgs[-1]["role"] == "user": msgs.pop()

        except KeyboardInterrupt:
            print()
            if msgs: save_session(cf, msgs); p(t('saved'), Colors.DIM)
            p(t('goodbye'), Colors.CYAN); break
        except EOFError:
            if msgs: save_session(cf, msgs)
            p(t('goodbye'), Colors.CYAN); break

if __name__ == "__main__":
    main()
