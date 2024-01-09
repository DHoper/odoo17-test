/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Notebook } from "@web/core/notebook/notebook";
import { useClicker } from "../clicker_hook";
import { ClickerValue } from "../clicker_value/clicker_value";

class ClickerClientAction extends Component {
    static template = "awesome_clicker.ClickerClientAction";
    static components = { Notebook, ClickerValue };
    setup() {
        this.clicker = useClicker();
    }
}

registry.category("actions").add("awesome_clicker.client_action", ClickerClientAction);
