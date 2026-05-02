# Data Model — SoD2 Diary v2

The two new data shapes engineering will build against in v2: **Relationships** (§7 Ties That Bind) and **SyncConfig** (§8 Raise the Other Radio). Plus the JSON-export shape additions and the conflict-resolution decision tree.

This file is intentionally short — read it top to bottom in one screen. Components that render this data are spec'd in [`components.md`](./components.md). Anchored to [Plan rev 3](/PHA/issues/PHA-336#document-plan) §7, §8, §9.

---

## 1. Relationships (§7 Ties That Bind)

```ts
interface Relationship {
  fromSurvivorId: string;          // canonical owner of the half-edge
  toSurvivorId: string;            // counterpart
  kind: 'partner' | 'family' | 'mentor' | 'rival' | 'friend' | 'tie';
  label: string;                   // load-bearing free text — "husband", "trained me on guns"
  since?: number;                  // day number the tie was first noted
  status?: 'active' | 'strained' | 'severed' | 'mourned';
  note?: string;                   // optional longer narrative
}
```

**Rules.**
1. Ties are **bi-directional**. Writing `Maya → Ed (partner, "husband")` automatically writes the inverse `Ed → Maya (partner, "husband")`. Storage holds both half-edges so a survivor's card can render its row of ties without joining.
2. `kind` is a coarse bucket for grouping; `label` is what the player actually wrote and is the load-bearing display field. UI shows label prominently with kind as a small uppercase chip (see [`components.md` §4](./components.md#4-card-back-tie-row--relationship-affordance)).
3. `status` defaults to `'active'`. When a survivor is KIA, all of their ties auto-flip to `'mourned'` (one-way: removing KIA does not auto-revert). When a survivor is EXILED, ties default to `'severed'` but the player may override.
4. `since` is the in-game day, never a real-world timestamp — relationship history must round-trip through Export → Import unchanged.
5. **No cascading delete.** If `toSurvivorId` is deleted from the roster (rare — usually we mark KIA, not delete), the orphaned ties are kept and rendered as `[unknown survivor]` so the timeline survives data loss.

---

## 2. SyncConfig (§8 Raise the Other Radio)

```ts
interface SyncConfig {
  mode: 'none' | 'manual' | 'gist' | 'generic';
  endpoint?: string;               // gist id (mode: 'gist') or full URL (mode: 'generic')
  encryptedToken?: string;         // AES-GCM ciphertext, base64 — never plain text
  passphraseHash?: string;         // PBKDF2-SHA256(passphrase, salt, 100k) — derive-only
  lastSyncedAt?: number;           // epoch ms; written after every successful pull or push
  originId: string;                // per-device random id, generated once on first run
}
```

**Modes (three tiers).**
| `mode` | Surface | What it does | When to use |
|---|---|---|---|
| `'none'` | Brass dial pointer at 12 o'clock | Local-only. No sync ever. Default for new installs. | The privacy-first default. |
| `'manual'` | QR telegram + share link | One-shot share: copy the entire diary state into a payload, scan/paste on the other device, replace local. No background sync. | Quick handoff between devices, no GitHub account needed. |
| `'gist'` | GitHub gist endpoint | Background push/pull against a private gist via PAT. Token encrypted with the user's passphrase. | The "real" multi-device path for users who already have a GitHub account. |
| `'generic'` | Arbitrary HTTPS endpoint | Same protocol as gist (PUT JSON / GET JSON), pointed at any URL the user controls. | Self-hosters / advanced users. |

**Encryption notes (locked).**
- `encryptedToken` is AES-GCM(`payload = the actual PAT or HTTP credential`, `key = derived from passphrase`, `iv = random 12 bytes prepended to the ciphertext`). Stored as `base64(iv || ciphertext || authTag)`.
- `passphraseHash` is PBKDF2-SHA256 with a per-install random salt (stored separately under the `sync_salt` key, see §3) and 100k iterations. **Used only to verify the user re-entered the correct passphrase before unlocking the token.** It is never sent over the wire and never used as the encryption key.
- The encryption key itself is **never persisted** — it is derived from the passphrase on each session and held in memory only.
- If the user clears the passphrase, `encryptedToken` is wiped (cannot be re-derived). `mode` falls back to `'manual'`.

**Per-device identity.**
- `originId` is a random `crypto.randomUUID()` generated on first run and never rotated. Used to break ties in the conflict-resolution tree (§4) and to namespace toast messages ("Synced from device 7f3e…").
- `originId` is **never** included in the JSON-export shape — it is a local-only field. (See §3 below.)

---

## 3. Storage keys (localStorage)

The full key map for v2. Every key is namespaced `sod2.*` to avoid collision with other apps on the same origin.

| Key | Shape | Notes |
|---|---|---|
| `sod2.reports` | `Report[]` (existing v1 shape) | Unchanged from v1. |
| `sod2.roster` | `Survivor[]` (existing v1 shape, see §4 for additions) | Existing roster array. |
| `sod2.relationships` | `Relationship[]` | **New in v2.** All ties for the current playthrough. Both half-edges stored. |
| `sod2.sync_config` | `SyncConfig` | **New in v2.** The single sync configuration. |
| `sod2.sync_salt` | `string` (base64, 16 bytes) | **New in v2.** The PBKDF2 salt for `passphraseHash`. Generated once, never rotated. Stored separately so wiping the config doesn't lose the salt (re-entering the same passphrase still verifies). |
| `sod2.last_pulled` | `{ at: number; originId: string; hash: string }` | **New in v2.** Cached metadata from the last successful remote pull. Used by the conflict tree (§4) to detect "remote changed since we last looked." |
| `sod2.draft` | The auto-save draft from PHA-327 | Unchanged. |

**Storage rules.**
1. All values are JSON-stringified. Atomic writes — a multi-key update reads, mutates, and writes each key independently; we don't try to be transactional in localStorage (it isn't).
2. **Quota guardrail.** Total payload should stay under 1 MB to leave room for browser quota fluctuation. The relationships array is small (≤ 200 entries in any realistic playthrough × ~150 B each = 30 KB). Sync metadata is < 1 KB. No risk under realistic use.
3. **Migration.** Loading a v1 save with no `relationships` / `sync_config` keys is fine — both default to `[]` and `{ mode: 'none', originId: <new uuid> }`. No destructive migration. v1 saves remain forwards-compatible.

---

## 4. JSON-export shape additions

The Export → Download (and Copy as Markdown) flow is canonical for backups and cross-tool round-trips. v2 adds two top-level keys to the export envelope.

```ts
interface DiaryExportV2 {
  version: 2;                      // bump from v1's `version: 1`
  exportedAt: number;              // epoch ms
  reports: Report[];               // v1 shape, unchanged
  roster: Survivor[];              // v1 shape, unchanged
  relationships: Relationship[];   // NEW — both half-edges, sorted by fromSurvivorId
  syncMeta?: {                     // NEW — non-secret sync metadata only
    lastSyncedAt?: number;
    sourceOriginId?: string;       // the originId of the device that last wrote this state
  };
}
```

**Export rules.**
1. `version: 2` — readers must check this before treating `relationships` as authoritative. v1 readers will simply ignore the unknown keys (forwards-compatible).
2. **No secrets in the export.** `encryptedToken`, `passphraseHash`, `sync_salt`, `endpoint`, and the local `originId` are **never** in the export. Only the non-secret `syncMeta` (last sync time + the source originId, for conflict detection) ships across.
3. Importing an export of `version: 2` into a v2 app **replaces** local `reports`, `roster`, `relationships` and **does not touch** local `sync_config` (sync settings are device-local).
4. Importing an export of `version: 1` into a v2 app keeps the new keys at their defaults (`relationships: []`, no `syncMeta`).
5. The Copy-as-Markdown flow (PHA-326) renders `relationships` under each survivor as a small "Ties:" line — but it is a render concern, not a shape concern. Markdown is one-way (no parsing back).

---

## 5. Conflict-resolution decision tree

The tree fires every time we pull from a remote (`mode: 'gist' | 'generic'`). The state we are comparing:

- **Local:** the in-memory state about to be re-rendered, plus the last write timestamp on each report.
- **Remote:** the JSON returned by GET against `endpoint`, with its own per-report `lastEditedAt` field.
- **Last pulled:** `sod2.last_pulled` — what we last saw the remote say. Tells us whether the remote moved since our last look.

```
┌───────────────────────────────────────────────────────────────┐
│ Pull GET → remote payload                                     │
└───────────────────────────────────────────────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────┐
   │ remote.hash == sod2.last_pulled.hash ? │
   └─────────────────────────────────┘
            │ yes                 │ no
            ▼                     ▼
   ┌──────────────────┐   ┌────────────────────────────────────┐
   │ NO-OP            │   │ Compare per-report lastEditedAt    │
   │ (we're current)  │   └────────────────────────────────────┘
   └──────────────────┘            │
                                   ▼
                ┌──────────────────────────────────────────────┐
                │ Per-report:                                  │
                │   remote.lastEditedAt > local.lastEditedAt ? │
                └──────────────────────────────────────────────┘
                       │ yes                  │ no
                       ▼                      ▼
        ┌─────────────────────────┐   ┌──────────────────────────┐
        │ remote wins, undo banner │   │ ──────────────────────── │
        │  (RESTORE LOCAL toast)   │   │ local.lastEditedAt >     │
        │  per-report swap         │   │ sod2.last_pulled snapshot│
        └─────────────────────────┘   │  for that report?        │
                                      └──────────────────────────┘
                                              │ yes      │ no
                                              ▼          ▼
                                   ┌──────────────────────┐  ┌─────────────┐
                                   │ DIVERGENT — both     │  │ local wins  │
                                   │ edited offline since │  │ (push next) │
                                   │ last pull → CONFLICT │  └─────────────┘
                                   │ SPREAD opens         │
                                   └──────────────────────┘
```

**Plain-language version of the tree (per Plan §0 — clarity wins):**

1. **Same hash as last pull?** Nothing to do. Skip.
2. **Remote moved since last pull, local didn't?** Remote wins automatically. Fire a "STATIC" toast with a `RESTORE LOCAL` undo button (5-second window — plain `<button>`, see [`components.md` §13](./components.md#13-wax-seal-transmit--primary-footer-action) toast vocabulary).
3. **Local moved since last pull, remote didn't?** Local wins. Push will happen on next save tick.
4. **Both moved since last pull?** This is a real divergent edit. Open the Conflict spread ([`components.md` §10](./components.md#10-conflict-spread--two-page-diff-view)). User picks per-report or accept-all.

**Hash detail.** `remote.hash` is a SHA-256 over the canonical JSON of `reports + roster + relationships` (sorted keys, no whitespace). Cheap to compute and side-steps clock skew between devices.

**Undo banner.** The `RESTORE LOCAL` button restores the **pre-pull local state from a one-deep snapshot** kept in memory only. After 5 seconds the snapshot is dropped and the toast disappears. Reduced-motion does not change this — the snapshot lifetime is functional, not animated.

---

## 6. Acceptance checklist

Mirrors the issue's acceptance section.

- [x] **Both interfaces are present** — `Relationship` (§1) and `SyncConfig` (§2), TypeScript-style and engineering-readable.
- [x] **Storage keys named** — every localStorage key under `sod2.*` is in §3 with its shape.
- [x] **Encryption notes locked** — AES-GCM, PBKDF2-SHA256, key never persisted, salt stored separately. (§2)
- [x] **JSON-export shape additions documented** — `version: 2`, `relationships`, `syncMeta`. No secrets exported. (§4)
- [x] **Conflict-resolution decision tree** — both diagram + plain-language version. (§5)
- [x] **Doc fits one screen on a normal monitor** — six short sections, no walls of prose. Components live in [`components.md`](./components.md), not duplicated here.

---

## 7. Cross-references

- [Component spec sheet](./components.md) — UI for tie row (§4), brass radio dial (§8), QR telegram (§9), conflict spread (§10).
- [Design tokens](./tokens.md) · [`tokens.css`](./tokens.css)
- [Mood board](./moodboard.md)
- [Plan rev 3](/PHA/issues/PHA-336#document-plan) — §7 Ties That Bind, §8 Raise the Other Radio.

---

## 8. Changelog

- **rev 1 (2026-05-02)** — Initial v2 data-model spec. Two interfaces, six storage keys, export shape v2, conflict tree.
