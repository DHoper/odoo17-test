/** @odoo-module */

import { loadJS } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";
import { Component, useState, useEffect, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class ChatWindow extends Component {
    static template = "tutorTalk.ChatWindow";

    setup() {
        this.rpc = useService("rpc");
        this.liveChat = useService("tutoringCentre_liveChat");
        this.userName = _t("Visitor");
        this.member = useState(useService("tutoringCentre_member"));
        this.channelInfo;
        this.textarea = useRef("textarea");
        this.state = useState({
            channelMessages: this.liveChat.channelMessages,
            text: "",
            parentPickLoading: false,
            parentPickShowPop: false,
            parentPickPopText: "",
        });

        useEffect(
            () => {
                if (this.state.channelMessages.length > 0) {
                    displayNotification(
                        `你有新訊息!:${this.state.channelMessages[-1]}`
                    );
                }
            },
            () => [this.state.channelMessages.length]
        );
    }

    get sanitizedMessages() {
        return this.state.channelMessages.map(message => ({
            ...message,
            sanitizedBody: message.body.replace(/<[^>]*>/g, ""),
        }));
    }

    autoResize() {
        this.textarea.el.style.height = 0;
        this.textarea.el.style.height = `${Math.min(
            this.textarea.el.scrollHeight,
            100
        )}px`;
    }

    timeFormat(time) {
        const dateObject = new Date(time);

        const datePart = dateObject.toISOString().split("T")[0];
        const timePart = dateObject.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });

        return `${timePart}`;
    }
    async parentPick() {
        console.log(7788, this.member.memberInfo, 7878787);
        this.state.parentPickLoading = true;
        const response = await this.rpc(
            "/tutoringCentre/TutorTalk/api/parentPickup",
            {
                childName: this.member.memberInfo.student.name,
            }
        );
        if (response) {
            this.state.parentPickLoading = false;
            this.state.parentPickPopText = "通知成功，請前往接送小朋友。";
            document.getElementById("parentPick").showModal();
        } else {
            this.state.parentPickLoading = true;
            this.state.parentPickPopText =
                "通知失敗，請再嘗試一次，或聯絡客服人員。";
            document.getElementById("parentPick").showModal();
        }
    }
    async onClickSendMessage() {
        this.liveChat.sendMessage(this.state.text);
        this.state.text = "";
    }
}

function displayNotification(message) {
    if (Notification.permission === "granted") {
        navigator.serviceWorker
            .getRegistration()
            .then(registration => {
                if (registration) {
                    const options = {
                        body: message,
                        vibrate: [200, 100, 200],
                    };

                    registration.showNotification("新訊息", options);
                }
            })
            .catch(err => {
                console.error("Error getting registration:", err);
            });
    }
}
