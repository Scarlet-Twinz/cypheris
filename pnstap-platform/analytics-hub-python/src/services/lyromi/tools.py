from .context import EnterpriseContext


class Tools:

    @staticmethod
    def get_enterprise_context():
        return EnterpriseContext.build()

    @staticmethod
    def get_system_summary():

        context = EnterpriseContext.build()

        return f"""
Organization: {context['organization']}
Companies: {context['companies']}
Users: {context['users']}
"""