/* @odoo-module */

import { reactive, useState } from "@odoo/owl";

import { registry } from "@web/core/registry";
// import { _t } from "@web/core/l10n/translation";

export class TutoringCentreLiveChat {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.messagingService = services["mail.messaging"];
        console.log(services, 888);
    }

    setup(env, services) {
        console.log(777);
        console.log(env);
        this.userName = "Visitor";
        this.channel_id = null;
        this.channelInfo = null;
        this.channelMessages = reactive([]);
        this.uuid = "";

        this._createChat();
    }

    async _createChat() {
        this.channelInfo = await this.rpc(
            "/tutoringCentre/parentPortal/buildChat",
            {
                channel_id: 1,
                anonymous_name: this.userName,
                chatbot_script_id: null,
                // previous_operator_id: cookie.get(this.OPERATOR_COOKIE),
                previous_operator_id: 1,
                persisted: true,
            },
            { shadow: true }
        );
        this.channel_id = this.channelInfo.id;
        this.uuid = this.channelInfo.uuid;
        console.log("頻道已建立", this.channelInfo);
        this._listenChannel();
    }

    async sendMessage(text) {
        // if (!this.channelInfo.channel_uuid) return;
        console.log(this.channelInfo.uuid, 54545);
        this.rpc("/tutoringCentre/livechat/send_message", {
            channel_uuid: this.channelInfo.uuid,
            message: text,
        });
        console.log("訊息已發送");
    }

    _listenChannel() {
        console.log("進入監聽函數");
        try {
            this.messagingService.isReady
                .then(() => {
                    console.log("開始監聽");
                    this.busService.addEventListener(
                        "notification",
                        ({ detail: notifications }) => {
                            for (const notif of notifications.filter(
                                ({ payload, type }) =>
                                    type === "discuss.channel/new_message" &&
                                    payload.id === this.channel_id
                            )) {
                                this.channelMessages.push(
                                    notif.payload.message
                                );
                                console.log("新消息");
                            }
                            console.log("notifications", notifications);
                        }
                    );
                })
                .catch(err => console.log("監聽失敗，錯誤訊息:", err));
        } catch (err) {
            console.log("頻道監聽失敗，錯誤訊息:", err);
        }
    }
}

export const tutoringCentreLiveChat = {
    dependencies: ["rpc", "bus_service", "mail.messaging"],
    start(env, services) {
        const tutoringCentreLiveChat = reactive(
            new TutoringCentreLiveChat(env, services)
        );
        console.log(env, services, 8896);
        tutoringCentreLiveChat.setup(env, services);
        return tutoringCentreLiveChat;
    },
};
registry
    .category("services")
    .add("TutoringCentreLiveChat", tutoringCentreLiveChat);
