/** @odoo-module */
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { AnnouncementWindow } from "./AnnouncementWindow/AnnouncementWindow";
import { loadFile } from "@odoo/owl";

export class Announcement extends Component {
    static template = "announcement.Root";
    static components = { AnnouncementWindow };
    static props = {};
    setup() {
        this.rpc = useService("rpc");
        this.router = useService("tutoringCentre_router");
        this.member = useService("tutoringCentre_member");
        this.state = useState({
            current_course_id: null,
            current_course: {},
            courses: [],
            showWindow: false,
            animateClass: "",
        });
        this.openAnnounceWindow = this.openAnnounceWindow.bind(this);
        this.closeAnnounceWindow = this.closeAnnounceWindow.bind(this);

        onWillStart(async () => {
            const courses = this.member.memberInfo.student[0].courses;
            for (const course of courses) {
                this.state.courses.push(course);
            }
        });
    }

    openAnnounceWindow(id, name) {
        this.state.current_course = { id, name };
        this.state.animateClass = "animate__slideInRight";
        this.state.showWindow = true;
    }

    closeAnnounceWindow() {
        this.state.animateClass = "animate__slideOutRight";
        setTimeout(() => {
            this.state.showWindow = false;
        }, 750);
    }
}
