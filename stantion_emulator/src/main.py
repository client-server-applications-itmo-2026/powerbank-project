"""
Эмулятор станции для тестирования Powerbank API.
Использует BasicAuth для аутентификации.
Запуск: python main.py
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


try:
    import requests
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


SLOT_STATES = ["charged", "charging", "empty"]


def _darken(hex_color: str) -> str:
    """Return a darker shade of the given hex color."""
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    r, g, b = int(r * 0.78), int(g * 0.78), int(b * 0.78)
    return f"#{r:02x}{g:02x}{b:02x}"

COLOR_OK = "#27ae60"
COLOR_ERR = "#e74c3c"
COLOR_NA = "#7f8c8d"
COLOR_WARN = "#f39c12"


@dataclass
class SlotRow:
    index: int
    state_var: tk.StringVar
    battery_id_var: tk.StringVar
    battery_model_var: tk.StringVar


class StantionEmulatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Эмулятор станции — Powerbank API")
        self.root.minsize(960, 700)
        self.root.resizable(True, True)

        self.current_task: Optional[dict] = None
        self.slot_rows: list[SlotRow] = []

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_ui()
        self._rebuild_slots(4)

    # ═══════════════════════════ UI ══════════════════════════════

    def _build_ui(self) -> None:
        # ── Config section ────────────────────────────────────────
        cfg_outer = ttk.LabelFrame(self.root, text="Конфигурация станции")
        cfg_outer.pack(fill=tk.X, padx=8, pady=(6, 2))
        self._build_config(cfg_outer)

        # ── Middle (slots | task) ─────────────────────────────────
        mid = ttk.Frame(self.root)
        mid.pack(fill=tk.BOTH, expand=True, padx=8, pady=2)
        self._build_slots_panel(mid)
        self._build_task_panel(mid)

        # ── Action buttons ────────────────────────────────────────
        act_outer = ttk.LabelFrame(self.root, text="Управление")
        act_outer.pack(fill=tk.X, padx=8, pady=2)
        self._build_actions(act_outer)

        # ── Log ───────────────────────────────────────────────────
        log_outer = ttk.LabelFrame(self.root, text="Журнал запросов")
        log_outer.pack(fill=tk.BOTH, expand=False, padx=8, pady=(2, 6))
        btn_row = ttk.Frame(log_outer)
        btn_row.pack(fill=tk.X, anchor=tk.E)
        ttk.Button(btn_row, text="Очистить журнал", command=self._clear_log).pack(
            side=tk.RIGHT, padx=4, pady=2
        )
        self._log_widget = scrolledtext.ScrolledText(
            log_outer,
            height=9,
            state=tk.DISABLED,
            font=("Courier New", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
        )
        self._log_widget.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 4))

    # ── Configuration ──────────────────────────────────────────

    def _build_config(self, parent: ttk.Frame) -> None:
        # Row 0 — server + credentials + status badge
        r0 = ttk.Frame(parent)
        r0.pack(fill=tk.X, padx=6, pady=3)

        ttk.Label(r0, text="Сервер URL:").pack(side=tk.LEFT)
        self._server_var = tk.StringVar(value="http://localhost:8000")
        ttk.Entry(r0, textvariable=self._server_var, width=34).pack(
            side=tk.LEFT, padx=(3, 14)
        )

        ttk.Label(r0, text="Логин:").pack(side=tk.LEFT)
        self._user_var = tk.StringVar(value="admin")
        ttk.Entry(r0, textvariable=self._user_var, width=14).pack(
            side=tk.LEFT, padx=(3, 8)
        )

        ttk.Label(r0, text="Пароль:").pack(side=tk.LEFT)
        self._pass_var = tk.StringVar(value="admin")
        ttk.Entry(r0, textvariable=self._pass_var, show="*", width=14).pack(
            side=tk.LEFT, padx=3
        )

        self._status_lbl = tk.Label(
            r0,
            text="  НЕ ЗАРЕГИСТРИРОВАНА  ",
            bg=COLOR_NA,
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.RIDGE,
            padx=6,
            pady=3,
        )
        self._status_lbl.pack(side=tk.RIGHT, padx=8)

        # Row 1 — station identity
        r1 = ttk.Frame(parent)
        r1.pack(fill=tk.X, padx=6, pady=3)

        ttk.Label(r1, text="Hardware ID:").pack(side=tk.LEFT)
        self._hw_id_var = tk.StringVar(value="stantion-001")
        ttk.Entry(r1, textvariable=self._hw_id_var, width=22).pack(
            side=tk.LEFT, padx=(3, 14)
        )

        ttk.Label(r1, text="Модель:").pack(side=tk.LEFT)
        self._model_var = tk.StringVar(value="PowerBase-X1")
        ttk.Entry(r1, textvariable=self._model_var, width=18).pack(
            side=tk.LEFT, padx=(3, 8)
        )

        ttk.Label(r1, text="Тип станции:").pack(side=tk.LEFT)
        self._type_var = tk.StringVar(value="standard")
        ttk.Entry(r1, textvariable=self._type_var, width=16).pack(
            side=tk.LEFT, padx=(3, 14)
        )

        ttk.Label(r1, text="Широта:").pack(side=tk.LEFT)
        self._lat_var = tk.StringVar(value="55.7558")
        ttk.Entry(r1, textvariable=self._lat_var, width=10).pack(
            side=tk.LEFT, padx=(3, 8)
        )

        ttk.Label(r1, text="Долгота:").pack(side=tk.LEFT)
        self._lon_var = tk.StringVar(value="37.6173")
        ttk.Entry(r1, textvariable=self._lon_var, width=10).pack(
            side=tk.LEFT, padx=(3, 14)
        )

        ttk.Label(r1, text="Слотов:").pack(side=tk.LEFT)
        self._slots_count_var = tk.IntVar(value=4)
        ttk.Spinbox(
            r1, from_=1, to=20, textvariable=self._slots_count_var, width=5
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(r1, text="Применить", command=self._on_apply_slots).pack(
            side=tk.LEFT, padx=6
        )

    # ── Slots panel ────────────────────────────────────────────

    def _build_slots_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Слоты")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")

        self._slots_canvas = canvas
        self._slots_inner = inner

        # Header row
        headers = [
            ("#", 5),
            ("Состояние", 11),
            ("Battery HW ID", 20),
            ("Модель батареи", 18),
        ]
        for col, (text, width) in enumerate(headers):
            ttk.Label(
                inner,
                text=text,
                width=width,
                anchor=tk.CENTER,
                font=("Arial", 9, "bold"),
            ).grid(row=0, column=col, padx=3, pady=(4, 2))

        # Separator
        ttk.Separator(inner, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=4, sticky=tk.EW, padx=2
        )

    # ── Task panel ─────────────────────────────────────────────

    def _build_task_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Текущая задача")
        frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        frame.configure(width=290)
        frame.pack_propagate(False)

        # Task info display
        info_frame = ttk.Frame(frame, relief=tk.GROOVE, borderwidth=1)
        info_frame.pack(fill=tk.X, padx=8, pady=8)
        self._task_var = tk.StringVar(value="— нет активной задачи —")
        ttk.Label(
            info_frame,
            textvariable=self._task_var,
            wraplength=260,
            justify=tk.LEFT,
            font=("Courier New", 9),
        ).pack(anchor=tk.W, padx=6, pady=6)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=2)

        # Result radio
        ttk.Label(frame, text="Результат выполнения:", font=("Arial", 9, "bold")).pack(
            anchor=tk.W, padx=8, pady=(6, 2)
        )
        self._result_var = tk.StringVar(value="success")
        rf = ttk.Frame(frame)
        rf.pack(anchor=tk.W, padx=8)
        ttk.Radiobutton(
            rf, text="Успех", variable=self._result_var, value="success"
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            rf, text="Ошибка", variable=self._result_var, value="error"
        ).pack(side=tk.LEFT)

        ttk.Label(frame, text="Текст ошибки:").pack(
            anchor=tk.W, padx=8, pady=(6, 1)
        )
        self._err_msg_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self._err_msg_var).pack(
            fill=tk.X, padx=8, pady=(0, 4)
        )

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(
            frame,
            text="Для задачи receive_battery:",
            font=("Arial", 9, "italic"),
        ).pack(anchor=tk.W, padx=8)

        ttk.Label(frame, text="HW ID полученной батареи:").pack(
            anchor=tk.W, padx=8, pady=(6, 1)
        )
        self._recv_bid_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self._recv_bid_var).pack(
            fill=tk.X, padx=8, pady=(0, 4)
        )

        ttk.Label(frame, text="Модель полученной батареи:").pack(
            anchor=tk.W, padx=8, pady=(4, 1)
        )
        self._recv_bmodel_var = tk.StringVar(value="Unknown")
        ttk.Entry(frame, textvariable=self._recv_bmodel_var).pack(
            fill=tk.X, padx=8, pady=(0, 4)
        )

    # ── Action buttons ─────────────────────────────────────────

    def _make_colored_btn(
        self, parent: tk.Widget, text: str, command, bg: str
    ) -> tk.Frame:
        """Colored button using Frame+Label — works on macOS Aqua."""
        frame = tk.Frame(parent, bg=bg, cursor="hand2", bd=0)
        lbl = tk.Label(
            frame,
            text=text,
            bg=bg,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=7,
            cursor="hand2",
        )
        lbl.pack()

        dark = _darken(bg)

        def _press(e):
            command()

        def _enter(e):
            lbl.configure(bg=dark)
            frame.configure(bg=dark)

        def _leave(e):
            lbl.configure(bg=bg)
            frame.configure(bg=bg)

        for w in (frame, lbl):
            w.bind("<Button-1>", _press)
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        return frame

    def _build_actions(self, parent: ttk.Frame) -> None:
        buttons = [
            ("Зарегистрировать", self._do_register, COLOR_OK),
            ("Heartbeat", self._do_heartbeat, COLOR_WARN),
            ("Pull задачу", self._do_pull, "#2980b9"),
            ("Принять задачу", self._do_accept, "#8e44ad"),
            ("Отправить результат", self._do_result, "#16a085"),
        ]
        for label, cmd, bg in buttons:
            self._make_colored_btn(parent, label, cmd, bg).pack(
                side=tk.LEFT, padx=6, pady=8
            )

    # ═══════════════════════════ Slots ═══════════════════════════

    def _on_apply_slots(self) -> None:
        self._rebuild_slots(self._slots_count_var.get())

    def _rebuild_slots(self, count: int) -> None:
        # Remove all rows after header (row=0) and separator (row=1)
        for w in list(self._slots_inner.winfo_children()):
            gi = w.grid_info()
            if gi and int(gi.get("row", 0)) > 1:
                w.destroy()

        self.slot_rows = []
        for i in range(count):
            sv = tk.StringVar(value="empty")
            bv = tk.StringVar(value="")
            mv = tk.StringVar(value="")
            row = SlotRow(i, sv, bv, mv)
            self.slot_rows.append(row)

            r = i + 2  # 0=header, 1=separator
            ttk.Label(self._slots_inner, text=str(i), width=5, anchor=tk.CENTER).grid(
                row=r, column=0, padx=3, pady=2
            )
            ttk.Combobox(
                self._slots_inner,
                textvariable=sv,
                values=SLOT_STATES,
                state="readonly",
                width=9,
            ).grid(row=r, column=1, padx=3, pady=2)
            ttk.Entry(self._slots_inner, textvariable=bv, width=20).grid(
                row=r, column=2, padx=3, pady=2
            )
            ttk.Entry(self._slots_inner, textvariable=mv, width=18).grid(
                row=r, column=3, padx=3, pady=2
            )

        self._slots_canvas.update_idletasks()
        self._slots_canvas.configure(scrollregion=self._slots_canvas.bbox("all"))
        self._log(f"[Слоты] Создано {count} слот(ов)")

    # ═══════════════════════════ Helpers ═════════════════════════

    def _auth(self) -> tuple[str, str]:
        return self._user_var.get(), self._pass_var.get()

    def _base(self) -> str:
        return self._server_var.get().rstrip("/")

    def _stantion_info(self) -> dict:
        return {
            "hardware_id": self._hw_id_var.get(),
            "model_name": self._model_var.get(),
            "location": {
                "lat": float(self._lat_var.get()),
                "lon": float(self._lon_var.get()),
            },
        }

    def _slot_states(self) -> list:
        out = []
        for sr in self.slot_rows:
            bid = sr.battery_id_var.get().strip()
            bmod = sr.battery_model_var.get().strip()
            battery = (
                {"hardware_id": bid, "model_name": bmod or "Unknown"} if bid else None
            )
            out.append(
                {
                    "slot_index": sr.index,
                    "state": sr.state_var.get(),
                    "battery_info": battery,
                }
            )
        return out

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_widget.configure(state=tk.NORMAL)
        self._log_widget.insert(tk.END, f"[{ts}] {msg}\n")
        self._log_widget.see(tk.END)
        self._log_widget.configure(state=tk.DISABLED)

    def _clear_log(self) -> None:
        self._log_widget.configure(state=tk.NORMAL)
        self._log_widget.delete("1.0", tk.END)
        self._log_widget.configure(state=tk.DISABLED)

    def _set_status(self, ok: bool, text: str = "") -> None:
        if ok:
            label = text or "  ЗАРЕГИСТРИРОВАНА  "
            self._status_lbl.configure(text=label, bg=COLOR_OK)
        else:
            self._status_lbl.configure(
                text=text or "  НЕ ЗАРЕГИСТРИРОВАНА  ", bg=COLOR_ERR
            )

    def _post(self, url: str, payload: dict, auth: tuple) -> requests.Response:
        self._log(f"─── POST {url} ───")
        self._log(json.dumps(payload, ensure_ascii=False, indent=2))
        resp = requests.post(url, json=payload, auth=auth, timeout=10)
        body = resp.text[:600] if resp.text else "(пустой ответ)"
        self._log(f"<<< {resp.status_code} {resp.reason}  {body}")
        self._log("")
        return resp

    # ═══════════════════════════ API ═════════════════════════════

    def _do_register(self) -> None:
        # Collect all StringVar values on the main thread
        payload = {
            "stantion_type_name": self._type_var.get(),
            "location": {
                "lat": float(self._lat_var.get()),
                "lon": float(self._lon_var.get()),
            },
            "hardware_id": self._hw_id_var.get(),
        }
        url = f"{self._base()}/api/register-stantion"
        auth = self._auth()

        try:
            resp = self._post(url, payload, auth)
            if resp.status_code in (200, 201, 204):
                self._set_status(True)
                self._log("✓ Станция зарегистрирована успешно")
            else:
                self._set_status(False)
                self._log(f"✗ Ошибка регистрации: {resp.status_code}")
        except Exception as exc:
            self._set_status(False)
            self._log(f"✗ Исключение: {exc}")

    def _do_heartbeat(self) -> None:
        payload = {
            "stantion_info": self._stantion_info(),
            "slot_states": self._slot_states(),
        }
        url = f"{self._base()}/api/create-stantion-heartbeat"
        auth = self._auth()

        try:
            resp = self._post(url, payload, auth)
            if resp.status_code in (200, 201, 204):
                self._log("✓ Heartbeat принят")
            else:
                self._log(f"✗ Heartbeat не принят: {resp.status_code}")
        except Exception as exc:
            self._log(f"✗ Исключение: {exc}")

    def _do_pull(self) -> None:
        payload = {"hardware_id": self._hw_id_var.get()}
        url = f"{self._base()}/api/pull-stantion-task"
        auth = self._auth()

        try:
            resp = self._post(url, payload, auth)
            if resp.status_code == 200:
                data = resp.json()
                self.current_task = data
                lines = [
                    f"Task ID:  {data.get('task_id', '?')}",
                    f"Тип:      {data.get('task_type', '?')}",
                ]
                if data.get("payload_release_battery_hardware_id"):
                    lines.append(
                        f"Battery:  {data['payload_release_battery_hardware_id']}"
                    )
                self._task_var.set("\n".join(lines))
                self._log("✓ Задача получена")
            elif resp.status_code == 204:
                self.current_task = None
                self._task_var.set("— нет активной задачи —")
                self._log("— Задач нет в очереди")
            else:
                self._log(f"✗ Ошибка pull: {resp.status_code}")
        except Exception as exc:
            self._log(f"✗ Исключение: {exc}")

    def _do_accept(self) -> None:
        if not self.current_task:
            messagebox.showwarning(
                "Нет задачи", "Сначала получите задачу через «Pull задачу»"
            )
            return
        payload = {
            "hardware_id": self._hw_id_var.get(),
            "task_id": self.current_task["task_id"],
        }
        url = f"{self._base()}/api/accept-stantion-task"
        auth = self._auth()

        try:
            resp = self._post(url, payload, auth)
            if resp.status_code == 200:
                self._log("✓ Задача принята в работу")
            else:
                self._log(f"✗ Ошибка принятия задачи: {resp.status_code}")
        except Exception as exc:
            self._log(f"✗ Исключение: {exc}")

    def _do_result(self) -> None:
        if not self.current_task:
            messagebox.showwarning(
                "Нет задачи", "Сначала получите задачу через «Pull задачу»"
            )
            return

        success = self._result_var.get() == "success"
        err = self._err_msg_var.get().strip() or None
        task_type = self.current_task.get("task_type", "")

        if task_type == "receive_battery":
            bid = self._recv_bid_var.get().strip()
            bmod = self._recv_bmodel_var.get().strip() or "Unknown"
            result = {
                "success": success,
                "error": err,
                "received_battery": (
                    {"hardware_id": bid, "model_name": bmod}
                    if (success and bid)
                    else None
                ),
            }
        else:
            result = {"success": success, "error": err}

        payload = {
            "hardware_id": self._hw_id_var.get(),
            "task_id": self.current_task["task_id"],
            "result": result,
        }
        url = f"{self._base()}/api/create-stantion-task-result"
        auth = self._auth()

        try:
            resp = self._post(url, payload, auth)
            if resp.status_code == 200:
                self.current_task = None
                self._task_var.set("— нет активной задачи —")
                self._log("✓ Результат отправлен, задача завершена")
            else:
                self._log(f"✗ Ошибка отправки результата: {resp.status_code}")
        except Exception as exc:
            self._log(f"✗ Исключение: {exc}")


# ═══════════════════════════════════════════════════════════════


def main() -> None:
    root = tk.Tk()
    try:
        # Adjust DPI scaling on macOS / Retina
        root.tk.call("tk", "scaling", 1.3)
    except tk.TclError:
        pass
    StantionEmulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
