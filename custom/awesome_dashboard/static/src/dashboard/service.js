/* @odoo-module */

import { reactive } from "@odoo/owl";

import { registry } from "@web/core/registry";

export class MailCoreCommon {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.attachmentService = services["mail.attachment"];
        this.messageService = services["mail.message"];
        this.messagingService = services["mail.messaging"];
        this.store = services["mail.store"];
        this.userSettingsService = services["mail.user_settings"];
    }

    setup() {
        this.messagingService.isReady.then(() => {
            this.busService.subscribe("mail.record/insert", payload => {
                for (const Model in payload) {
                    console.log("訊息服務資料", Model);
                }
            });
        });
    }
}

export const mailCoreCommon = {
    dependencies: [
        "bus_service",
        "mail.attachment",
        "mail.message",
        "mail.messaging",
        "mail.store",
        "mail.user_settings",
    ],
    start(env, services) {
        const mailCoreCommon = reactive(new MailCoreCommon(env, services));
        mailCoreCommon.setup();
        console.log(env,124454);
        return mailCoreCommon;
    },
};

registry.category("services").add("liveABC", mailCoreCommon);
