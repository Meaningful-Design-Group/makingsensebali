# Rhino MCP setup — official mcneel Rhino-MCP-Platform (macOS + Rhino 8)

Source of truth: <https://mcneel.github.io/RhinoMCP/docs/>. This is the corrected, accurate
flow (an earlier draft of this file had the wrong command and a needless build-from-source
path). Two pieces: a **Claude Desktop connector** (`.mcpb` extension) and a **Rhino plugin**
(yak package). The connector talks to a running Rhino that has the plugin loaded and its
server **started**.

> Requirements: **Apple Silicon Mac** (Intel Macs are NOT supported), **Rhino 8 on the latest
> release**, Claude Desktop (web claude.ai can't use MCP).

## 1. Claude Desktop connector

1. Download `connector.mcpb` from the RhinoMCP releases
   (<https://github.com/mcneel/RhinoMCP/releases>).
2. Claude Desktop → `Settings → Extensions → Advanced settings` → **Install Extension** →
   pick the `.mcpb` → **Install**.

## 2. Rhino plugin (yak)

Install the plugin via Rhino's package manager — either in Rhino (`PackageManager`, search
**Rhino-MCP-Platform**, install) or via the yak CLI that ships with Rhino:

```bash
"/Applications/Rhino 8.app/Contents/Resources/bin/yak" install Rhino-MCP-Platform
```

(Upgrade: `yak update Rhino-MCP-Platform`. Remove: `yak uninstall Rhino-MCP-Platform`.)

## 3. Start the server — THE STEP THAT FIXES TIMEOUTS

The connection is made when **Claude Desktop starts**, and Rhino must already be serving at
that moment. So the order matters:

1. **Quit and reopen Rhino 8** after installing the plugin, so it loads. Confirm in
   `PackageManager` that **Rhino-MCP-Platform** is installed.
2. In Rhino, run the command **`MCPStart`**. (This starts the server. The router defaults to
   Rhino 8.)
3. **Fully quit and reopen Claude Desktop** — not just reload. If Claude starts before Rhino
   is serving, every tool call hangs and times out.
4. Verify: `Settings → Extensions` shows the **Rhino3d** connector connected.
5. Test: ask Claude "create a box in Rhino" — a box should appear in the active document.

## Troubleshooting (from the official docs)

- **Agent doesn't see Rhino / calls time out** → connection wasn't made on startup. Make sure
  `MCPStart` is running in Rhino, then **quit and reopen Claude Desktop**. Confirm the plugin
  is installed (`PackageManager`) and the connector shows connected (`Settings → Extensions`).
- **"It says it did something but I don't see it"** → check you're looking at the right Rhino
  window; `View → Zoom → Zoom Extents`; check for hidden layers.
- **Plugin won't load / not in PackageManager** → not supported on .NET Framework or Intel
  Macs; update Rhino to the latest release.
- **Rhino 9 WIP** → in the connector settings change `8` to `9` (Grasshopper-2 `gh2_` tools
  need Rhino 9 WIP).

## Using it with this project

- **Rhino** = organic skin / surfacing (NURBS/SubD), viewport feedback, form studies.
- **build123d** (`tools/enclosure_v*.py`) = functional chassis: exact fits, interference,
  airflow geometry — the source of truth. Bring forms over; don't replace it.
- First move once live: import the corrected **v11** chassis (`v11/v11_plus_body.step`) as a
  reference and shape the shell over it, keeping the flat back, the airflow openings, and the
  80×40×18 HM bay clear.
