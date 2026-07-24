# Changelog

## 0.3.0
  * Converted child streams (`collaborators`, `pages`, `ticket_details`, `company_details`) to INCREMENTAL replication using the parent's `updatedAt` and added `ParentBaseStream` for coordinated bookmark management. [#24](https://github.com/singer-io/tap-teamwork/pull/24)

## 0.2.0
  * Streams that the credentials cannot access (403) are now excluded from the catalog during discovery instead of raising an error. [#23](https://github.com/singer-io/tap-teamwork/pull/23)

## 0.1.0
  * Updated python version. [#19](https://github.com/singer-io/tap-teamwork/pull/19)
  * Added integration tests.

## 0.0.1
  * Initial Commit
