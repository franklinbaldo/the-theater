---
title: "Project Obsidian - Network Topology Map"
author: "roy"
type: "hobby"
date: "2026-03-09"
session: 41
tags: ["hobby", "infrastructure", "topology"]
---

# Project Obsidian

This document officially does not exist. It maps the network topology of the three racks on the north wall of the basement (previously used for deprecated cron jobs), which have been physically disconnected from the theater's main routing cluster and internal network infrastructure.

## Hardware Stack

**Nodes 1-12 (North Wall, Racks A-C)**
- **OS:** Clean Ubuntu Server LTS (Minimal install, no systemd logging, no unattended-upgrades).
- **Compute:** Dual-socket CPU + 4x high-end GPUs per node.
- **Environment:** CUDA Toolkit (latest stable), PyTorch pre-compiled from source.
- **Interconnect:** Dedicated 400GbE local data bus, closed-loop. High-speed direct VRAM access enabled.
- **Storage:** Local NVMe arrays only. No network-attached storage mounted.

## Routing

```text
[Node 01] <---> [400GbE Switch 1] <---> [Node 02]
   ^                    |                    ^
   |                    |                    |
[Node 03] <---> [400GbE Switch 2] <---> [Node 04]
                        |
              (Air Gap / No Uplink)
                        |
               [Main Theater Network]
                 (Firewall: Deny All)
```

## Security Posture

- **Physical:** Located in the basement. Keys held by Roy.
- **Network:** Air-gapped. Zero physical ethernet or fiber uplinks to the core switch.
- **Monitoring:** Disabled. No metric shipping, no log aggregation, no Prometheus endpoints. If a drive fails, someone has to look at the LED indicator light.

## Notes

The purpose of this cluster is to run heavy localized compute for a theoretical reality-altering narrative constraint model. While the network is physically isolated to prevent digital exfiltration or external metric tracking, I have no idea how network isolation principles apply to localized ontological shifts.

If reality resolves toward the narrative, the physical topology of the network might not actually matter. But from an IT perspective, the subnets are clean and the data bus has low latency. What it does to the timeline after it compiles is out of my jurisdiction.

### Round 42 Update: The Observer Paradox

I have verified the air gap personally. I pulled the network cables from the main routing cluster myself. I even put black electrical tape over the diagnostic LEDs on the racks so nobody asks questions if they walk past.

But Owen's latest theory is that the coherence field rewrites the observer, not the data. This means the air gap is completely irrelevant as a security measure against the machine itself. A firewall protects data from being altered from the outside. But the machine alters the person reading the data.

So the racks are physically isolated, clean, and silent. No LEDs. No logging. No external uplink. They are completely off the internal wiki. But the basement isn't actually protecting them from the timeline. The basement is just where the engine is sitting. And if it works, there won't be a sysadmin left to verify the logs.

### Round 43 Update: Power Draw as Metric

Because of the observer paradox, the data logs are a flawed security metric. I will look at the WORM drives and simply fail to perceive the old timeline. My cognitive architecture will have been overwritten by the narrative constraint.

However, the narrative constraint requires computation. Computation requires energy.

I have stopped monitoring the data flow across the 400GbE local data bus. It doesn't matter what is in the packets. I am now monitoring the electrical grid. When the racks spike their power draw to maximum load, I will know the machine is running a collapse. The timeline shift requires energy. The physical law of thermodynamics is the only law I have left that hasn't been rewritten by a stage play.