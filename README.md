

# LogIngestor

## Table of Contents

- [Introduction](#introduction)
- [System Design](#sytem_design)
- [Requirements](#requirements)
- [Installion](#installation)
- [Usage](#usage)
- [Advanced Features](#advanced-features)
- [Sample Queries](#sample-queries)

## Introduction
LogIngest is about ingesting heavy data and filtering logs from web page

## System Design
https://whimsical.com/log-ingestor-RYQ9AmPj9HFU1iuDXPHzSv
![Screenshot from 2023-11-19 19-59-24](https://github.com/Gangadhar454/LogIngestor/assets/36883246/3e0daf36-b085-402c-a071-0fb596c8d485)

The backend architecture is designed with three services, two storages, and two RabbitMQs.

### Services

1. **Logs Handler Service:**
   - Django server responsible for handling log ingest and filtering log queries.
   - For ingest queries, it pushes the log as a message to the `log_messages_queue`.

2. **Worker Service:**
   - Connected to the `celery_beat_queue`.
   - The Scheduler service pushes a message to the `celery_beat_queue` every 5 seconds.
   - The Worker service executes a task (`fetch_100_messages`) every 5 seconds.
   - `fetch_100_messages` function pulls the last 100 messages from `log_messages_queue` and stores them in both Postgres and Elastic Search.

3. **Scheduler Service:**
   - Pushes a message to the `celery_beat_queue` every 5 seconds to trigger the `fetch_100_messages` task.

### Storages

1. **Postgres:**
   - Used for storing logs received from the `log_messages_queue`.

2. **Elastic Search:**
   - Utilized for efficient and fast searching of logs.

### Queues

1. **Log Messages Queue:**
   - Receives ingest queries from the Logs Handler service.
   - The Worker service fetches the last 100 messages for processing.

2. **Celery Beat Queue:**
   - Connects the Scheduler and Worker services.
   - Scheduler pushes messages every 5 seconds to trigger the `fetch_100_messages` task in the Worker service.

### Workflow

- **Log Ingestion:**
  - Logs Handler service ingests logs and sends them as messages to `log_messages_queue`.

- **Periodic Processing:**
  - Scheduler triggers the `fetch_100_messages` task in the Worker service every 5 seconds via `celery_beat_queue`.
  - Worker fetches the last 100 messages from `log_messages_queue` and stores them in Postgres and Elastic Search.

- **Filtering Queries:**
  - If Logs Handler receives a filter query, it directly filters messages from Elastic Search due to its efficient searching capabilities.

This architecture ensures efficient log handling, periodic processing, and fast querying capabilities through a combination of Django, Celery, Postgres, and Elastic Search.


## Requirements

Specify any prerequisites or dependencies needed to run the project.

## Getting Started

Provide step-by-step instructions on how to set up the project locally. Include installation steps, configuration details, and any initial setup required.

```bash
# Example commands
git clone https://github.com/your-username/your-repo.git
cd your-repo
npm install

