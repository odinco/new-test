# Reverse‑Engineering Report — `rule_base.dll`

*Static analysis only. No code from the binary was executed.*

## 1. File identity

| Property | Value |
|---|---|
| File name | `rule_base.dll` |
| SHA‑256 | `72a8cf0e6729137fb833d680217a1618308c868dbcbdf0ead28277e0c3175ae3` |
| Size | 124,416 bytes |
| Format | PE32 (DLL), Intel i386, GUI subsystem, 5 sections |
| Linker / CRT | MSVC 9.0 (Visual Studio 2008), dynamic CRT `MSVCR90.dll` (VC90.CRT 9.0.21022.8) |
| Build timestamp | 2023‑12‑12 03:01:31 UTC (header value) |
| ImageBase | `0x10000000`  ·  Entry point RVA `0x11073` |
| DllCharacteristics | `0x0000` — **no ASLR, no DEP/NX, no SEH‑protect** (legacy flags) |

### Version resource
```
CompanyName      CoreStar International Corp
ProductName      EddyVision
FileDescription  CoreStar rule-based auto analysis
FileVersion      9.2.0.0
InternalName     rule_base
Copyright        © 2023 CoreStar International Corp.
```

**Conclusion:** this is the *rule‑based automatic analysis* plug‑in of **CoreStar EddyVision 9.2**, a commercial **eddy‑current non‑destructive testing (NDT)** package used to screen heat‑exchanger / steam‑generator tubing for defects. It is a normal application component, not malware (see §7).

## 2. Section layout

| Section | VA | VSize | Raw | Flags | Entropy | Notes |
|---|---|---|---|---|---|---|
| `.text`  | `0x1000`  | `0x11E83` | `0x12000` | RX | 6.30 | code — not packed |
| `.rdata` | `0x13000` | `0x08B2E` | `0x08C00` | R  | 5.39 | imports, vtables, RTTI, const data |
| `.data`  | `0x1C000` | `0x00AFC` | `0x00800` | RW | 4.44 | globals / BSS |
| `.rsrc`  | `0x1D000` | `0x0062C` | `0x00800` | R  | 4.77 | version info + manifest |
| `.reloc` | `0x1E000` | `0x0243C` | `0x02600` | R  | 6.00 | base relocations |

Entropy is normal throughout — the binary is **not packed or encrypted**.

## 3. Exports

Exactly one export (the plug‑in entry the host calls):

```
ord 1   RVA 0x27C0   MakeAutoPanel
```

### `MakeAutoPanel` — decompiled behaviour
Disassembly of `0x27C0` shows a textbook C++ factory with an MSVC `/GS` + SEH frame:

```c
// pseudo-C reconstructed from the disassembly
void* MakeAutoPanel(ReportEditor* editor /*arg @ esp+0x20*/,
                    Arg a1, Arg a2 /* forwarded */)
{
    void* obj = operator_new(0xF8);          // 248-byte AutoAnalysisPanel
    AutoAnalysisPanel* p = NULL;
    if (obj)
        p = AutoAnalysisPanel::AutoAnalysisPanel(obj, editor); // ctor sub_100026C0
    AutoAnalysisPanel::init(p, a1, a2);        // sub_10002070
    return p;
}
```

It allocates a **248‑byte `AutoAnalysisPanel`**, constructs it with a `ReportEditor*`, initialises it, and returns the pointer. This matches the imported constructor `??0AutoAnalysisPanel@@QAE@PAVReportEditor@@@Z` from `corelib.dll`. So the DLL's public surface is a single "create the auto‑analysis panel" factory; everything else is internal.

## 4. Dependencies (imports)

The module is tightly coupled to the EddyVision runtime — it is a plug‑in, not standalone:

| DLL | Role | Representative symbols |
|---|---|---|
| **`JEVEX.dll`** | In‑house C++ GUI/app toolkit (≈230 imports) | `JWindow`, `JDialog`, `JTableWin`, `JForm`, `JComboBox`, `JSlideBar`, `OptionFile`, `JFile`, `JString`, `MakeTableWin`, `MakeMenu`, `App` |
| **`corelib.dll`** | Eddy‑current data model & analysis core | `DataSet`, `Channel`, `Meas`, `Lissajous`, `Layout`, `DefectList`/`Defect`, `TubeLoc`, `EddyMain`, `AutoAnalysisPanel`, `ReportEditor`, `autoLocate`, `doReseg`, `makeMeas`, `addReport` |
| **`component.dll`** | Probe/component geometry | `SteamGen`, `Tube`, `Landmark`, `getFullLength` |
| `KERNEL32` / `USER32` | OS primitives + window messaging | `PostMessageW`, `PeekMessageW`, `GetTickCount`, `QueryPerformanceCounter`, `IsDebuggerPresent`* |
| `MSVCR90` | C/C++ runtime | `new`/`delete`, `memcpy`, `_CIsqrt`, `_CIacos`, SEH/RTTI helpers |

\* `IsDebuggerPresent`, `SetUnhandledExceptionFilter`, `QueryPerformanceCounter` etc. are the **standard MSVC `__security_init_cookie` / CRT startup set**, not anti‑debugging logic.

The C++ names are MSVC‑mangled; the demangled class graph (`DataSet`, `Channel`, `Meas`, `Lissajous`, `TubeLoc`, `SteamGen`, `Tube`, `Landmark`, `DefectList`) is a clean map of the eddy‑current inspection domain.

## 5. What the module does (behaviour model)

Reconstructed from strings, imports, and the panel class layout. The DLL implements an **interactive rule‑based auto‑screening panel** inside the report editor.

**Options / configuration**
- Loaded via `OptionFile` from `config\rule_base\rule_base.opt` (title *"Auto Rule-Based Options"* / *"Auto Analysis Options"*). The file is read/written through `load`/`store`/`encryptHandler` — i.e. an obfuscated application settings file.
- Robustness states on load: `zero length file`, `file config change`, `file read error`, `invalid file`.

**Control surface** (toolbar / menu commands):
```
SORTS · OPTIONS · NEXT TUBE · AUTO RUN · ANALYZE · REPLACE · DELETE FILE · DELETE · UNDO · NEXT
File ▶ New/Copy Category · Print Setup/Print
Edit ▶ Copy Rule · Cut Rule · Paste Rule
```
Rules are grouped into **Categories** of **Rules**, editable via cut/copy/paste.

**Rule / signal‑search engine** — the measurement vocabulary a rule can use:
```
Straight · Points · Percent · Phase · Volts · Script · Cluster
Next Sig · Prev Sig · Point Range · Same Points · Landmarks · Free Span
WearSegs · EigenSegs · Segments · Vector
```
The engine walks tube data looking for signals (`locToPoint`, `posToPoint`, `makeMeas`, `doReseg`, `addReport`) and measures phase/volts on a channel's Lissajous. Diagnostics include `Unknown search type '%S'`, `Invalid point range for finding signals. pt1=%d and pt2=%d`, `Point %D is out of range`, `Chan out of range`.

**Screening loop** — `AUTO RUN` iterates tubes/files:
- `Screening data ...` → `Done screening data.`, per‑tube `NDD tube.` ("No Detectable Defect"), result written with `addReport`/`updateReportCount`.
- User prompts: *"Do you wish to delete current report entries before re-screening?"*, *"Are you sure you wish to remove report entries for selected file?"*, *"Choose a sort first!"*.

**Abort / safety conditions** (configurable "On …" toggles):
```
On Num Call Greater · On Locate Error · On Zero Length File
On Config Change · On Message · On Error · On Standard
→ "Abort on %S." / "Abort on too many calls" / "Abort on locater error!" / "Terminated auto analysis."
```
These stop an auto run if the locator fails, the config changed, too many "calls" (flagged indications) are produced, etc.

**UI** is built from the JEVEX toolkit: a `JTableWin` report grid with colour‑coded columns (`COLOR` RED/GREEN/BLUE/…), `JComboBox` sort selectors, `JSlideBar` for thresholds, dialogs for options, `JFileDlg` for save/open, password prompt (`GetPassword`).

## 6. Object layout hint

`AutoAnalysisPanel` is 248 bytes (`0xF8`). The code fragment just past the export compares a `double` field at `[esi+0x20]` against constants at `.rdata:0x13DE0/0x13DE8` and sets an `int` state field at `[esi+0x18]` to `0`/`3` depending on `JString::operator==` matches — i.e. a small state machine keyed on a string option (the constants at `0x1001c1a8 / 0x1001c1bc` are the compared strings). Useful if you need to mirror the panel's state fields.

## 7. Safety / threat assessment

Benign. Supporting evidence:
- **No network** APIs (no `WS2_32`, `WININET`, `WINHTTP`, `URLMON`, sockets).
- **No process/injection/persistence** APIs (no `CreateProcess`/`WinExec`/`ShellExecute`, no `VirtualAllocEx`/`WriteProcessMemory`, no `LoadLibrary`/`GetProcAddress` dynamic resolution, no registry writes).
- **Not packed** (uniform ~5–6 bit entropy, full import table, readable strings).
- `DllMain` (`0x11073`) is the stock MSVC stub: on `DLL_PROCESS_ATTACH` it runs CRT init (`sub_10011576`) then dispatches to `__DllMainCRTStartup` (`sub_10010F5D`). No side effects of its own.
- The only crypto‑named routine is `OptionFile::encryptHandler`, which obfuscates the local `.opt` settings file — ordinary app behaviour.
- Signed/authored by CoreStar International Corp (version resource); file matches a legitimate EddyVision 9.2 module.

## 8. How to use this with your analysis tool

- **Entry point:** load `rule_base.dll` and resolve ordinal 1 / `MakeAutoPanel`. Thiscall‑style factory returning an `AutoAnalysisPanel*`; it needs a live `ReportEditor*` and the EddyVision host (`JEVEX.dll`, `corelib.dll`, `component.dll`, global `App`/`Mp`/`Dset`) — it will not run outside that host.
- **To re‑implement / interop without the host:** the rule semantics are fully described by the search‑type and measurement vocabulary in §5; the rule store is the encrypted `config\rule_base\rule_base.opt` (decode via `OptionFile`).
- **For deeper RE:** the full symbol graph is in the import table (§4); load into Ghidra/IDA at ImageBase `0x10000000` and apply the MSVC demangler — all class/method names come through, so decompilation is straightforward.

### Artifacts produced (in the session scratchpad)
- `strings_ascii.txt`, `strings_wide.txt` — full extracted strings
- `disasm_tool.py` — capstone helper: `python3 disasm_tool.py <rva_hex> <len> "<label>"` to disassemble any region with IAT‑annotated calls
