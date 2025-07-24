# tap-teamwork

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

This tap:

- Pulls raw data from the [teamwork API].
- Extracts the following resources:
    - [Projects](https://developer.teamwork.com/projects/api-v3/projects)

    - [Tasks](https://developer.teamwork.com/projects/api-v3/tasks)

    - [Taskcomments](https://developer.teamwork.com/projects/api-v3/comments)

    - [Taskdependencies](https://developer.teamwork.com/projects/api-v3/dependencies)

    - [Tasktags](https://developer.teamwork.com/projects/api-v3/tags)

    - [Taskboardcolumns](https://developer.teamwork.com/projects/api-v3/board-columns)

    - [Timesheets](https://developer.teamwork.com/projects/api-v3/timesheets)

    - [Timesheettotals](https://developer.teamwork.com/projects/api-v3/timesheets)

    - [Workloadplanners](https://developer.teamwork.com/projects/api-v3/workload)

    - [Milestones](https://developer.teamwork.com/projects/api-v3/milestones)

    - [MilestonesDeadlines](https://developer.teamwork.com/projects/api-v3/milestones)

    - [Tasklists](https://developer.teamwork.com/projects/api-v3/tasklists)

    - [Notebooks](https://developer.teamwork.com/projects/api-v3/notebooks)

    - [NotebooksComments](https://developer.teamwork.com/projects/api-v3/notebooks)

    - [Dashboards](https://developer.teamwork.com/projects/api-v3/dashboards)

    - [Forms](https://developer.teamwork.com/projects/api-v3/forms)

    - [MeTimers](https://developer.teamwork.com/projects/api-v3/timers)

    - [Projectcategories](https://developer.teamwork.com/projects/api-v3/categories)

    - [Spaces](https://developer.teamwork.com/)

    - [Pages](https://developer.teamwork.com/)

    - [Users](https://developer.teamwork.com/)

    - [Tags](https://developer.teamwork.com/)

    - [Collaborators](https://developer.teamwork.com/)

    - [Activities](https://developer.teamwork.com/)

    - [Tickets](https://developer.teamwork.com/)

    - [TicketDetails](https://developer.teamwork.com/)

    - [Customers](https://developer.teamwork.com/)

    - [CustomerDetails](https://developer.teamwork.com/)

    - [Inboxes](https://developer.teamwork.com/)

    - [InboxDetails](https://developer.teamwork.com/)

    - [SearchTickets](https://developer.teamwork.com/)

    - [Threads](https://developer.teamwork.com/)

    - [TicketsByCustomer](https://developer.teamwork.com/)

    - [TicketNotes](https://developer.teamwork.com/)

    - [AuditTrail](https://developer.teamwork.com/)

    - [CompanyDetails](https://developer.teamwork.com/)

    - [CompanyTickets](https://developer.teamwork.com/)

    - [CompanyCustomers](https://developer.teamwork.com/)

    - [TicketTypes](https://developer.teamwork.com/)

    - [TicketPriorities](https://developer.teamwork.com/)

- Outputs the schema for each resource
- Incrementally pulls data based on the input state


## Streams


** [projects](https://developer.teamwork.com/projects/api-v3/projects)**
- Data Key = projects
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [tasks](https://developer.teamwork.com/projects/api-v3/tasks)**
- Data Key = tasks
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [taskcomments](https://developer.teamwork.com/projects/api-v3/comments)**
- Data Key = comments
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [taskdependencies](https://developer.teamwork.com/projects/api-v3/dependencies)**
- Data Key = dependencies
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [tasktags](https://developer.teamwork.com/projects/api-v3/tags)**
- Data Key = tags
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [taskboardcolumns](https://developer.teamwork.com/projects/api-v3/board-columns)**
- Data Key = columns
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [timesheets](https://developer.teamwork.com/projects/api-v3/timesheets)**
- Data Key = timesheets
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [timesheettotals](https://developer.teamwork.com/projects/api-v3/timesheets)**
- Data Key = totals
- Primary keys: ['userId']
- Replication strategy: FULL_TABLE

** [workloadplanners](https://developer.teamwork.com/projects/api-v3/workload)**
- Data Key = planners
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [milestones](https://developer.teamwork.com/projects/api-v3/milestones)**
- Data Key = milestones
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [milestones_deadlines](https://developer.teamwork.com/projects/api-v3/milestones)**
- Data Key = deadlines
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [tasklists](https://developer.teamwork.com/projects/api-v3/tasklists)**
- Data Key = tasklists
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [notebooks](https://developer.teamwork.com/projects/api-v3/notebooks)**
- Data Key = notebooks
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [notebooks_comments](https://developer.teamwork.com/projects/api-v3/notebooks)**
- Data Key = comments
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [dashboards](https://developer.teamwork.com/projects/api-v3/dashboards)**
- Data Key = dashboards
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [forms](https://developer.teamwork.com/projects/api-v3/forms)**
- Data Key = forms
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [me_timers](https://developer.teamwork.com/projects/api-v3/timers)**
- Data Key = timers
- Primary keys: ['id']
- Replication strategy: INCREMENTAL

** [projectcategories](https://developer.teamwork.com/projects/api-v3/categories)**
- Data Key = categories
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [spaces](https://developer.teamwork.com/)**
- Data Key = spaces
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [pages](https://developer.teamwork.com/)**
- Data Key = pages
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [users](https://developer.teamwork.com/)**
- Data Key = users
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [tags](https://developer.teamwork.com/)**
- Data Key = tags
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [collaborators](https://developer.teamwork.com/)**
- Data Key = collaborators
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [activities](https://developer.teamwork.com/)**
- Data Key = activities
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [tickets](https://developer.teamwork.com/)**
- Data Key = tickets
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [ticket_details](https://developer.teamwork.com/)**
- Data Key = ticket_details
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [customers](https://developer.teamwork.com/)**
- Data Key = customers
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [customer_details](https://developer.teamwork.com/)**
- Data Key = customer_details
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [inboxes](https://developer.teamwork.com/)**
- Data Key = inboxes
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [inbox_details](https://developer.teamwork.com/)**
- Data Key = inbox_details
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [search_tickets](https://developer.teamwork.com/)**
- Data Key = search_tickets
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [threads](https://developer.teamwork.com/)**
- Data Key = threads
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [tickets_by_customer](https://developer.teamwork.com/)**
- Data Key = tickets_by_customer
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [ticket_notes](https://developer.teamwork.com/)**
- Data Key = ticket_notes
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [audit_trail](https://developer.teamwork.com/)**
- Data Key = audit_trail
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [company_details](https://developer.teamwork.com/)**
- Data Key = company_details
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [company_tickets](https://developer.teamwork.com/)**
- Data Key = company_tickets
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [company_customers](https://developer.teamwork.com/)**
- Data Key = company_customers
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [ticket_types](https://developer.teamwork.com/)**
- Data Key = ticket_types
- Primary keys: ['id']
- Replication strategy: FULL_TABLE

** [ticket_priorities](https://developer.teamwork.com/)**
- Data Key = ticket_priorities
- Primary keys: ['id']
- Replication strategy: FULL_TABLE



## Authentication

## Quick Start

1. Install

    Clone this repository, and then install using setup.py. We recommend using a virtualenv:

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > python setup.py install
    OR
    > cd .../tap-teamwork
    > pip install -e .
    ```
2. Dependent libraries. The following dependent libraries were installed.
    ```bash
    > pip install singer-python
    > pip install target-stitch
    > pip install target-json
    
    ```
    - [singer-tools](https://github.com/singer-io/singer-tools)
    - [target-stitch](https://github.com/singer-io/target-stitch)

3. Create your tap's `config.json` file.  The tap config file for this tap should include these entries:
   - `start_date` - the default value to use if no bookmark exists for an endpoint (rfc3339 date string)
   - `user_agent` (string, optional): Process and email for API logging purposes. Example: `tap-teamwork <api_user_email@your_company.com>`
   - `request_timeout` (integer, `300`): Max time for which request should wait to get a response. Default request_timeout is 300 seconds.
   
    ```json
    {
        "start_date": "2019-01-01T00:00:00Z",
        "user_agent": "tap-teamwork <api_user_email@your_company.com>",
        "request_timeout": 300,
        ...
    }```

    Optionally, also create a `state.json` file. `currently_syncing` is an optional attribute used for identifying the last object to be synced in case the job is interrupted mid-stream. The next run would begin where the last job left off.

    ```json
    {
        "currently_syncing": "engage",
        "bookmarks": {
            "export": "2019-09-27T22:34:39.000000Z",
            "funnels": "2019-09-28T15:30:26.000000Z",
            "revenue": "2019-09-28T18:23:53Z"
        }
    }
    ```

4. Run the Tap in Discovery Mode
    This creates a catalog.json for selecting objects/fields to integrate:
    ```bash
    tap-teamwork --config config.json --discover > catalog.json
    ```
   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md

5. Run the Tap in Sync Mode (with catalog) and [write out to state file](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md

    For Sync mode:
    ```bash
    > tap-teamwork --config tap_config.json --catalog catalog.json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To load to json files to verify outputs:
    ```bash
    > tap-teamwork --config tap_config.json --catalog catalog.json | target-json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To pseudo-load to [Stitch Import API](https://github.com/singer-io/target-stitch) with dry run:
    ```bash
    > tap-teamwork --config tap_config.json --catalog catalog.json | target-stitch --config target_config.json --dry-run > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

6. Test the Tap
    
    While developing the teamwork tap, the following utilities were run in accordance with Singer.io best practices:
    Pylint to improve [code quality](https://github.com/singer-io/getting-started/blob/master/docs/BEST_PRACTICES.md
    ```bash
    > pylint tap_teamwork -d missing-docstring -d logging-format-interpolation -d too-many-locals -d too-many-arguments
    ```
    Pylint test resulted in the following score:
    ```bash
    Your code has been rated at 9.67/10
    ```

    To [check the tap](https://github.com/singer-io/singer-tools
    ```bash
    > tap_teamwork --config tap_config.json --catalog catalog.json | singer-check-tap > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

    #### Unit Tests

    Unit tests may be run with the following.

    ```
    python -m pytest --verbose
    ```

    Note, you may need to install test dependencies.

    ```
    pip install -e .'[dev]'
    ```
---

Copyright &copy; 2019 Stitch
