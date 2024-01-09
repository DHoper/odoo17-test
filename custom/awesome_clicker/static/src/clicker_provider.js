/** @odoo-module **/

import { registry } from "@web/core/registry";

const commandProviderRegistry = registry.category("command_provider");

commandProviderRegistry.add("clicker", {
    provide: (env, options) => {
        return [
            {
                name: "買一隻a型機器人",
                action() {
                    env.services["awesome_clicker.clicker"].buyBot("botA");
                },
            },
            {
                name: "打開點擊遊戲面板",
                action() {
                    env.services.action.doAction({
                        type: "ir.actions.client",
                        tag: "awesome_clicker.client_action",
                        target: "new",
                        name: "Clicker Game",
                    });
                },
            }
        ]
    },
});
