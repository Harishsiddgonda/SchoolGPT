# SchoolGPT Stakeholder Roles & Access Control
### RSR Technologies Enterprise AI Platform

SchoolGPT implements strict Role-Based Access Control (RBAC) across all features and document searches:

| Priority | Role | Purpose & Privileges | Authorized Document Scope |
| :---: | :--- | :--- | :--- |
| **100** | **Super Admin** | Full system configuration, AI model switching, server telemetry, user management, unrestricted document access. | All documents (including system & sensitive audits) |
| **90** | **School Administrator** | Operations management, user account provisioning, role assignment, policy uploads. | Administrative policies, staff records, circulars, general docs |
| **80** | **Principal** | Executive oversight, performance analytics, confidential school policies, disciplinary guidelines. | Confidential school policies, staff circulars, general docs |
| **60** | **Teacher** | Curriculum materials, syllabus updates, exam schedules, lesson plans, student guidance. | Academic syllabus, exam schedules, student rules, circulars |
| **40** | **Parent** | Fee structures, payment schedules, school bus routes, transport policies, holiday notices, PTA meetings. | Fee policies, transport routes, school calendar, notices |
| **20** | **Student** | Student handbook, code of conduct, library guidelines, club schedules, examination dates, homework guidelines. | Student handbooks, timetables, clubs, library rules |

---

### Document-Level Authorization Guarantee
When a user submits a query:
1. The user's role priority is verified.
2. The RAG vector query filters out all document chunks whose `min_role` requirement exceeds the user's priority.
3. Information from confidential documents is never leaked to unauthorized roles.
