from base import teamworkBaseTest
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest

class teamworkAllFields(AllFieldsTest, teamworkBaseTest):
    
    MISSING_FIELDS = {
        "customer_details" : {
            'permission',
            'password',
            'addMethod',
            'deletedAt',
            'company'
        },
        "users" : {
            'deletedBy',
            'LinkedCompany',
            'deletedAt',
            'LinkedInstallation'
        },
        "spaces" : {
            'deletedBy',
            'LinkedCompany',
            'projectId',
            'deletedAt'
        },
        "collaborators" : {
            'meta'
        },
        "ticket_details" : {
            'companies_id',
            'priority',
            'customerContact',
            'businesshoursId',
            'hasAttachments',
            'BCC',
            'spamScore',
            'numThreads',
            'companyCustomers',
            'fields',
            'happinessRating',
            'createdByUser',
            'tags',
            'threads',
            'inboxName',
            'externalId',
            'CC',
            'preview',
            'inboxId',
            'hasTimeLogged',
            'assignedTo',
            'reviewStatus'
        },
        "pages" : {
            'deletedBy',
            'LinkedInstallation',
            'deletedAt'
        },
        "ticket_search" : {
            'deletedBy',
            'customFields',
            'tags',
            'dueAt',
            'reactions',
            'priorityId',
            'closedAt',
            'sourceId',
            'files',
            'inboxId',
            'customerId',
            'typeId',
            'deletedAt',
            'statusId',
            'body'
        },
        "milestones" : {
            'latestUpdates'
            'numCommentsRead',
            'completedBy',
            'completerId',
            'percentageComplete',
            'lockdownId',
            'lockdown',
            'completedOn',
            'percentageTasksCompleted'
        },
        "tickets" : {
            'isRead',
            'hasAttachments',
            'priorityId',
            'priorityColor',
            'deletedByUserId',
            'readonly',
            'inboxId',
            'numActiveTasks',
            'numThreads',
            'reviewStatus',
            'responseTimes',
            'spam_score',
            'numCompletedTasks',
            'company'
        },
        "inboxes" : {
            'deletedBy',
            'ticketstatus',
            'createdBy',
            'syncAccountId',
            'updatedBy',
            'useTeamworkMailServer',
            'smtpProvider',
            'autoReplyFromUserId',
            'autoReplyEnabled',
            'synced',
            'iconImage',
            'clientOnly',
            'state',
            'smtpPassword',
            'smtpSecurity',
            'smtpServer',
            'smtpPort',
            'createdAt',
            'smtpUsername',
            'autoReplySubject',
            'syncSubscriptionId',
            'spamThreshold',
            'displayOrder',
            'publicIconImage',
            'usingOfficeHours',
            'updatedAt',
            'autoReplyMessage',
            'user',
            'syncDays',
            'starred',
            'deletedAt',
            'localPart'
        },
        "companies" : {
            'deletedBy',
            'address',
            'deletedAt'
        },
        "company_details" : {
            'deletedBy',
            'address',
            'deletedAt'
        },
        "space_tags" : {
            'deletedBy',
            'pageCount',
            'deletedAt'
        },
        "project_tags" : {
            'count'
        },
        "ticket_priorities" : {
            'deletedAt',
            'deletedBy',
            'filter_args',
            'ticketCount'
        },
    }
    @staticmethod
    def name():
        return "tap_tester_teamwork_all_fields_test"

    def streams_to_test(self):
        # All streams with data in this env.
        # tasks/milestones excluded: many optional fields not returned.
        return {
            "projects", "notebooks", "tickets", "ticket_details",
            "users", "customers", "collaborators", "customer_details",
            "ticket_search", "companies", "company_details",
            "inboxes", "space_tags", "project_tags",
            "ticket_types", "ticket_priorities", "pages",
        }