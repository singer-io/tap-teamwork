from tap_teamwork.streams.projects import Projects
from tap_teamwork.streams.tasks import Tasks
from tap_teamwork.streams.milestones import Milestones
from tap_teamwork.streams.notebooks import Notebooks
from tap_teamwork.streams.spaces import Spaces
from tap_teamwork.streams.tickets import Tickets
from tap_teamwork.streams.ticket_details import TicketDetails
from tap_teamwork.streams.users import Users
from tap_teamwork.streams.inboxes import Inboxes
from tap_teamwork.streams.ticket_types import TicketTypes
from tap_teamwork.streams.customers import Customers
from tap_teamwork.streams.companies import Companies
from tap_teamwork.streams.pages import Pages
from tap_teamwork.streams.tags import Tags
from tap_teamwork.streams.collaborators import Collaborators
from tap_teamwork.streams.company_details import CompanyDetails
from tap_teamwork.streams.customer_details import CustomerDetails
from tap_teamwork.streams.ticket_search import TicketSearch
from tap_teamwork.streams.ticket_priorities import TicketPriorities
from singer import get_logger
LOGGER = get_logger()


# Define streams
STREAMS = [
    Tickets,
    TicketDetails,
    Projects,
    Tasks,
    Milestones,
    Notebooks,
    Spaces,
    Users,
    Inboxes,
    TicketTypes,
    Customers,
    Companies,
    Pages,
    Tags,
    Collaborators,
    CompanyDetails,
    CustomerDetails,
    TicketSearch,
    TicketPriorities
]

# Parent-child binding logic
for child_cls in STREAMS:
    if hasattr(child_cls, "parent_stream_type"):
        for parent_cls in STREAMS:
            if (
                isinstance(child_cls.parent_stream_type, str) and
                parent_cls.__name__ == child_cls.parent_stream_type
            ) or (
                isinstance(child_cls.parent_stream_type, type) and
                issubclass(parent_cls, child_cls.parent_stream_type)
            ):
                if not hasattr(parent_cls, "child_to_sync"):
                    parent_cls.child_to_sync = []
                parent_cls.child_to_sync.append(child_cls)
                LOGGER.info(f"Bound child stream {child_cls.tap_stream_id} to parent {parent_cls.tap_stream_id}")
