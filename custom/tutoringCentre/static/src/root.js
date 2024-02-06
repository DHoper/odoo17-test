/** @odoo-module */
import {
    Component,
    onWillStart,
    useState,
    useEffect,
    reactive,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { ChatWindow } from "./TutorTalk/ChatWindow/ChatWindow";
import { MemberRegister } from "./component/Member_register";
import { Router } from "./router";

export class Root extends Component {
    static template = "tutorTalk.Root";
    static components = { Router, ChatWindow, MemberRegister };
    static props = {};
    async setup() {
        onWillStart(() => this.registerServiceWorker());
        this.rpc = useService("rpc");
        this.router = useService("tutoringCentre_router");
        this.memberService = useState(useService("TutoringCentreMember"));
        // this.state = useState({
        //     routerComponent: ChatWindow,
        // });

        // this.props = {
        //     changeRoute: this.changeRoute.bind(this),
        // };

        await this.memberService.init();

        // if (!this.memberService.state.registration) {
        //     this.state.routerComponent = MemberRegister;
        // }
    }

    // changeRoute(routeStr) {
    //     const routeComponent = {
    //         MemberRegister: MemberRegister,
    //         ChatWindow: ChatWindow,
    //     };

    //     const path = `/tutoringCentre/${routeStr}`;
    //     history.pushState({}, "", `${window.location.pathname}${path}`);

    //     this.state.routerComponent = routeComponent[routeStr];
    // }

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
