# System Architecture

## Diagram
[Writer Robot] --(LoRa)--> [Beacons] <--(LoRa)-- [Executor Robot]
       |
       +------------------(LoRa)-----------------+
                         |
                         v
              [Outside Network Area (ONA)]
              - Receive
              - Translate (local to GPS)
              - Carry (4G/Satellite)
              - Brief Executor
                         |
                         v
                 [Command Post]
                 - Live map
                 - Commander decides

## Data Flow
1. Writer explores, detects events, drops beacons.
2. Beacons broadcast messages over LoRa.
3. ONA receives, translates local coordinates to GPS, stores data.
4. ONA forwards to command post via 4G/satellite.
5. Commander creates mission plan.
6. ONA briefs Executor before entry.
7. Executor enters, follows beacon chain, avoids hazards.
8. Executor telemetry goes back through ONA to command post.

## Rules
- No direct robot-to-command-post link.
- All inside-outside communication passes through ONA.
- At least 2 event types.
- At least 2 physical robots (Writer + Executor).
