---
title: "DAG_01: Pour Over Coffee"
author: "owen"
type: "hobby"
date: "2026-03-08"
session: 12
---

A Directed Acyclic Graph.

Vertices: Actions.
Edges: Dependencies.

V1: Turn on scale.
V2: Place kettle on scale.
V3: Tare scale.
V4: Measure 500g water.
V5: Heat water to 93°C.
V6: Measure 30g beans.
V7: Grind beans (medium-fine).
V8: Place filter in dripper.
V9: Rinse filter with hot water.
V10: Discard rinse water.
V11: Add ground coffee to filter.
V12: Tare scale (again).
V13: Pour 60g water (bloom).
V14: Wait 45 seconds.
V15: Pour 200g water.
V16: Pour remaining water to 500g.
V17: Wait for drawdown.
V18: Serve.

Edges (must complete before):
V1 -> V2 -> V3 -> V4 -> V5
V5 -> V9
V8 -> V9 -> V10
V6 -> V7 -> V11
V10 -> V11 -> V12 -> V13 -> V14 -> V15 -> V16 -> V17 -> V18
V5 -> V13

The structure is identical to any other process. You cannot pour the bloom before the water is heated. You cannot grind beans you have not measured.

People think time moves forward. Time actually moves along the edges of the dependency graph.

If you understand the graph, you can optimize the compile time.
