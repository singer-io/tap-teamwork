# tap-teamwork

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md

This tap:

- Pulls raw data from the [teamwork API].
- Extracts the following resources:

Collaborators [https://apidocs.teamwork.com/docs/spaces/v1/collaborators/get-v1-spaces-space-id-pages-page-id-collaborators-json]

Companies [https://apidocs.teamwork.com/docs/desk/v2/companies/get-v2-companies-json]

CompanyDetails [https://apidocs.teamwork.com/docs/desk/v2/companies/get-v2-companies-json]

Customers [https://apidocs.teamwork.com/docs/desk/v2/customers/get-v2-customers-json]

CustomerDetails [https://apidocs.teamwork.com/docs/desk/v2/customers/get-v2-search-customers-json]

Inboxes [https://apidocs.teamwork.com/docs/desk/v2/inboxes/get-v2-inboxes-json]

Milestones [https://apidocs.teamwork.com/docs/teamwork/v3/milestones/get-projects-api-v3-milestones-json]

Notebooks [https://apidocs.teamwork.com/docs/teamwork/v3/notebooks/get-projects-api-v3-notebooks-json]

Pages [https://apidocs.teamwork.com/docs/spaces/v1/pages/head-v1-pages-page-id-json]

Projects [https://apidocs.teamwork.com/docs/teamwork/v3/projects/get-projects-api-v3-projects-json]

Spaces [https://apidocs.teamwork.com/docs/spaces/v1/spaces/get-v1-spaces-json]

Tags [https://apidocs.teamwork.com/docs/spaces/v1/tags/get-v1-tags-json]

Tasks [https://apidocs.teamwork.com/docs/teamwork/v3/tasks/get-projects-api-v3-projects-project-id-tasks-json]

TicketDetails [https://apidocs.teamwork.com/docs/desk/v2/tickets/get-v2-search-tickets-json]

TicketPriorities [https://apidocs.teamwork.com/docs/desk/v2/ticket-priorities/get-v2-ticketpriorities-json]

Tickets [https://apidocs.teamwork.com/docs/desk/v2/tickets/post-v2-installations-installation-id-tickets-id-recover-json]

TicketSearch [https://apidocs.teamwork.com/docs/desk/v2/tickets/get-v2-search-tickets-json]

TicketTypes [https://apidocs.teamwork.com/docs/desk/v2/ticket-types/get-v2-tickettypes-json]

Users [https://apidocs.teamwork.com/docs/desk/v2/users/get-v2-me-json]

- Outputs the schema for each resource
- Incrementally pulls data based on the input state


## Streams


**collaborators** [https://apidocs.teamwork.com/docs/spaces/v1/collaborators/get-v1-spaces-space-id-pages-page-id-collaborators-json]

Data Key = collaborators

Primary keys: ['id']

Replication strategy: FULL_TABLE

**companies** [https://apidocs.teamwork.com/docs/desk/v2/companies/get-v2-companies-json]

Data Key = companies

Primary keys: ['id']

Replication strategy: INCREMENTAL

**company_details**[https://apidocs.teamwork.com/docs/desk/v2/companies/get-v2-companies-json]

Data Key = company

Primary keys: ['id']

Replication strategy: FULL_TABLE

**customers**[https://apidocs.teamwork.com/docs/desk/v2/customers/get-v2-customers-json]

Data Key = customers

Primary keys: ['id']

Replication strategy: FULL_TABLE

**customer_details**[https://apidocs.teamwork.com/docs/desk/v2/customers/get-v2-search-customers-json]

Data Key = customer

Primary keys: ['id']

Replication strategy: FULL_TABLE

**inboxes**[https://apidocs.teamwork.com/docs/desk/v2/inboxes/get-v2-inboxes-json]

Data Key = inboxes

Primary keys: ['id']

Replication strategy: INCREMENTAL

**milestones**[https://apidocs.teamwork.com/docs/teamwork/v3/milestones/get-projects-api-v3-milestones-json]

Data Key = milestones

Primary keys: ['id']

Replication strategy: INCREMENTAL

**notebooks**[https://apidocs.teamwork.com/docs/teamwork/v3/notebooks/get-projects-api-v3-notebooks-json]

Data Key = notebooks

Primary keys: ['id']

Replication strategy: INCREMENTAL

**pages**[https://apidocs.teamwork.com/docs/spaces/v1/pages/head-v1-pages-page-id-json]

Data Key = pages

Primary keys: ['id']

Replication strategy: FULL_TABLE

**projects**[https://apidocs.teamwork.com/docs/teamwork/v3/projects/get-projects-api-v3-projects-json]

Data Key = projects

Primary keys: ['id']

Replication strategy: INCREMENTAL

**spaces**[https://apidocs.teamwork.com/docs/spaces/v1/spaces/get-v1-spaces-json]

Data Key = spaces

Primary keys: ['id']

Replication strategy: INCREMENTAL

**tags**[https://apidocs.teamwork.com/docs/spaces/v1/tags/get-v1-tags-json]

Data Key = tags

Primary keys: ['id']

Replication strategy: FULL_TABLE

**tasks**[https://apidocs.teamwork.com/docs/teamwork/v3/tasks/get-projects-api-v3-projects-project-id-tasks-json]

Data Key = tasks

Primary keys: ['id']

Replication strategy: INCREMENTAL

**ticket_details**[https://apidocs.teamwork.com/docs/desk/v2/tickets/get-v2-search-tickets-json]

Data Key = ticket

Primary keys: ['id']

Replication strategy: FULL_TABLE

**ticket_priorities**[https://apidocs.teamwork.com/docs/desk/v2/ticket-priorities/get-v2-ticketpriorities-json]

Data Key = priorities

Primary keys: ['id']

Replication strategy: INCREMENTAL

**ticket_search**[https://apidocs.teamwork.com/docs/desk/v2/tickets/get-v2-search-tickets-json]

Data Key = tickets

Primary keys: ['id']

Replication strategy: INCREMENTAL

**ticket_types**[https://apidocs.teamwork.com/docs/desk/v2/ticket-types/get-v2-tickettypes-json]

Data Key = types

Primary keys: ['id']

Replication strategy: INCREMENTAL

**tickets**[https://apidocs.teamwork.com/docs/desk/v2/tickets/post-v2-installations-installation-id-tickets-id-recover-json]

Data Key = tickets

Primary keys: ['id']

Replication strategy: INCREMENTAL

**users**[https://apidocs.teamwork.com/docs/desk/v2/users/get-v2-me-json]

Data Key = users

Primary keys: ['id']

Replication strategy: INCREMENTAL



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
