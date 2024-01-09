/** @odoo-module */

import { Component, useExternalListener } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService } from "@web/core/utils/hooks";
import { useClicker } from "../clicker_hook";
import { ClickerValue } from "../clicker_value/clicker_value";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class ClickerSystray extends Component {
    static template = "awesome_clicker.ClickerSystray";
    static components = { ClickerValue, Dropdown, DropdownItem };

    setup() {
        this.clicker = useClicker();
        this.action = useService("action");
        useExternalListener(
            window,
            "click",
            event => {
                const targetElement = event.target;
                const button = targetElement.closest("#counterButton");
                if (button || event.target.id === "counterButton") {
                    return;
                }
                this.clicker.increment(1);
            },
            { capture: true }
        );
    }
    openGameClient() {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action",
            target: "new",
            name: "Clicker",
        });
    }

    get numberTrees() {
        let sum = 0;
        for (const tree in this.clicker.trees) {
            sum += this.clicker.trees[tree].purchased;
        }
        return sum;
    }

    get numberFruits() {
        let sum = 0;
        for (const fruit in this.clicker.fruits) {
            sum += this.clicker.fruits[fruit];
        }
        return sum;
    }
}

export const systrayItem = {
    Component: ClickerSystray,
};

registry.category("systray").add("awesome_clicker.ClickerSystray", systrayItem, { sequence: 1000 });
