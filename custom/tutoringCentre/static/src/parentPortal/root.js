/** @odoo-module */
import { Component, onWillStart, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { cookie } from "@web/core/browser/cookie";
import { _t } from "@web/core/l10n/translation";

const serviceRegistry = registry.category("services");

export class Root extends Component {
    static template = "tutoringCentre.Root";
    static props = {};
    setup() {
        onWillStart(() => this.registerServiceWorker());
        // serviceRegistry.add("bus_service", busService);
        this.rpc = useService("rpc");
        this.liveChat = useState(useService("TutoringCentreLiveChat"));
        this.userName = _t("Visitor");
        this.channelInfo;
        this.state = useState({
            channelMessages: this.liveChat.channelMessages,
            text: "",
        });

        useEffect(
            () => {
                if (this.state.channelMessages.length > 0) {
                    console.log(66666666);
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

    async onClickSendMessage() {
        this.liveChat.sendMessage(this.state.text);
        console.log(this.state.channelMessages, 17117);
        console.log(this.liveChat.channelMessages, 9898);
    }

    registerServiceWorker() {
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker
                .register("/tutoringCentre/service-worker.js", {
                    scope: "/tutoringCentre/parentPortal",
                })
                .then(registration => {
                    if (Notification.permission !== "granted") {
                        Notification.requestPermission();
                    }
                })
                .catch(error => {
                    console.error("Service worker 註冊失敗, 錯誤:", error);
                });
        }
    }
}

// if ("serviceWorker" in navigator) {
//     navigator.serviceWorker
//         .register("./service-worker.js")
//         .then(registration => {
//             // 請求推送權限
//             if (Notification.permission !== "granted") {
//                 Notification.requestPermission().then(permission => {
//                     if (permission === "granted") {
//                         navigator.serviceWorker
//                             .getRegistration()
//                             .then(registration => {
//                                 const options = {
//                                     body: "測試測試22",
//                                 };
//                                 registration.showNotification(
//                                     "Notification Title",
//                                     options
//                                 );
//                             });
//                     }
//                 });
//             } else {
//                 // 如果權限已經被授予，即可開始定時推送通知
//                 // setInterval(displayNotification, 10000);
//             }
//         })
//         .catch(error => {
//             console.error("服務註冊錯誤:", error);
//         });
// }

// 定義推送通知的函數

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
