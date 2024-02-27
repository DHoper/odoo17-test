/** @odoo-module */
import { Component, onWillStart, onRendered, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Home } from "./Home/Home";
import { MemberRegister } from "./pages/Member_register";
import { TutorTalk } from "./TutorTalk/TutorTalk";
import { Router } from "./router";

export class Root extends Component {
    static template = "tutoringCentre.Root";
    static components = {
        Router,
        Home,
        TutorTalk,
        MemberRegister,
    };
    static props = {};
    async setup() {
        onWillStart(() => {
            this.registerServiceWorker();
        });
        this.rpc = useService("rpc");
        this.router = useState(useService("tutoringCentre_router"));
        this.memberService = useState(useService("tutoringCentre_member"));

        this.state = useState({
            currentRoute: "default",
        });

        this.navigate = this.navigate.bind(this);
    }

    navigate(route) {
        this.router.navigate(route);
        this.state.currentRoute = route;
    }

    registerServiceWorker() {
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker
                .register("/tutoringCentre/service-worker", {
                    scope: "/tutoringCentre",
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
