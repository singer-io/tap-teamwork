from base import teamworkBaseTest
from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest

class teamworkAutomaticFields(MinimumSelectionTest, teamworkBaseTest):
    """With no user-selected fields, automatic fields (PK/RK) are still replicated."""

    @staticmethod
    def name():
        return "tap_tester_teamwork_automatic_fields_test"

    def streams_to_test(self):
        # Limit to streams that reliably have data in this account
        # (Avoiding empty/rare streams like pages, collaborators, customers, etc.)
        return {
            "projects",
            "tasks",
            "milestones",
            "notebooks",
            "ticket_details",
            "customer_details",
            "inboxes",
            'spaces',
            'customers',
            'tickets',
            'ticket_search',
            'users'
        }