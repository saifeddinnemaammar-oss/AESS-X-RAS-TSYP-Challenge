# System Architecture

The Nabad (نبض) USAR (Urban Search and Rescue) system is divided into three distinct zones to ensure reliable operation in disconnected and hazardous environments.

## Zone Architecture

```mermaid
flowchart TD
    subgraph Zone_A [Zone A: Disaster Area / Indoors]
        W[Writer Robot]
        E[Executor Robot]
        B1((Beacon 1))
        B2((Beacon 2))
        W -->|Deploys| B1
        W -->|Deploys| B2
        B1 -.->|LoRa| B2
        E -.->|Homing / LoRa| B1
    end

    subgraph Zone_B [Zone B: Outside Network Area]
        ONA[ONA Gateway]
    end

    subgraph Zone_C [Zone C: Safe Zone]
        CP[Command Post]
    end

    B1 ==LoRa==> ONA
    B2 ==LoRa==> ONA
    ONA ==4G / LTE==> CP
    CP ==4G / LTE==> ONA
    ONA ==LoRa==> E