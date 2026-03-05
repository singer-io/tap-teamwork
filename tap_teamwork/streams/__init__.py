"""
Initialize and register all stream classes for the tap-teamwork connector.
"""

from tap_teamwork.streams.projects import Projects
from tap_teamwork.streams.tasks import Tasks
from tap_teamwork.streams.milestones import Milestones
from tap_teamwork.streams.notebooks import Notebooks
from tap_teamwork.streams.spaces import Spaces
from tap_teamwork.streams.users import Users
from tap_teamwork.streams.inboxes import Inboxes
from tap_teamwork.streams.ticket_types import TicketTypes
from tap_teamwork.streams.tickets import Tickets
from tap_teamwork.streams.ticket_details import TicketDetails
from tap_teamwork.streams.customers import Customers
from tap_teamwork.streams.customer_details import CustomerDetails
from tap_teamwork.streams.companies import Companies
from tap_teamwork.streams.company_details import CompanyDetails
from tap_teamwork.streams.pages import Pages
from tap_teamwork.streams.collaborators import Collaborators
from tap_teamwork.streams.ticket_search import TicketSearch
from tap_teamwork.streams.ticket_priorities import TicketPriorities
from tap_teamwork.streams.project_tags import ProjectTags
from tap_teamwork.streams.space_tags import SpaceTags

# Dictionary mapping stream names to their classes
STREAMS = {
    "projects": Projects,
    "tasks": Tasks,
    "milestones": Milestones,
    "notebooks": Notebooks,
    "spaces": Spaces,
    "users": Users,
    "inboxes": Inboxes,
    "ticket_types": TicketTypes,
    "tickets": Tickets,
    "ticket_details": TicketDetails,
    "customers": Customers,
    "customer_details": CustomerDetails,
    "companies": Companies,
    "company_details": CompanyDetails,
    "pages": Pages,
    "collaborators": Collaborators,
    "ticket_search": TicketSearch,
    "ticket_priorities": TicketPriorities,
    "project_tags": ProjectTags,
    "space_tags": SpaceTags
}
