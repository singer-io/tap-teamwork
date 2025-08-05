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

STREAMS = {
    "projects": Projects,
    "tasks": Tasks,
    "milestones": Milestones,
    "notebooks": Notebooks,
    "spaces": Spaces,
    "tickets": Tickets,
    "ticket_details": TicketDetails,
    "users": Users,
    "inboxes": Inboxes,
    "ticket_types": TicketTypes,
    "customers": Customers,
    "companies": Companies,
    "pages": Pages,
    "tags": Tags,
    "collaborators": Collaborators,
    "company_details": CompanyDetails,
    "customer_details": CustomerDetails,
    "ticket_search": TicketSearch,
    "ticket_priorities": TicketPriorities,
}
