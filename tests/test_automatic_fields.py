from base import teamworkBaseTest
from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest

class teamworkAutomaticFields(MinimumSelectionTest, teamworkBaseTest):
    """With no user-selected fields, automatic fields (PK/RK) are still replicated."""

    @staticmethod
    def name():
        return "tap_tester_teamwork_automatic_fields_test"

    def streams_to_test(self):
        # All streams with data in this account.
        # Excluded: collaborators (same user appears across multiple spaces, non-unique PKs).
        return {
            "projects", "tasks", "milestones", "notebooks",
            "spaces", "tickets", "ticket_details", "users",
            "inboxes", "customers", "companies",
            "company_details", "customer_details", "ticket_search",
            "space_tags", "project_tags",
            "ticket_types", "ticket_priorities", "pages",
        }