{
    "name": "demo",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "author": "mytime.click",
    "website": "https://github.com/OCA/partner-contact",
    "category": "Uncategorized",
    "version": "18.0.1.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": ["data/res_users.xml"],
    "post_load": "post_load",
    "post_init_hook": "post_init_hook",
}
