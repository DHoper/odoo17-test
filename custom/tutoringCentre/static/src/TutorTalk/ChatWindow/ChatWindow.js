/** @odoo-module */

import { loadJS } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";
import {
    Component,
    useState,
    useEffect,
    useRef,
    onWillStart,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class ChatWindow extends Component {
    static template = "tutorTalk.ChatWindow";
    static props = ["close", "channel_info"];
    setup() {
        this.rpc = useService("rpc");
        this.liveChat = useService("tutoringCentre_liveChat");
        this.userName = _t("Visitor");
        this.member = useState(useService("tutoringCentre_member"));
        this.textarea = useRef("textarea");
        this.state = useState({
            channelMessages: null,
            text: "",
            parentPickLoading: false,
            parentPickShowPop: false,
            parentPickPopText: "",
            in_livechat: false,
        });

        onWillStart(() => {
            const id = this.props.channel_info.id;

            if (id in this.liveChat.live_channel_messages) {
                this.state.channelMessages =
                    this.liveChat.live_channel_messages[id];
                this.state.in_livechat = true;
            } else if (id in this.liveChat.announce_channel_messages) {
                this.state.channelMessages =
                    this.liveChat.announce_channel_messages[id];
                this.state.in_livechat = false;
            } else {
                console.error(
                    "tutoringCentre_liveChat 服務中找不到該頻道訊息"
                );
            }
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
    autoResize() {
        this.textarea.el.style.height = 0;
        this.textarea.el.style.height = `${Math.min(
            this.textarea.el.scrollHeight,
            100
        )}px`;
    }

    async parentPick() {
        this.state.parentPickLoading = true;
        const response = await this.rpc(
            "/tutoringCentre/api/tutorTalk/parentPickup",
            {
                childName: this.member.memberInfo.student[0].name,
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
        this.liveChat.sendMessage(this.props.channel_info.id, this.state.text);
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
