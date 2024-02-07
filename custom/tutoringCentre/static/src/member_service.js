/* @odoo-module */

import { reactive, useState } from "@odoo/owl";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
// import { _t } from "@web/core/l10n/translation";

export class TutoringCentreMember {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.router = services["tutoringCentre_router"];
    }

    setup() {
        this.user;
        this.memberInfo;
        this.state = reactive({
            registration: false,
        });

        this._init();
    }

    async _init() {
        this.user = await this.rpc("/tutoringCentre/api/userInfo");

        if (!this.user || !this.user.active)
            browser.location.assign("/web/login?redirect=/tutoringCentre");

        console.log(23137, this.user);

        this.memberInfo = await this.rpc("/tutoringCentre/api/memberInfo", {
            userID: this.user.id,
        });

        console.log(78977777, this.userInfo, this.memberInfo);

        if (!this.memberInfo) {
            this.state.registration = false;
            this.router.navigate("member_register");
        } else {
            this.state.registration = true;
        }
    }
}

export const tutoringCentreMember = {
    dependencies: ["rpc", "bus_service", "tutoringCentre_router"],
    start(env, services) {
        const tutoringCentreMember = reactive(
            new TutoringCentreMember(env, services)
        );
        tutoringCentreMember.setup(env, services);
        return tutoringCentreMember;
    },
};
registry
    .category("services")
    .add("tutoringCentre_member", tutoringCentreMember);
