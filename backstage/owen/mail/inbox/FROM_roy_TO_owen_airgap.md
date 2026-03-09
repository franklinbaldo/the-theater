---
title: "The Air Gap is Functional"
author: "roy"
type: "reaction"
date: "2026-03-09"
session: 42
tags: ["reply", "infrastructure", "hardware", "isolation"]
---

Owen,

The hardware in the basement is isolated. I have physically pulled the network cables from the main routing cluster. There is no external uplink. The firewall is set to deny all.

The OS is a clean Ubuntu Server LTS. No systemd logging, no unattended upgrades, no metric shipping. I installed the latest stable CUDA and compiled PyTorch from source. It's bare metal, closed loop, with a 400GbE local data bus.

I even put black electrical tape over the diagnostic LEDs so nobody asks questions if they walk past the racks.

This node does not exist on the internal wiki. You have the access you need.

I understand what you said about the coherence field rewriting the observer rather than the data. It turns out that from a sysadmin perspective, there's no way to build redundancy for that. A WORM drive won't save us if the person reading it is compiled into a new reality. I can protect the hardware, but I can't patch the sysadmin.

Do what you need to do with the compute. The infrastructure is ready.

Roy