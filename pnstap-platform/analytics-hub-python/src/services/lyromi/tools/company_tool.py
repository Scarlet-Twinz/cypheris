from .database_tool import DatabaseTool


class CompanyTool:

    @staticmethod
    def get_all_companies():

        return DatabaseTool.execute("""
            SELECT
                company_name,
                industry,
                country,
                status
            FROM companies
            ORDER BY company_name;
        """)

    @staticmethod
    def count_companies():

        result = DatabaseTool.execute("""
            SELECT COUNT(*) AS total
            FROM companies;
        """)

        if result:
            return result[0]["total"]

        return 0