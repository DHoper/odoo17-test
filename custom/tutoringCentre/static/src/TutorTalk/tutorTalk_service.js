/* @odoo-module */

import { reactive, useState, markup } from "@odoo/owl";
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
        this.member = services["tutoringCentre_member"];
    }

    async setup() {
        this.live_channel_ids = [];
        this.announce_channel_ids = [];
        this.live_channels = [];
        this.announce_channels = [];
        this.live_channel_messages = {};
        this.announce_channel_messages = {};
        this.last_message_list = reactive({});
        this.last_message_notify = reactive({});
        await this._connectChat();
    }

    //需加入頻道在資料庫不存在時的處裡邏輯
    async _connectChat() {
        this.live_channel_ids = [];
        const courses = [];
        for (const student of this.member.memberInfo.student) {
            if (student.active_channels.length > 0) {
                this.live_channel_ids.push(...student.active_channels);
            }
            courses.push(...student.courses);
        }
        const im_livechat_ids = [];
        for (const course of courses) {
            if (
                course.im_livechat_id &&
                !im_livechat_ids.includes(course.im_livechat_id[0])
            ) {
                im_livechat_ids.push(course.im_livechat_id[0]);
            }
        }

        this.announce_channel_ids = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_announce_channel",
            { im_livechat_ids }
        );

        await this._fetch_channel();

        await this._connect_channel(
            this.live_channel_messages,
            this.live_channel_ids
        );

        await this._connect_channel(
            this.announce_channel_messages,
            this.announce_channel_ids
        );

        await this._bus_subscribe(
            this.announce_channel_ids.concat(this.live_channel_ids),
            [this.announce_channel_messages, this.live_channel_messages]
        );
    }

    async _fetch_channel() {
        this.live_channels = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
            {
                channel_ids: this.live_channel_ids,
            }
        );

        this.announce_channels = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
            {
                channel_ids: this.announce_channel_ids,
            }
        );
    }
    async _connect_channel(messages_container, ids) {
        for (const id of ids) {
            const { messages } = await this.rpc("/discuss/channel/messages", {
                channel_id: id,
            });
            const useable_messages = messages.filter(message => {
                if (message.body) {
                    message.body = markup(message.body);
                    message.write_date = this.timeFormat(message.write_date);
                }

                return message.body && message.message_type !== "notification";
            });

            const message_list = useable_messages.reverse();
            messages_container[id] = message_list;
            if (message_list.length > 1) {
                const last_message = message_list[message_list.length - 1];
                last_message.body = last_message.body.replace(/<[^>]*>/g, "");
                this.last_message_list[id] = last_message;
            }
        }
    }

    async _bus_subscribe(ids, messages_container_list) {
        for (const id of ids) {
            this.busService.addChannel(`${id}`);
        }

        this.busService.subscribe("discuss.channel/new_message", payload => {
            if (!ids.includes(payload.id)) return;
            const messages_container = messages_container_list.find(item =>
                Object.keys(item).includes(payload.id.toString())
            );

            if (messages_container) {
                payload.message.body = markup(payload.message.body);
                payload.write_date = this.timeFormat(payload.write_date);
                messages_container[payload.id].push(payload.message);
                this.last_message_list[payload.id] = payload.message;
                this.last_message_list[payload.id].body =
                    this.last_message_list[payload.id].body.replace(
                        /<[^>]*>/g,
                        ""
                    );
                this.last_message_list[payload.id].write_date =
                    this.timeFormat(
                        this.last_message_list[payload.id].write_date
                    );
                this.last_message_notify[payload.id] = true;
            }
        });
        this.busService.subscribe("mail.record/insert", payload => {
            if (!payload.Message) return;
            const foundMessage = messages_container_list
                .flatMap(obj => Object.values(obj))
                .flat()
                .find(message => message.id === payload.Message.id);

            if (!foundMessage) return;

            if (payload.Message.body === "") {
                // 删除消息
                messages_container_list.forEach(container => {
                    Object.keys(container).forEach(key => {
                        const messageArray = container[key];
                        const indexToRemove = messageArray.findIndex(
                            message => message.id === foundMessage.id
                        );
                        if (indexToRemove !== -1) {
                            messageArray.splice(indexToRemove, 1);
                            console.log("消息已从容器中移除");
                        }
                    });
                });
            } else {
                // 更新消息内容
                foundMessage.body = markup(payload.Message.body);
            }
        });
    }

    onMessage({ detail: notifications }) {
        notifications = notifications.filter(
            item => item.payload.channel === this.channel
        );
    }

    async sendMessage(channel_id, text) {
        if (!text) return;
        await this.rpc("/tutoringCentre/api/tutorTalk/livechat/send_message", {
            channel_id,
            message: text,
        });
    }

    timeFormat(time) {
        const dateObject = new Date(time);
        const timePart = dateObject.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });

        return `${timePart}`;
    }
}

export const tutoringCentreLiveChat = {
    dependencies: [
        "rpc",
        "bus_service",
        "mail.messaging",
        "tutoringCentre_member",
    ],
    async start(env, services) {
        const tutoringCentreLiveChat = reactive(
            new TutoringCentreLiveChat(env, services)
        );
        await tutoringCentreLiveChat.setup(env, services);
        return tutoringCentreLiveChat;
    },
};
registry
    .category("services")
    .add("tutoringCentre_liveChat", tutoringCentreLiveChat);
