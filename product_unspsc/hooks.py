# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import tools, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    # Create an environment with superuser rights
    env = api.Environment(cr, SUPERUSER_ID, {})
    _load_unspsc_codes(env)
    _assign_codes_uom(env)
    demo_product = env.ref('product.consu_delivery_03', raise_if_not_found=False)
    if demo_product:
        _assign_codes_demo(env)


def uninstall_hook(env):
    env.cr.execute("DELETE FROM product_unspsc_code;")
    env.cr.execute("DELETE FROM ir_model_data WHERE model='product_unspsc_code';")


def _load_unspsc_codes(env):
    """Import CSV data as it is faster than XML and because we can't use noupdate
    anymore with CSV.
    Even with the faster CSVs, it would take +30 seconds to load it with the regular
    ORM methods, while here it is under 3 seconds.
    """
    csv_path = 'product_unspsc/data/product.unspsc.code.csv'
    with tools.misc.file_open(csv_path, 'rb') as csv_file:
        csv_file.readline()  # Skip header line
        env.cr.copy_expert(
            """COPY product_unspsc_code (code, name, applies_to, active)
               FROM STDIN WITH DELIMITER '|'""",
            csv_file
        )
    # Create xml_id to allow referencing this data
    env.cr.execute(
        """INSERT INTO ir_model_data
           (name, res_id, module, model, noupdate)
           SELECT concat('unspsc_code_', code), id, 'product_unspsc', 'product.unspsc.code', 't'
           FROM product_unspsc_code"""
    )


def _assign_codes_uom(env):
    """Assign the codes in UoM for each data record (data created above)."""
    tools.convert.convert_file(
        env.cr, 'product_unspsc', 'data/product_data.xml', None,
        mode='init', kind='data'
    )


def _assign_codes_demo(env):
    """Assign the codes in the demo products (used in demo invoices)."""
    tools.convert.convert_file(
        env.cr, 'product_unspsc', 'demo/product_demo.xml', None,
        mode='init'
    )

