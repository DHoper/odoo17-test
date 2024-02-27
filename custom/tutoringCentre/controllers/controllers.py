from odoo.http import request, route, Controller
from odoo.fields import Command
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
import logging


_logger = logging.getLogger(__name__)


class TutoringCentreController(Controller):
    @add_guest_to_context
    @route(
        "/tutoringCentre/api/userInfo",
        type="json",
        auth="public",
    )
    def _get_user_info(self):
        return request.env.user.read()[0]

    @route(
        "/tutoringCentre/api/createMember",
        type="json",
        auth="public",
    )
    def _create_member(self, studentName, course_ids, channel_ids):
        user_id = request.env.user.id
        new_member = (
            request.env["tutoring_centre.member"]
            .sudo()
            .create_member(user_id, studentName, course_ids, channel_ids)
        )

        return new_member.read()

    @route(
        "/tutoringCentre/api/memberInfo",
        type="json",
        auth="public",
    )
    def _get_member_info(self, userID):
        member = (
            request.env["tutoring_centre.member"]
            .sudo()
            .search([("portal_user", "=", userID)], limit=1)
        )

        if not member:
            return False

        student_data = member.student.read()
        for student in student_data:
            student["courses"] = member.student.filtered(
                lambda s: s.id == student["id"]
            ).courses.read()

        member_values = member.read()[0]
        member_values["student"] = student_data

        return member_values

    @route(
        ["/tutoringCentre", "/tutoringCentre/<path:subpath>"],
        auth="public",
        website=True,
        sitemap=True,
    )
    def _render_tutoringCentre(self, config_id=None):
        return request.render(
            "tutoringCentre.root",
            {
                "session_info": request.env["ir.http"].get_frontend_session_info(),
            },
        )
