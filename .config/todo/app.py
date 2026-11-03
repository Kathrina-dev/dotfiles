#!/usr/bin/env python3

import json
import re
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, ListView, ListItem, Static
from textual.binding import Binding

TASK_FILE = Path.home() / ".config/todo/tasks.json"

def parse_date_string(due_str: str) -> datetime | None:
    if not due_str or not isinstance(due_str, str):
        return None

    clean_due = due_str.strip()
    if not clean_due:
        return None

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(clean_due, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(clean_due)
    except ValueError:
        return None

class TaskItem(ListItem):
    def __init__(
        self,
        title: str,
        done: bool = False,
        due: str = "",
    ) -> None:
        super().__init__()
        self.title_text = title
        self.done = done
        self.due = due

    def _render_title(self) -> str:
        if self.done:
            return f"[bold #00ff87]✓[/] [strike #888888]{self.title_text}[/]"
        return f"[bold #ffffff]□[/] [bold #ffffff]{self.title_text}[/]"

    def _render_due(self) -> str:
        if not self.due:
            return ""

        dt = parse_date_string(self.due)
        if dt:
            if dt.hour == 0 and dt.minute == 0:
                return f"[#cccccc]{dt.strftime('%Y-%m-%d')}[/]"
            return f"[#cccccc]{dt.strftime('%Y-%m-%d %H:%M')}[/]"

        return f"[#cccccc]{self.due}[/]"

    def compose(self) -> ComposeResult:
        yield Static(
            self._render_title(),
            classes="task-title",
            id="title",
        )
        yield Static(
            self._render_due(),
            classes="task-due",
            id="due",
        )

    def update_content(self) -> None:
        self.query_one("#title", Static).update(self._render_title())
        self.query_one("#due", Static).update(self._render_due())

class TodoApp(App):
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "focus_input", "Add Task"),
        Binding("space", "toggle_task", "Toggle Done"),
        Binding("d", "delete_task", "Delete Task"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    CSS = """
        Screen, App {
            background: #000000;
            color: #ffffff;
        }

        #main {
            width: 100%;
            height: 100%;
            padding: 1 2;
            background: #000000;
        }

        #task_list {
            width: 100%;
            height: 1fr;
            background: #000000;
            color: #ffffff;
            border: none;
            scrollbar-size: 1 1;
            scrollbar-color: #ff1493;
        }

        ListView, ListView > * {
            background: #000000;
            color: #ffffff;
        }

        ListItem {
            layout: horizontal;
            width: 100%;
            height: 1;
            padding: 0 1;
            background: #000000;
            color: #ffffff;
        }

        .task-title {
            width: 1fr;
            height: 1;
            background: #000000;
            color: #ffffff;
            content-align: left middle;
        }

        .task-due {
            width: auto;
            height: 1;
            background: #000000;
            color: #ffffff;
            content-align: right middle;
            text-align: right;
        }

        ListItem:hover,
        ListItem:hover .task-title,
        ListItem:hover .task-due {
            background: #222222;
        }

        ListItem.-highlight,
        ListItem.-highlight .task-title,
        ListItem.-highlight .task-due {
            background: #ff1493;
            color: #ffffff;
            text-style: bold;
        }

        #input_box {
            dock: bottom;
            width: 100%;
            height: 1;
            margin-top: 1;
            padding: 0 1;
            background: #111111;
            color: #ffffff;
            border: none;
        }

        #input_box:focus {
            background: #ff1493;
            color: #ffffff;
        }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="main"):
            yield ListView(id="task_list")
            yield Input(
                placeholder="Submit report --due 2026-09-28 14:00",
                id="input_box",
            )

    def on_mount(self) -> None:
        self.task_list = self.query_one("#task_list", ListView)
        self.input_box = self.query_one("#input_box", Input)
        self.load_and_sort_tasks()
        self.task_list.focus()

    def parse_task_input(self, raw_input: str) -> tuple[str, str]:
        match = re.search(
            r"(?:--due|@)\s+(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)$",
            raw_input,
            re.IGNORECASE,
        )

        if not match:
            return raw_input.strip(), ""

        due = match.group(1).strip()
        title = raw_input[:match.start()].strip()

        if len(due) == 10:
            due += " 00:00"

        return title, due

    def _sort_key(self, task: dict) -> tuple:
        due = task.get("due", "").strip()
        parsed_due = parse_date_string(due)

        if parsed_due is None:
            # Tasks WITHOUT deadlines are prioritized first (group 0)
            return (0, datetime.min, task.get("title", "").lower())

        # Tasks WITH deadlines appear after (group 1), ordered chronologically
        return (1, parsed_due, task.get("title", "").lower())

    def get_all_tasks_data(self) -> list[dict]:
        tasks = []
        for item in self.task_list.children:
            if isinstance(item, TaskItem):
                tasks.append(
                    {
                        "title": item.title_text,
                        "done": item.done,
                        "due": item.due,
                    }
                )
        return tasks

    def load_and_sort_tasks(self) -> None:
        if not TASK_FILE.exists():
            return

        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                raw_tasks = json.load(f)

            cleaned_tasks = []
            for t in raw_tasks:
                title = t.get("title", "")
                due = t.get("due", "")
                
                if not due and ("--due" in title or "@" in title):
                    p_title, p_due = self.parse_task_input(title)
                    if p_due:
                        title, due = p_title, p_due

                cleaned_tasks.append({
                    "title": title,
                    "done": t.get("done", False),
                    "due": due,
                })

            self.render_sorted_tasks(cleaned_tasks)
        except (json.JSONDecodeError, OSError):
            pass

    def render_sorted_tasks(
        self,
        tasks: list[dict],
        focus_title: str | None = None,
    ) -> None:
        tasks.sort(key=self._sort_key)
        self.task_list.clear()

        target_index = 0
        for i, task in enumerate(tasks):
            item = TaskItem(
                task.get("title", ""),
                task.get("done", False),
                task.get("due", ""),
            )
            self.task_list.mount(item)

            if focus_title and task.get("title") == focus_title:
                target_index = i

        self.save_tasks_to_file(tasks)

        if self.task_list.children:
            self.task_list.index = target_index

    def save_tasks_to_file(self, tasks: list[dict]) -> None:
        TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = TASK_FILE.with_suffix(".tmp")

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                tasks,
                f,
                indent=2,
                ensure_ascii=False,
            )

        tmp.replace(TASK_FILE)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()

        if value:
            title, due = self.parse_task_input(value)
            tasks = self.get_all_tasks_data()
            tasks.append(
                {
                    "title": title,
                    "done": False,
                    "due": due,
                }
            )

            self.render_sorted_tasks(tasks, focus_title=title)
            self.input_box.value = ""
            self.task_list.focus()

    def action_focus_input(self) -> None:
        self.input_box.focus()

    def action_toggle_task(self) -> None:
        if self.task_list.has_focus and self.task_list.highlighted_child:
            item = self.task_list.highlighted_child
            if isinstance(item, TaskItem):
                item.done = not item.done
                item.update_content()
                self.save_tasks_to_file(self.get_all_tasks_data())

    def action_delete_task(self) -> None:
        if self.task_list.has_focus and self.task_list.highlighted_child:
            item = self.task_list.highlighted_child
            item.remove()
            self.save_tasks_to_file(self.get_all_tasks_data())

    def action_cursor_down(self) -> None:
        if self.task_list.has_focus:
            self.task_list.action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.task_list.has_focus:
            self.task_list.action_cursor_up()

    def on_key(self, event) -> None:
        if self.input_box.has_focus and event.key == "escape":
            self.task_list.focus()
            event.prevent_default()

if __name__ == "__main__":
    TodoApp().run()