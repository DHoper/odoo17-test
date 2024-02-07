/* @odoo-module */

import { reactive, useState } from "@odoo/owl";
import { session } from "@web/session";

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
// import { _t } from "@web/core/l10n/translation";

export class TutoringCentreLiveChat {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.messagingService = services["mail.messaging"];
    }

    setup() {
        this.userName = "Visitor";
        this.user;
        this.channel_id = null;
        this.channelInfo = null;
        this.channel = null;
        this.channelMessages = reactive([]);
        this.uuid = "";

        this._createChat();
    }

    //需加入頻道在資料庫不存在時的處裡邏輯
    async _createChat() {
        this.user = await this.rpc("/tutoringCentre/api/userInfo");

        if (!this.user || !this.user.active)
            browser.location.assign(
                "/web/login?redirect=/tutoringCentre/TutorTalk"
            );
        this.userName = this.user.name;
        // browser.localStorage.removeItem("tutorTalk_channelInfo");

        // 嘗試獲取本地端頻道資訊
        const localChannelInfo = browser.localStorage.getItem(
            "tutorTalk_channelInfo"
        );

        if (localChannelInfo) {
            this.channelInfo = JSON.parse(localChannelInfo);
            this.channel = await this.rpc(
                "/tutoringCentre/TutorTalk/api/livechat/fetchChannel",
                { channel_uuid: this.channelInfo.uuid }
            );
        }

        if (
            !this.channelInfo ||
            !this.channel ||
            !this.channel.channel_partner_ids.includes(this.user.partner_id[0])
        ) {
            const { channel_info, channel } = await this.rpc(
                "/tutoringCentre/TutorTalk/api/livechat/buildChat",
                {
                    channel_id: 2,
                    anonymous_name: this.userName,
                    chatbot_script_id: null,
                    previous_operator_id: 1,
                    persisted: true,
                },
                { shadow: true }
            );

            console.log(channel_info, "頻道", channel);
            if (channel_info) {
                browser.localStorage.setItem(
                    "tutorTalk_channelInfo",
                    JSON.stringify(channel_info)
                );
            }

            this.channelInfo = channel_info;
            this.channel = channel;
        }

        this.channel_id = this.channelInfo.id;
        this.uuid = this.channelInfo.uuid;

        this.busService.addChannel(`${this.channel.id}`);
        this.busService.subscribe("discuss.channel/new_message", payload => {
            if (payload.id !== this.channel_id) return;
            this.channelMessages.push(payload.message);
        });
    }

    onMessage({ detail: notifications }) {
        notifications = notifications.filter(
            item => item.payload.channel === this.channel
        );
    }

    async sendMessage(text) {
        if (!this.channelInfo.uuid) return;
        await this.rpc("/tutoringCentre/TutorTalk/api/livechat/send_message", {
            channel_uuid: this.channelInfo.uuid,
            message: text,
        });
    }
}

export const tutoringCentreLiveChat = {
    dependencies: ["rpc", "bus_service", "mail.messaging"],
    start(env, services) {
        const tutoringCentreLiveChat = reactive(
            new TutoringCentreLiveChat(env, services)
        );
        tutoringCentreLiveChat.setup(env, services);
        return tutoringCentreLiveChat;
    },
};
registry
    .category("services")
    .add("tutoringCentre_liveChat", tutoringCentreLiveChat);
