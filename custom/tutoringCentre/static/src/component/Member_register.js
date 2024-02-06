/** @odoo-module */
import { Component, onWillStart, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MemberRegister extends Component {
    static template = "tutorTalk.member_register";
    static props = {};
    setup() {
        this.rpc = useService("rpc");
        this.router = useService("tutoringCentre_router");
        this.memberService = useService("TutoringCentreMember");
        this.state = useState({
            studentName: "",
            birthDate: null,
        });
    }

    async submitForm() {
        const response = await this.rpc("/tutoringCentre/api/createMember", {
            userID: this.memberService.user.id,
            studentName: this.state.studentName,
        });
        if (response) {
            this.memberService.state.registration = true;
            this.router.navigate("home");
        } else {
            this.memberService.state.registration = false;
            alert("未成功!");
        }
    }
}
