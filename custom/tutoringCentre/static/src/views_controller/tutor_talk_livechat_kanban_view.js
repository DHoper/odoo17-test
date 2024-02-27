/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanDropdownMenuWrapper } from "@web/views/kanban/kanban_dropdown_menu_wrapper";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { registry } from "@web/core/registry";

export class TutorTalkLivechatController extends KanbanController {
    setup() {
        super.setup(...arguments);
    }

    async openRecord(record) {
        if (!record.data.is_member) {
            return super.openRecord(record);
        }
        this.actionService.doAction("mail.action_discuss", {
            name: _t("Discuss"),
            additionalContext: { active_id: record.resId },
        });
    }
}

const tutorTalkLivechatTreeView = {
    ...kanbanView,
    Controller: TutorTalkLivechatController,
};

registry
    .category("views")
    .add(
        "tutoringCentre.tutor_talk_channel_kanban",
        tutorTalkLivechatTreeView
    );
