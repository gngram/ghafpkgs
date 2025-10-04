# Copyright 2022-2025 TII (SSRC) and the Ghaf contributors
# SPDX-License-Identifier: Apache-2.0

import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from upm.api_client import APIClient
import gi

from upm.logger import logger, log_entry_exit

gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gtk, Gio

from upm.logger import logger

SELECT_LABEL = "Select"

class WinGenerator(Gtk.ApplicationWindow):
    def __init__(
        self,
        app: Gtk.Application,
        apiclient,
        devices,
        title: str = "Device Bridge",
    ):
        super().__init__(application=app, title=title)
        self.devices = devices
        self.apiclient = apiclient
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(root)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_margin_top(8)
        content_box.set_margin_bottom(8)
        content_box.set_margin_start(8)
        content_box.set_margin_end(8)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        root.append(content_box)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        content_box.append(scroller)

        self.inner = Gtk.FlowBox()
        self.inner.set_selection_mode(Gtk.SelectionMode.NONE)
        self.inner.set_valign(Gtk.Align.START)
        self.inner.set_halign(Gtk.Align.FILL)
        self.inner.set_column_spacing(8)
        self.inner.set_row_spacing(8)
        self.inner.set_homogeneous(False)
        self.inner.set_min_children_per_line(2)
        self.inner.set_max_children_per_line(2)
        scroller.set_child(self.inner)

        self.action_bar = Gtk.ActionBar()
        root.append(action_bar)

        self.action_bar.pack_start(Gtk.Box(hexpand=True))
        self.blocks = {}

    def _add_close_btn(self):
        self.close_btn = Gtk.Button(label="Close")
        self.close_btn.connect("clicked", lambda *_: self.close())
        self.action_bar.pack_end(self.close_btn)
        self.connect("close-request", self._on_close_request)
        
    def _add_refresh_btn(self):
        self.refresh_btn = Gtk.Button(label="Refresh")
        self.refresh_btn.set_tooltip_text("Refresh status from JSON.")
        self.refresh_btn.connect("clicked", self._on_refresh_clicked)
        self.action_bar.pack_end(self.refresh_btn)
        
    def show_notification(self):
        self.set_default_size(320, 320)
        self._add_close_btn()
        self._load_ui()

    def show_app_window(self):
        self.set_default_size(600, 300)
        self._add_refresh_btn()
        self._add_close_btn()
        self._load_ui()

    def _clear_blocks_ui(self) -> None:
        for info in list(self.blocks.values()):
            container = info.get("container")
            if container is not None and container.get_parent() is not None:
                self.inner.remove(container)
        self.blocks.clear()

    def _make_dropdown(
        self, device_id: str, items: List[str], selected: Optional[str]
    ) -> Gtk.DropDown:
        model = Gtk.StringList.new([SELECT_LABEL] + items)
        dropdown = Gtk.DropDown.new(model=model, expression=None)
        dropdown.set_hexpand(False)
        if selected and selected in items:
            dropdown.set_selected(items.index(selected) + 1)
        else:
            dropdown.set_selected(0)
        dropdown.connect("notify::selected", self._on_dropdown_changed, device_id)
        return dropdown

    def _add_block_ui(
        self,
        device_id: str,
        product: str,
        targets: List[str],
        selected: Optional[str],
    ) -> None:
        frame = Gtk.Frame()
        frame.add_css_class("card")
        frame.set_hexpand(True)
        frame.set_vexpand(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        frame.set_child(vbox)

        lbl = Gtk.Label()
        lbl.set_use_markup(True)
        lbl.set_selectable(True)
        lbl.set_xalign(0.0)
        lbl.set_hexpand(True)
        lbl.set_markup(f"{product}:")
        vbox.append(lbl)

        dropdown = self._make_dropdown(device_id, targets, selected)
        vbox.append(dropdown)

        self.inner.append(frame)

        self.blocks[device_id] = {
            "container": frame,
            "label": lbl,
            "dropdown": dropdown,
        }

    def _load_ui(self):
        self._clear_blocks_ui()
        for dev in self.devices:
            dev_id = dev.get("device_node")
            product = dev.get("product_name")
            permitted = dev.get("allowed_vms", [])
            selected = dev.get("vm")
            self._add_block_ui(dev_id, product, permitted, selected)

    def _find_device(self, device_id: str):
        for dev in self.devices:
            if dev.get("device_node") == device_id:
                return dev
        return None

    def _request_passthrough(self, device_id: str, new_vm: str) -> bool:
        device = self._find_device(device_id)
        response = self.apiclient.usb_detach(device)
        if response.get("result") != "ok":
            logger.error(f"Failed to detach device!")
        response = self.appclient.usb_attach(device, new_vm)
        if response.get("result") != "ok":
            logger.error(f"Failed to attach device!")
            return False
        return True
    
    def _on_dropdown_changed(
        self, dropdown: Gtk.DropDown, _pspec, device_id: str
    ) -> None:
        idx = dropdown.get_selected()
        if idx < 0:
            return
        model = dropdown.get_model()
        text = model.get_string(idx)
        if text is None or text == SELECT_LABEL:
            return
        status = self._request_passthrough(device_id, text)
        if not status:
            self._show_error_dialog(
                title="Error", message="Failed to request passthrough."
            )

    def _on_refresh_clicked(self, _btn: Gtk.Button) -> None:
        response = self.apiclient.usb_list()
        if response.get("result") == "ok":
            self.devices = response.get("devices", [])
            self._load_ui()

    def _show_error_dialog(self, title: str, message: str) -> bool:
        dlg = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
            secondary_text=message,
        )
        dlg.connect("response", lambda d, _r: d.destroy())
        dlg.present()
        return False

    def _on_close_request(self, *_args) -> bool:
        return False


class USBDeviceMap(Gtk.Application):
    def __init__(self, server_port=7000):
        super().__init__(
            application_id="ghaf.usb-device.map", flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.server_port = server_port
        self._win: Optional[WinGenerator] = None

    def do_activate(self):
        if not self._win:
            apiclient = APIClient(port = self.server_port)
            devices = apiclient.usb_list()
            if devices.get("result") == "ok":
                self._win = WinGenerator(self, apiclient=apiclient, devices=devices.get("usb_devices", []), title="USB Device Map")
                self._win.show_app_window()
        self._win.present()


class Notification(Gtk.Application):
    def __init__(self, server_port=7000):
        super().__init__(
            application_id="ghaf.usbdevice.notificiation", flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.server_port = server_port
        self._win: Optional[WinGenerator] = None

    def do_activate(self, apiclient, device):
        if not self._win:
            self._win = WinGenerator(self, apiclient=apiclient, devices=[device], title="Device Notification!")
            self._win.show_notification()
        self._win.present()

   
class USBDeviceNotification():
    def __init__(self, server_port=7000):
        self.server_port = server_port
        self.apiclient = APIClient.recv_notifications(callback=self.notify_user, port=server_port)
    
    def notify_user(self, device):
        th = threading.Thread(target=self.show_notif_window, args=(device))
        th.start()
        th.join()

    def show_notif_window(self, device):
        notif = Notification(self.server_port)
        raise SystemExit(notif.run(None))
        
