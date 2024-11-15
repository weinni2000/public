import functools
import logging
import os
import pathlib

from werkzeug.exceptions import (
    NotFound,
)

import odoo
from odoo.http import Request

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    # works but is switched of to not block it.
    # id_bb_user = env.ref("bulletin_board_owl.bb_user").id
    id_bb_user = env.ref("base.public_user").id

    module_path = pathlib.Path(__file__).parent.absolute()
    with open(f"/{module_path}/bb_user_id.txt", "w") as f:
        f.write(str(id_bb_user))


def post_load():
    def _serve_db(self):
        """
        Prepare the user session and load the ORM before forwarding the
        request to ``_serve_ir_http``.
        """
        cr_readonly = None
        rule = None
        args = None
        not_found = None

        # reuse the same cursor for building+checking the registry and
        # for matching the controller endpoint
        try:
            self.registry, cr_readonly = self._open_registry()
            if self.session.uid is None:
                try:
                    module_path = pathlib.Path(__file__).parent.absolute()
                    file_path = f"/{module_path}/bb_user_id.txt"
                    if os.path.isfile(file_path):
                        with open(file_path) as f:
                            new_uid = f.read()
                            if new_uid:
                                new_uid = int(new_uid)
                except Exception as e:
                    _logger.info(f"Error while setting user id: {e}")
                    new_uid = self.session.id
            else:
                new_uid = self.session.uid

            self.env = odoo.api.Environment(cr_readonly, new_uid, self.session.context)
            try:
                rule, args = self.registry["ir.http"]._match(self.httprequest.path)
            except NotFound as not_found_exc:
                not_found = not_found_exc
        finally:
            if cr_readonly is not None:
                cr_readonly.close()

        if not_found:
            # no controller endpoint matched -> fallback or 404
            return self._transactioning(
                functools.partial(self._serve_ir_http_fallback, not_found),
                readonly=True,
            )

        # a controller endpoint matched -> dispatch it the request
        self._set_request_dispatcher(rule)
        readonly = rule.endpoint.routing["readonly"]
        if callable(readonly):
            readonly = readonly(rule.endpoint.func.__self__)
        return self._transactioning(
            functools.partial(self._serve_ir_http, rule, args),
            readonly=readonly,
        )

    Request._serve_db = _serve_db
