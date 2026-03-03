from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static, Input
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from datetime import datetime, timedelta
import calendar
import json
import os

DATA_FILE = "period_data.json"
DEFAULT_DATA = {
    "periods": [],
    "settings": {"cycle_length": 28, "period_length": 5, "language": "ru"},
    "symptoms": {}
}

LOGO = """\
 ██████╗ ███████╗██████╗ ██╗ ██████╗ ██████╗ 
 ██╔══██╗██╔════╝██╔══██╗██║██╔═══██╗██╔══██╗
 ██████╔╝█████╗  ██████╔╝██║██║   ██║██║  ██║
 ██╔═══╝ ██╔══╝  ██╔══██╗██║██║   ██║██║  ██║
 ██║     ███████╗██║  ██║██║╚██████╔╝██████╔╝
 ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═════╝
          ✦  T R A C K E R  v 1 . 0  ✦"""

BOOT_STEPS = [
    "  [#ff69b4]█░░░░░░░░░░░░░░░░░░░[/]  [dim]initializing...[/]",
    "  [#ff69b4]████░░░░░░░░░░░░░░░░[/]  [dim]loading data...[/]",
    "  [#ff69b4]████████░░░░░░░░░░░░[/]  [dim]checking cycles...[/]",
    "  [#ff69b4]████████████░░░░░░░░[/]  [dim]calc fertility...[/]",
    "  [#ff69b4]████████████████░░░░[/]  [dim]almost ready...[/]",
    "  [#ff69b4]████████████████████[/]  [bold #ff69b4]READY ✦[/]",
]

I18N = {
    "ru": {
        "status_title": "✦ STATUS",
        "menu_title": "✦ MENU",
        "cycle_day": "День цикла:    {value}",
        "next_period": "След. период:  {value}",
        "started_days_ago": "начался {days} дн. назад",
        "today_mark": "СЕГОДНЯ (!)",
        "in_days": "через {days} дн.",
        "status_fertile": "Статус:        ФЕРТИЛЬНЫЙ ✦",
        "status_ov_today": "Статус:        ОВУЛЯЦИЯ СЕГОДНЯ ✦",
        "ovulation_date": "Овуляция:      {date}",
        "no_data": "Нет данных - нажми [A]",
        "menu_calendar": "[C]  Календарь",
        "menu_add": "[A]  Добавить период",
        "menu_fertile": "[F]  Фертильность",
        "menu_stats": "[S]  Статистика",
        "menu_symptoms": "[N]  Симптомы",
        "menu_settings": "[T]  Настройки",
        "menu_quit": "[Q]  Выход",
        "hint": "\n  [C]Cal [A]Add [F]Fert [S]Stats [N]Note [T]Set [Q]Quit",
        "back": "Назад",
        "add_title": "✦ ДОБАВИТЬ ПЕРИОД",
        "start_date_prompt": "\nДата начала (YYYY-MM-DD):",
        "save_back_hint": "\n[Enter] Сохранить   [Esc] Назад",
        "period_added": "✦ Период добавлен!",
        "already_exists": "⚠ Уже существует",
        "invalid_date_example": "⚠ Неверный формат. Пример: 2025-03-15",
        "calendar_weekdays": "Пн   Вт   Ср   Чт   Пт   Сб   Вс",
        "legend": "\n  [#ff69b4]█[/] след.период  [#ffd700]█[/] овуляция  [#98fb98]█[/] фертильное  [#aaaaff]█[/] прошлые",
        "calendar_controls": "\n[←][→] месяц   [T] сегодня   [Esc] назад",
        "fertile_title": "✦ ФЕРТИЛЬНОСТЬ",
        "not_enough_data": "⚠ Недостаточно данных.",
        "add_one_period": "Добавьте хотя бы один период.",
        "fertile_window": "Фертильное окно:",
        "today_arrow": "  << СЕГОДНЯ",
        "ovulation_line": "Овуляция:  {date}{today}",
        "today_star": "  << СЕГОДНЯ ✦",
        "days_to_ovulation": "До овуляции: {days} дн.",
        "stats_title": "✦ СТАТИСТИКА",
        "recorded_cycles": "Записано циклов:  {value}",
        "average_cycle": "Средний цикл:     {value} дн.",
        "current_day": "Текущий день:     {value}",
        "next_period_stats": "След. период:     {date} {suffix}",
        "in_days_short": "(через {days}д)",
        "days_ago_short": "({days}д назад)",
        "history_sep": "─── История ───",
        "symptoms_title": "✦ СИМПТОМЫ",
        "date_prompt": "\nДата (YYYY-MM-DD):",
        "symptom_label": "Симптом:",
        "symptom_placeholder": "головная боль, усталость...",
        "recent_entries": "Последние записи",
        "enter_symptom": "⚠ Введите симптом",
        "saved": "✦ Записано!",
        "invalid_date": "⚠ Неверный формат даты",
        "settings_title": "✦ НАСТРОЙКИ",
        "cycle_length_prompt": "\nДлина цикла (15-60, сейчас: {value}):",
        "period_length_prompt": "Длит. периода (1-14, сейчас: {value}):",
        "language_prompt": "Язык / Language (ru/en, сейчас: {value}):",
        "settings_saved": "✦ Сохранено!",
        "cycle_validation": "⚠ Цикл: введи число от 15 до 60",
        "period_validation": "⚠ Период: введи число от 1 до 14",
        "language_validation": "⚠ Язык: введи ru или en",
        "month_1": "ЯНВАРЬ",
        "month_2": "ФЕВРАЛЬ",
        "month_3": "МАРТ",
        "month_4": "АПРЕЛЬ",
        "month_5": "МАЙ",
        "month_6": "ИЮНЬ",
        "month_7": "ИЮЛЬ",
        "month_8": "АВГУСТ",
        "month_9": "СЕНТЯБРЬ",
        "month_10": "ОКТЯБРЬ",
        "month_11": "НОЯБРЬ",
        "month_12": "ДЕКАБРЬ",
    },
    "en": {
        "status_title": "✦ STATUS",
        "menu_title": "✦ MENU",
        "cycle_day": "Cycle day:      {value}",
        "next_period": "Next period:    {value}",
        "started_days_ago": "started {days}d ago",
        "today_mark": "TODAY (!)",
        "in_days": "in {days} days",
        "status_fertile": "Status:         FERTILE ✦",
        "status_ov_today": "Status:         OVULATION TODAY ✦",
        "ovulation_date": "Ovulation:      {date}",
        "no_data": "No data - press [A]",
        "menu_calendar": "[C]  Calendar",
        "menu_add": "[A]  Add period",
        "menu_fertile": "[F]  Fertility",
        "menu_stats": "[S]  Statistics",
        "menu_symptoms": "[N]  Symptoms",
        "menu_settings": "[T]  Settings",
        "menu_quit": "[Q]  Quit",
        "hint": "\n  [C]Cal [A]Add [F]Fert [S]Stats [N]Note [T]Set [Q]Quit",
        "back": "Back",
        "add_title": "✦ ADD PERIOD",
        "start_date_prompt": "\nStart date (YYYY-MM-DD):",
        "save_back_hint": "\n[Enter] Save   [Esc] Back",
        "period_added": "✦ Period added!",
        "already_exists": "⚠ Already exists",
        "invalid_date_example": "⚠ Invalid format. Example: 2025-03-15",
        "calendar_weekdays": "Mo   Tu   We   Th   Fr   Sa   Su",
        "legend": "\n  [#ff69b4]█[/] next period  [#ffd700]█[/] ovulation  [#98fb98]█[/] fertile  [#aaaaff]█[/] past",
        "calendar_controls": "\n[←][→] month   [T] today   [Esc] back",
        "fertile_title": "✦ FERTILITY",
        "not_enough_data": "⚠ Not enough data.",
        "add_one_period": "Add at least one period.",
        "fertile_window": "Fertile window:",
        "today_arrow": "  << TODAY",
        "ovulation_line": "Ovulation:  {date}{today}",
        "today_star": "  << TODAY ✦",
        "days_to_ovulation": "Days to ovulation: {days}",
        "stats_title": "✦ STATS",
        "recorded_cycles": "Recorded cycles: {value}",
        "average_cycle": "Average cycle:   {value} days",
        "current_day": "Current day:     {value}",
        "next_period_stats": "Next period:     {date} {suffix}",
        "in_days_short": "(in {days}d)",
        "days_ago_short": "({days}d ago)",
        "history_sep": "--- History ---",
        "symptoms_title": "✦ SYMPTOMS",
        "date_prompt": "\nDate (YYYY-MM-DD):",
        "symptom_label": "Symptom:",
        "symptom_placeholder": "headache, fatigue...",
        "recent_entries": "Recent entries",
        "enter_symptom": "⚠ Enter a symptom",
        "saved": "✦ Saved!",
        "invalid_date": "⚠ Invalid date format",
        "settings_title": "✦ SETTINGS",
        "cycle_length_prompt": "\nCycle length (15-60, current: {value}):",
        "period_length_prompt": "Period length (1-14, current: {value}):",
        "language_prompt": "Language (ru/en, current: {value}):",
        "settings_saved": "✦ Saved!",
        "cycle_validation": "⚠ Cycle: enter a number from 15 to 60",
        "period_validation": "⚠ Period: enter a number from 1 to 14",
        "language_validation": "⚠ Language: enter ru or en",
        "month_1": "JANUARY",
        "month_2": "FEBRUARY",
        "month_3": "MARCH",
        "month_4": "APRIL",
        "month_5": "MAY",
        "month_6": "JUNE",
        "month_7": "JULY",
        "month_8": "AUGUST",
        "month_9": "SEPTEMBER",
        "month_10": "OCTOBER",
        "month_11": "NOVEMBER",
        "month_12": "DECEMBER",
    },
}


def get_lang(data=None):
    d = data or load_data()
    lang = d.get("settings", {}).get("language", "ru")
    return lang if lang in I18N else "ru"


def tr(key, data=None, **kwargs):
    lang = get_lang(data)
    template = I18N[lang].get(key, key)
    return template.format(**kwargs) if kwargs else template

# ── DATA ──────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_DATA.copy()
    with open(DATA_FILE) as f:
        data = json.load(f)

    data.setdefault("periods", [])
    data.setdefault("symptoms", {})
    data.setdefault("settings", {})
    data["settings"].setdefault("cycle_length", DEFAULT_DATA["settings"]["cycle_length"])
    data["settings"].setdefault("period_length", DEFAULT_DATA["settings"]["period_length"])
    data["settings"].setdefault("language", DEFAULT_DATA["settings"]["language"])
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_last(data):
    if not data["periods"]:
        return None
    return datetime.strptime(data["periods"][-1], "%Y-%m-%d")

def next_period(data):
    last = get_last(data)
    return last + timedelta(days=data["settings"]["cycle_length"]) if last else None

def ovulation(data):
    np = next_period(data)
    return np - timedelta(days=14) if np else None

def fertile_window(data):
    ov = ovulation(data)
    return [ov + timedelta(days=i) for i in range(-2, 3)] if ov else []

def avg_cycle(data):
    if len(data["periods"]) < 2:
        return None
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["periods"]]
    gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    return sum(gaps) // len(gaps)

def cycle_day(data):
    last = get_last(data)
    return (datetime.now().date() - last.date()).days + 1 if last else None

def days_to_next(data):
    np = next_period(data)
    return (np.date() - datetime.now().date()).days if np else None

def box(W, title, rows):
    """Build a plain-text box. rows = list of strings."""
    lines = [
        "╔" + "═" * W + "╗",
        "║  " + title + " " * max(0, W - len(title) - 2) + "║",
        "╠" + "═" * W + "╣",
    ]
    for r in rows:
        lines.append("║  " + r + " " * max(0, W - len(r) - 2) + "║")
    lines.append("╚" + "═" * W + "╝")
    return "\n".join(lines)

# ── BOOT ──────────────────────────────────────────

class BootScreen(Screen):
    step: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Container(
            Static(LOGO, id="logo", markup=False),
            Static("", id="bar", markup=True),
            id="boot_box",
        )

    def on_mount(self):
        self._timer = self.set_interval(0.15, self._tick)

    def _tick(self):
        i = self.step
        if i < len(BOOT_STEPS):
            self.query_one("#bar").update(BOOT_STEPS[i])
        self.step += 1
        if self.step >= len(BOOT_STEPS) + 1:
            self._timer.stop()
            self.set_timer(0.3, self._done)

    def _done(self):
        self.app.switch_screen(Dashboard())

# ── DASHBOARD ─────────────────────────────────────

class Dashboard(Screen):
    
    def on_key(self, event):
        key = event.key.lower()
        if key == "c":
            self.app.push_screen(CalendarScreen())
        elif key == "a":
            self.app.push_screen(AddScreen())
        elif key == "f":
            self.app.push_screen(FertileScreen())
        elif key == "s":
            self.app.push_screen(StatsScreen())
        elif key == "n":
            self.app.push_screen(SymptomScreen())
        elif key == "t":
            self.app.push_screen(SettingsScreen())
        elif key == "q":
            self.app.exit()

    def compose(self) -> ComposeResult:
        yield Container(
            Static(LOGO, id="logo", markup=False),
            Container(
                Static("", id="status_box", markup=False),
                Static("", id="menu_box",   markup=False),
                id="dashboard_row",
            ),
            Static("", id="hint_box",   markup=False),
            id="main_container"
        )

    def on_mount(self):
        self._refresh()

    def on_screen_resume(self):
        self._refresh()

    def _refresh(self):
        data = load_data()
        self.query_one("#status_box").update(self._status())
        self.query_one("#menu_box").update(self._menu())
        self.query_one("#hint_box").update(tr("hint", data))

    def _status(self):
        data  = load_data()
        today = datetime.now().date()
        W     = 32
        rows  = []

        cd = cycle_day(data)
        if cd:
            rows.append(tr("cycle_day", data, value=cd))

        d = days_to_next(data)
        if d is not None:
            if d < 0:
                v = tr("started_days_ago", data, days=abs(d))
            elif d == 0:
                v = tr("today_mark", data)
            else:
                v = tr("in_days", data, days=d)
            rows.append(tr("next_period", data, value=v))

        ov = ovulation(data)
        fw = fertile_window(data)
        if ov:
            if any(f.date() == today for f in fw):
                rows.append(tr("status_fertile", data))
            elif ov.date() == today:
                rows.append(tr("status_ov_today", data))
            else:
                rows.append(tr("ovulation_date", data, date=ov.strftime("%d.%m.%Y")))

        if not rows:
            rows.append(tr("no_data", data))

        return "\n" + box(W, tr("status_title", data), rows)

    def _menu(self):
        data = load_data()
        W = 32
        items = [
            tr("menu_calendar", data),
            tr("menu_add", data),
            tr("menu_fertile", data),
            tr("menu_stats", data),
            tr("menu_symptoms", data),
            tr("menu_settings", data),
            tr("menu_quit", data),
        ]
        return "\n" + box(W, tr("menu_title", data), items)

# ── BASE SCREEN ────────────────────────────────────

class BaseScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back", show=False)]

    def action_go_back(self):
        if len(self.app.screen_stack) > 1:
            self.app.pop_screen()

# ── ADD ───────────────────────────────────────────

class AddScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        data = load_data()
        yield Container(
            Static(box(40, tr("add_title", data), []), markup=False, id="title"),
            Static(tr("start_date_prompt", data), markup=False),
            Input(placeholder=datetime.now().strftime("%Y-%m-%d"), id="date"),
            Static("", id="err", markup=False),
            Static(tr("save_back_hint", data), markup=False),
            id="form",
        )

    def on_input_submitted(self, _):
        val = self.query_one("#date").value.strip() or datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(val, "%Y-%m-%d")
            data = load_data()
            if val not in data["periods"]:
                data["periods"].append(val)
                data["periods"].sort()
                save_data(data)
                self.app.notify(tr("period_added", data))
            else:
                self.app.notify(tr("already_exists", data))
            if len(self.app.screen_stack) > 1:
                self.app.pop_screen()
        except ValueError:
            self.query_one("#err").update(tr("invalid_date_example"))

# ── CALENDAR ──────────────────────────────────────

class CalendarScreen(BaseScreen):

    month: reactive[int] = reactive(datetime.now().month)
    year:  reactive[int] = reactive(datetime.now().year)

    def on_key(self, event):
        key = event.key.lower()
        if key == "left":
            self.month -= 1
            if self.month == 0:
                self.month = 12
                self.year -= 1
            self._draw()
            event.stop()
        elif key == "right":
            self.month += 1
            if self.month == 13:
                self.month = 1
                self.year += 1
            self._draw()
            event.stop()
        elif key == "t":
            self.month = datetime.now().month
            self.year = datetime.now().year
            self._draw()
            event.stop()

    def compose(self) -> ComposeResult:
        data = load_data()
        yield Container(
            Static("", id="cal", markup=True),
            Static(tr("legend", data), markup=True, id="legend"),
            Static(tr("calendar_controls", data), markup=False),
            id="cal_wrap",
        )

    def on_mount(self):
        self._draw()

    def _draw(self):
        data  = load_data()
        today = datetime.now().date()
        fw    = [f.date() for f in fertile_window(data)]
        ov    = ovulation(data)
        ov_d  = ov.date() if ov else None
        np    = next_period(data)
        np_d  = np.date() if np else None

        past = set()
        for p in data["periods"]:
            d = datetime.strptime(p, "%Y-%m-%d").date()
            for i in range(data["settings"].get("period_length", 5)):
                past.add(d + timedelta(days=i))

        mname = tr(f"month_{self.month}", data)
        hdr = " ◄  " + mname + " " + str(self.year) + "  ► "
        W = 36
        t  = "[bold #ff69b4]╔" + "═" * W + "╗\n"
        t += "║" + hdr.center(W) + "║\n"
        t += "╠" + "═" * W + "╣\n"
        t += "║ [dim]" + tr("calendar_weekdays", data) + "[/] ║\n"
        t += "╠" + "─" * W + "╣[/]\n"

        for week in calendar.monthcalendar(self.year, self.month):
            row = "[bold #ff69b4]║[/] "
            for day in week:
                if day == 0:
                    row += "     "
                else:
                    cur = datetime(self.year, self.month, day).date()
                    d = str(day).rjust(2)
                    if   cur == today: d = "[bold white reverse]" + d + "[/]"
                    elif cur == np_d:  d = "[bold #ff69b4]"       + d + "[/]"
                    elif cur == ov_d:  d = "[bold #ffd700]"       + d + "[/]"
                    elif cur in fw:    d = "[#98fb98]"             + d + "[/]"
                    elif cur in past:  d = "[#aaaaff]"             + d + "[/]"
                    else:              d = "[dim]"                 + d + "[/]"
                    row += " " + d + "  "
            t += row + "[bold #ff69b4]║[/]\n"

        t += "[bold #ff69b4]╚" + "═" * W + "╝[/]"
        self.query_one("#cal").update(t)

# ── FERTILE ───────────────────────────────────────

class FertileScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        data = load_data()
        yield Container(
            Static("", id="v", markup=False),
            Static("\n[Esc] " + tr("back", data), markup=False),
            id="form",
        )

    def on_mount(self):
        data  = load_data()
        fw    = fertile_window(data)
        ov    = ovulation(data)
        today = datetime.now().date()

        if not fw:
            rows = [tr("not_enough_data", data), tr("add_one_period", data)]
        else:
            rows = [tr("fertile_window", data)]
            for day in fw:
                mark = tr("today_arrow", data) if day.date() == today else ""
                rows.append("  *  " + day.strftime("%Y-%m-%d") + mark)
            rows.append("")
            rows.append(tr(
                "ovulation_line",
                data,
                date=ov.strftime("%Y-%m-%d"),
                today=tr("today_star", data) if ov.date() == today else "",
            ))
            d2ov = (ov.date() - today).days
            if d2ov > 0:
                rows.append(tr("days_to_ovulation", data, days=d2ov))

        self.query_one("#v").update("\n" + box(40, tr("fertile_title", data), rows))

# ── STATS ─────────────────────────────────────────

class StatsScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        data = load_data()
        yield Container(
            Static("", id="v", markup=False),
            Static("\n[Esc] " + tr("back", data), markup=False),
            id="form",
        )

    def on_mount(self):
        data  = load_data()
        avg   = avg_cycle(data)
        today = datetime.now().date()
        rows  = []

        rows.append(tr("recorded_cycles", data, value=len(data["periods"])))
        if avg:
            rows.append(tr("average_cycle", data, value=avg))
        cd = cycle_day(data)
        if cd:
            rows.append(tr("current_day", data, value=cd))
        np = next_period(data)
        if np:
            dl = (np.date() - today).days
            suf = tr("in_days_short", data, days=dl) if dl >= 0 else tr("days_ago_short", data, days=abs(dl))
            rows.append(tr("next_period_stats", data, date=np.strftime("%d.%m.%Y"), suffix=suf))

        if len(data["periods"]) >= 2:
            rows.append("")
            rows.append(tr("history_sep", data))
            dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["periods"]]
            for i, d in enumerate(reversed(dates[-8:])):
                rows.append("  " + str(i+1).rjust(2) + ".  " + d.strftime("%Y-%m-%d"))

        self.query_one("#v").update("\n" + box(40, tr("stats_title", data), rows))

# ── SYMPTOMS ──────────────────────────────────────

class SymptomScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        data = load_data()
        yield Container(
            Static(box(40, tr("symptoms_title", data), []), markup=False),
            Static(tr("date_prompt", data), markup=False),
            Input(placeholder=datetime.now().strftime("%Y-%m-%d"), id="date"),
            Static(tr("symptom_label", data), markup=False),
            Input(placeholder=tr("symptom_placeholder", data), id="symptom"),
            Static("", id="list", markup=False),
            Static(tr("save_back_hint", data), markup=False),
            id="form",
        )

    def on_mount(self):
        self._refresh()

    def _refresh(self):
        data = load_data()
        if not data["symptoms"]:
            return
        rows = []
        for date in sorted(data["symptoms"].keys(), reverse=True)[:5]:
            rows.append(date + ":  " + ", ".join(data["symptoms"][date]))
        self.query_one("#list").update("\n" + box(40, tr("recent_entries", data), rows))

    def on_input_submitted(self, event):
        if event.input.id != "symptom":
            return
        date_val = self.query_one("#date").value.strip() or datetime.now().strftime("%Y-%m-%d")
        symptom  = self.query_one("#symptom").value.strip()
        if not symptom:
            self.app.notify(tr("enter_symptom"))
            return
        try:
            datetime.strptime(date_val, "%Y-%m-%d")
            data = load_data()
            data["symptoms"].setdefault(date_val, []).append(symptom)
            save_data(data)
            self.query_one("#symptom").value = ""
            self.app.notify(tr("saved", data))
            self._refresh()
        except ValueError:
            self.app.notify(tr("invalid_date"))

# ── SETTINGS ──────────────────────────────────────

class SettingsScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        data = load_data()
        cl   = str(data["settings"]["cycle_length"])
        pl   = str(data["settings"]["period_length"])
        lang = get_lang(data)
        yield Container(
            Static(box(40, tr("settings_title", data), []), markup=False),
            Static(tr("cycle_length_prompt", data, value=cl), markup=False),
            Input(placeholder=cl, id="cycle"),
            Static(tr("period_length_prompt", data, value=pl), markup=False),
            Input(placeholder=pl, id="period"),
            Static(tr("language_prompt", data, value=lang), markup=False),
            Input(placeholder=lang, id="language"),
            Static("", id="msg", markup=False),
            Static(tr("save_back_hint", data), markup=False),
            id="form",
        )

    def on_input_submitted(self, _):
        data    = load_data()
        cycle   = self.query_one("#cycle").value.strip()
        period  = self.query_one("#period").value.strip()
        language = self.query_one("#language").value.strip().lower()
        msg     = self.query_one("#msg")
        changed = False
        if cycle:
            if cycle.isdigit() and 15 <= int(cycle) <= 60:
                data["settings"]["cycle_length"] = int(cycle)
                changed = True
            else:
                msg.update(tr("cycle_validation", data))
                return
        if period:
            if period.isdigit() and 1 <= int(period) <= 14:
                data["settings"]["period_length"] = int(period)
                changed = True
            else:
                msg.update(tr("period_validation", data))
                return
        if language:
            if language in I18N:
                data["settings"]["language"] = language
                changed = True
            else:
                msg.update(tr("language_validation", data))
                return
        if changed:
            save_data(data)
            self.app.notify(tr("settings_saved", data))
        if len(self.app.screen_stack) > 1:
            self.app.pop_screen()

# ── APP ───────────────────────────────────────────

class PeriodApp(App):
    TITLE = "PERIOD TRACKER"
    CSS = """
    Screen {
        background: #110018;
    }
    #main_container {
        layout: vertical;
        height: 100%;
        width: 100%;
        overflow: hidden;
    }
    #boot_box {
        align: center middle;
        padding: 2 4;
    }
    #logo {
        color: #ff69b4;
        text-style: bold;
        margin-top:1;
        margin-bottom: 1;
        text-align: center;
    }
    #status_box, #menu_box, #hint_box {
        color: #ffb6c1;
    }
    #dashboard_row {
        layout: horizontal;
        width: 100%;
        height: auto;
        margin: 0 1;
    }
    #status_box {
        width: 1fr;
        margin: 0 1 0 0;
    }
    #menu_box {
        width: 1fr;
        margin: 0 0 0 1;
    }
    #hint_box {
        margin: 0 1;
    }
    #form {
        background: #1a0025;
        border: tall #660066;
        margin: 1 2;
        padding: 1 2;
    }
    #cal_wrap {
        background: #1a0025;
        border: tall #660066;
        margin: 1 2;
        padding: 1 2;
    }
    Static {
        color: #ffb6c1;
    }
    Input {
        background: #110018;
        border: tall #550055;
        color: #ff69b4;
        margin: 0 0 1 0;
    }
    Input:focus {
        border: tall #ff69b4;
        color: white;
    }
    #legend {
        color: #664466;
    }
    #cal {
        color: #ffb6c1;
    }
    """

    def on_mount(self):
        self.push_screen(BootScreen())


def main():
    PeriodApp().run()

if __name__ == "__main__":
    main()
