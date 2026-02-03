# Project Title: Greenfield University Instant Library

## Description
At Greenfield University, the BSC Computer Science department faces a shortage of physical textbooks due to a growing student population. The limited availability of library resources has led to long wait times and challenges in accessing essential study materials.
To solve this, the university’s Cloud Solutions Department developed the Instant Library—a virtual library platform. Using Flask for backend development, AWS EC2 for hosting, and DynamoDB for managing data, the system allows students to register, log in, and request books online. AWS SNS sends real-time notifications to students and library staff about requests, ensuring effective communication and resource management. This cloud-based solution enhances the availability of study materials, providing seamless access for all students.

## Scenarios

### Scenario 1: Efficient Book Request System for Students
In the Instant Library System at Greenfield University, AWS EC2 ensures a reliable infrastructure to manage multiple students accessing the platform simultaneously. For example, a student can log in, navigate to the book request page, and easily submit a request for unavailable textbooks. Flask handles backend operations, efficiently retrieving and processing user data in real-time. The cloud-based architecture allows the platform to handle a high volume of book requests during peak periods, ensuring smooth operation without delays.

### Scenario 2: Seamless Book Request Notifications for Library Staff
When students request books that are unavailable in the physical library, the Instant Library System uses AWS SNS to notify both the students and the library staff. For instance, a student requests a textbook, and Flask processes the request while SNS sends an email to both the student (confirming the request) and the library staff (informing them of the new request). The secure integration with AWS DynamoDB stores all book requests, ensuring they are tracked and resolved efficiently.

### Scenario 3: Easy Access to Library Resources
The Instant Library System provides students with easy access to available resources in the library. For example, a student logs in and views the list of available books and materials on the platform. They can quickly check the availability status or place a request if the book is not in stock. Flask manages real-time data fetching from DynamoDB, while EC2 hosting ensures the platform performs seamlessly even when multiple students access it at the same time, offering a smooth and uninterrupted user experience.

## Architecture

This AWS-based architecture powers a scalable and secure web application using Amazon EC2 for hosting the backend, with a lightweight framework like Flask handling core logic. Application data is stored in Amazon DynamoDB, ensuring fast, reliable access, while user access is managed through AWS IAM for secure authentication and control. Real-time alerts and system notifications are enabled via Amazon SNS, enhancing communication and user engagement.

```mermaid
flowchart LR
    %% =====================
    %% USERS
    %% =====================
    U1[👤 Student]
    U2[👤 Library Staff]

    %% =====================
    %% FRONTEND
    %% =====================
    subgraph FRONTEND["HTML Interface"]
        F1[🔍 Search Catalog]
        F2[📖 Request Book]
        F3[👁 View Request Status]
        F4[🔐 Register / Login]
    end

    %% =====================
    %% AUTH
    %% =====================
    Login[Login]
    Confirm[Confirm Availability]

    %% =====================
    %% AWS CLOUD
    %% =====================
    subgraph AWS["AWS Cloud"]
        
        %% ---------------------
        %% FLASK APP
        %% ---------------------
        subgraph FLASK["Flask Application"]
            API[⚗ Flask API]
            HTTPS[🔒 HTTPS]
        end

        %% ---------------------
        %% COMPUTE & SECURITY
        %% ---------------------
        EC2[🖥 AWS EC2]
        VPC[🌐 AWS VPC]
        IAM[🔐 AWS IAM]

        %% ---------------------
        %% DATABASE
        %% ---------------------
        DB[(📦 Amazon DynamoDB)]

        %% ---------------------
        %% NOTIFICATION
        %% ---------------------
        subgraph SNS["AWS SNS"]
            Topic[📢 SNS Topic]
            MailStudent[✉ Email to Student]
            MailStaff[✉ Email to Staff]
        end
    end

    %% =====================
    %% USER FLOWS
    %% =====================
    U1 -->|via Frontend| F1
    U1 --> F2
    U1 --> F3
    U1 --> F4

    U2 -->|via Frontend| F3
    U2 --> Confirm

    %% =====================
    %% FRONTEND → BACKEND
    %% =====================
    F1 -->|HTTPS| API
    F2 -->|HTTPS| API
    F3 -->|HTTPS| API
    F4 -->|HTTPS| API

    %% =====================
    %% BACKEND INTERNAL
    %% =====================
    API --> EC2
    EC2 --> VPC
    API --> IAM
    API --> HTTPS

    %% =====================
    %% DATABASE ACCESS
    %% =====================
    API -->|CRUD user/book request| DB

    %% =====================
    %% NOTIFICATIONS
    %% =====================
    API -->|trigger notification| Topic
    Topic -->|new request| MailStaff
    Topic -->|request processed| MailStudent
```

## Entity Relationship (ER) Diagram

An ER (Entity-Relationship) diagram visually represents the logical structure of a database by defining entities, their attributes, and the relationships between them. It helps organize data efficiently by illustrating how different components of the system interact and relate. This structured approach supports effective database normalization, data integrity, and simplified query design.

```mermaid
flowchart LR

    %% =====================
    %% ENTITIES
    %% =====================
    Users[Users]
    Requests[Requests]

    %% =====================
    %% RELATIONSHIP
    %% =====================
    Makes{Makes}

    %% =====================
    %% USERS ATTRIBUTES
    %% =====================
    U1((username))
    U2((email))
    U3((password))

    %% =====================
    %% REQUESTS ATTRIBUTES
    %% =====================
    R0((request_id PK))
    R1((sender))
    R2((email))
    R3((book_name))
    R4((description))
    R5((subject))
    R6((roll_no))
    R7((name))
    R8((semester))
    R9((year))
    R10((user_id FK))

    %% =====================
    %% CONNECTIONS
    %% =====================
    Users --> U1
    Users --> U2
    Users --> U3

    Users --> Makes
    Makes --> Requests

    Requests --> R0
    Requests --> R1
    Requests --> R2
    Requests --> R3
    Requests --> R4
    Requests --> R5
    Requests --> R6
    Requests --> R7
    Requests --> R8
    Requests --> R9
    Requests --> R10

    %% =====================
    %% CARDINALITY LABEL
    %% =====================
    Users ---|1 to Many| Requests
```
