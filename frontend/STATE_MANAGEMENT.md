# State Management Plan

## Decision: React local state + props (no global state library needed)

### Rationale

The app has 4 independent pages with minimal shared state.
Each page owns its data lifecycle (fetch on mount/action, display, reset).
No need for Redux/Zustand/Context at this stage.

### If shared state is needed later (e.g., recent calculations in nav badge):
→ Add a single React Context (`CalculationContext`) that wraps the layout.
→ Keeps the last N calculation results in memory.
→ Still no external library needed.

---

## Per-Page State Strategy

### 1. Calculator (`/`)

| State | Type | Trigger |
|-------|------|---------|
| `formData` | CalculationRequest | User types in form |
| `quickEstimate` | boolean | Toggle switch |
| `result` | CalculationResult \| null | API response from POST /calculate |
| `isLoading` | boolean | While API call in-flight |
| `error` | string \| null | API error message |

**Pattern:** `useState` for each. Form submission calls `calculateLandedCost()`,
sets `isLoading=true`, then `result` or `error` on completion.

---

### 2. HTS Code Browser (`/hts-codes`)

| State | Type | Trigger |
|-------|------|---------|
| `query` | string | Debounced search input |
| `levelFilter` | string \| null | Filter tab click |
| `results` | HTSCode[] | API response from GET /hts-codes |
| `selectedCode` | HTSCode \| null | Click on a result |
| `isLoading` | boolean | While searching |

**Pattern:** `useState` + `useEffect` with debounce (300ms).
When `query` or `levelFilter` changes → fetch from API.

---

### 3. Calculation History (`/history`)

| State | Type | Trigger |
|-------|------|---------|
| `items` | CalculationLog[] | Fetched on mount + filter change |
| `filter` | { hts_code?: string } | Filter input |
| `pagination` | { offset, limit } | Page navigation |
| `expandedId` | string \| null | Click to expand |
| `isLoading` | boolean | While fetching |

**Pattern:** `useState` + `useEffect`. Fetch `listCalculations()` on mount
and when filter/pagination changes. Click expands inline detail.

---

### 4. Admin Panel (`/admin`)

| State | Type | Trigger |
|-------|------|---------|
| `activeTab` | "rules" \| "exclusions" \| "fx" \| "hts" | Tab click |
| `items` | TariffRule[] \| Exclusion[] \| FXRate[] \| HTSCode[] | Per-tab fetch |
| `formMode` | "idle" \| "create" \| "edit" | Button clicks |
| `selectedItem` | any \| null | Click to edit |
| `isLoading` | boolean | While fetching/submitting |

**Pattern:** `useState` per tab. Each tab is essentially its own mini-CRUD page.
Form modal opens on create/edit, submits, then refreshes list.

---

## When to Upgrade

Add a Context or state library if/when:
- Multiple pages need the same live data (e.g., "last 5 calculations" shown in sidebar)
- WebSocket/real-time updates are added
- User auth state needs to be global

Until then: keep it simple with local state.
