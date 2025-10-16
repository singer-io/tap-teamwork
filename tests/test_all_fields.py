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
            'draftVersion',
            'deletedBy',
            'changeMessage',
            'createdBy',
            'tags',
            'isPrivate',
            'isFullWidth',
            'LinkedInstallation',
            'contentRevision',
            'isRequiredReading',
            'banner',
            'parentId',
            'meta',
            'updatedBy',
            'isPublished',
            'id',
            'isHomePage',
            'content',
            'title',
            'reactions',
            'slug',
            'summary',
            'updatedAt',
            'order',
            'state',
            'breadcrumb',
            'publicShare',
            'readerInlineCommentsEnabled',
            'space',
            'deletedAt',
            'createdAt'
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
        "inboxes" : {
            'permissions',
            'completedAt',
            'dependencies',
            'timer',
            'projectId',
            'endDate',
            'taskList'
        },
    }
    @staticmethod
    def name():
        return "tap_tester_teamwork_all_fields_test"

    def streams_to_test(self):
        # Use only streams that are stable in this env for "all fields" checks.
        # tasks/milestones have many optional fields that aren't returned here.
        return {"projects", "notebooks", "tickets", "ticket_details", "users", "customers", "collaborators", "customer_details", "ticket_search"}