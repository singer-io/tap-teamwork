from tap_teamwork.streams.projects import Projects
from tap_teamwork.streams.tasks import Tasks
from tap_teamwork.streams.taskcomments import Taskcomments
from tap_teamwork.streams.taskdependencies import Taskdependencies
from tap_teamwork.streams.tasktags import Tasktags
from tap_teamwork.streams.taskboardcolumns import Taskboardcolumns
from tap_teamwork.streams.timesheets import Timesheets
from tap_teamwork.streams.timesheettotals import Timesheettotals
from tap_teamwork.streams.workloadplanners import Workloadplanners
from tap_teamwork.streams.milestones import Milestones
from tap_teamwork.streams.milestones_deadlines import MilestonesDeadlines
from tap_teamwork.streams.tasklists import Tasklists
from tap_teamwork.streams.notebooks import Notebooks
from tap_teamwork.streams.notebooks_comments import NotebooksComments
from tap_teamwork.streams.dashboards import Dashboards
from tap_teamwork.streams.forms import Forms
from tap_teamwork.streams.me_timers import MeTimers
from tap_teamwork.streams.projectcategories import Projectcategories
from tap_teamwork.streams.spaces import Spaces
from tap_teamwork.streams.pages import Pages
from tap_teamwork.streams.users import Users
from tap_teamwork.streams.tags import Tags
from tap_teamwork.streams.collaborators import Collaborators
from tap_teamwork.streams.activities import Activities
from tap_teamwork.streams.tickets import Tickets
from tap_teamwork.streams.ticket_details import TicketDetails
from tap_teamwork.streams.customers import Customers
from tap_teamwork.streams.customer_details import CustomerDetails
from tap_teamwork.streams.inboxes import Inboxes
from tap_teamwork.streams.inbox_details import InboxDetails
from tap_teamwork.streams.search_tickets import SearchTickets
from tap_teamwork.streams.threads import Threads
from tap_teamwork.streams.tickets_by_customer import TicketsByCustomer
from tap_teamwork.streams.ticket_notes import TicketNotes
from tap_teamwork.streams.audit_trail import AuditTrail
from tap_teamwork.streams.company_details import CompanyDetails
from tap_teamwork.streams.company_tickets import CompanyTickets
from tap_teamwork.streams.company_customers import CompanyCustomers
from tap_teamwork.streams.ticket_types import TicketTypes
from tap_teamwork.streams.ticket_priorities import TicketPriorities

STREAMS = {
    "projects": Projects,
    "tasks": Tasks,
    "taskcomments": Taskcomments,
    "taskdependencies": Taskdependencies,
    "tasktags": Tasktags,
    "taskboardcolumns": Taskboardcolumns,
    "timesheets": Timesheets,
    "timesheettotals": Timesheettotals,
    "workloadplanners": Workloadplanners,
    "milestones": Milestones,
    "milestones_deadlines": MilestonesDeadlines,
    "tasklists": Tasklists,
    "notebooks": Notebooks,
    "notebooks_comments": NotebooksComments,
    "dashboards": Dashboards,
    "forms": Forms,
    "me_timers": MeTimers,
    "projectcategories": Projectcategories,
    "spaces": Spaces,
    "pages": Pages,
    "users": Users,
    "tags": Tags,
    "collaborators": Collaborators,
    "activities": Activities,
    "tickets": Tickets,
    "ticket_details": TicketDetails,
    "customers": Customers,
    "customer_details": CustomerDetails,
    "inboxes": Inboxes,
    "inbox_details": InboxDetails,
    "search_tickets": SearchTickets,
    "threads": Threads,
    "tickets_by_customer": TicketsByCustomer,
    "ticket_notes": TicketNotes,
    "audit_trail": AuditTrail,
    "company_details": CompanyDetails,
    "company_tickets": CompanyTickets,
    "company_customers": CompanyCustomers,
    "ticket_types": TicketTypes,
    "ticket_priorities": TicketPriorities,
}
