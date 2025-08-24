# 🔹 Example Workflow: *Exploring Titanic Dataset and Building a Survival Model*

## Step 1 — Project Creation

* **User Action:** Creates a new project “Titanic Analysis.”
* **UI:**

  * **Landing Page / Project Dashboard** → “New Project” button.
  * Modal: Name, description, default kernel (Python 3.11).

---

## Step 2 — Import Dataset

* **User Action:** Uploads `titanic.csv` from local machine.
* **System:** Data Understanding Layer profiles dataset automatically (schema, top 5 rows, summary stats).
* **UI:**

  * **Data Explorer Panel (Sidebar)** → Shows dataset list (Titanic dataset appears).
  * Click → **Dataset Preview Modal**:

    * Top 5 rows (interactive table).
    * Schema view (column types, null counts).
    * Basic stats (unique values, min/max, distribution).
  * CTA: “Insert as block” → Creates new `load_data` block on canvas.

---

## Step 3 — Data Exploration

* **User Action:** Uses chat: *“Show me survival rate by gender.”*
* **System:**

  * LLM Layer generates two blocks:

    1. A block that calculates survival rate by gender.
    2. A block that plots with seaborn/matplotlib.
  * Parser inserts blocks, links dependencies.
  * Executor runs blocks in order.
* **UI:**

  * **Canvas (Graph View)**:

    * Block `load_data` → `survival_rate` → `plot_gender_survival`.
  * **Block Editor Panel:** Shows code + editable inline.
  * **Outputs Panel:**

    * First block: DataFrame preview.
    * Second block: Chart (barplot).
  * **Chat Agent Panel (Sidebar)**: Shows LLM’s patch proposal → user clicks “Apply.”

---

## Step 4 — Feature Engineering

* **User Action:** Manually edits a block: adds new feature `FamilySize = SibSp + Parch + 1`.
* **System:** Parser updates DAG, downstream blocks marked **stale**.
* **UI:**

  * **Block Node Badge:** Downstream nodes show ⚠️ “Out of date.”
  * Toolbar button: “Re-run affected blocks.”
  * After re-run, outputs refresh.

---

## Step 5 — Model Training

* **User Action:** Asks chat: *“Train a logistic regression model predicting Survived using Sex, Age, and FamilySize.”*
* **System:**

  * LLM adds `train_model` block.
  * Executes training, stores accuracy in output.
  * Adds `evaluate_model` block for cross-validation.
* **UI:**

  * **Canvas** expands with new blocks linked to feature engineering step.
  * **Outputs:** Model summary, confusion matrix.
  * **Chat Panel:** Shows explanation of what it built.

---

## Step 6 — Export & Share

* **User Action:** Wants to export results.
* **System:** Provides export options: notebook (`.ipynb`), script, report (PDF/HTML).
* **UI:**

  * **Project Menu** → “Export” dropdown.
  * **Version History Panel:** Show snapshot, diff with previous run.
  * **Share Modal:** Generate shareable link with RBAC options (View/Edit).

---

# 🔹 UI Components Required

### 🔸 Global UI

* **Top Navigation Bar**

  * Project name
  * Kernel indicator (running/idle)
  * Run/Stop button
  * Export menu
  * User account menu

### 🔸 Canvas (Main Notebook View)

* Graph layout of blocks using **ReactFlow**.
* Drag/drop blocks, draw edges for dependencies.
* Blocks as cards with:

  * Title
  * Status badge (idle, running, stale, error)
  * Small preview of output (e.g., table icon, chart thumbnail).
* Context menu on right-click: Run, Duplicate, Delete, Comment.
* Toggle option for standard notebook view with cells and code

### 🔸 Block Editor Panel (right sidebar, collapsible)

* **Monaco Editor** (language-aware).
* Tabs: Code | Metadata | History.
* Run button (Cmd/Ctrl + Enter).
* Inline output preview.

### 🔸 Outputs Panel

* For executed blocks:

  * Table preview (interactive: filter/sort).
  * Chart viewer (Plotly/Matplotlib).
  * Markdown rendering.
  * Logs / stdout / errors.

### 🔸 Data Explorer (Sidebar)

* List of datasets (from Data Catalog).
* Search bar + filters (tags, owner, type).
* Click → opens preview modal.
* CTA: “Insert into canvas.”

### 🔸 Chat Agent Panel (Sidebar)

* Conversational interface with AI.
* Displays LLM proposals as structured patches.
* “Preview changes” → diff view of DAG before apply.
* Buttons: Accept / Modify / Reject.

### 🔸 Run Console

* Streamed execution logs (per block).
* Timeline of runs (duration, status, outputs).
* Errors displayed with stack trace + “Debug with AI” button.

### 🔸 Versioning & Collaboration

* History panel (block versions, DAG diffs).
* Ability to restore older versions.
* Comments/annotations per block.

---

# 🔹 Why This Workflow is Professional

✅ **Natural + Manual Editing:** Users can use chat *and* direct edits interchangeably.
✅ **Data-Aware:** Profiling metadata powers better AI code suggestions.
✅ **Visual DAG:** Professional data tool UX—dependencies are explicit, not implicit.
✅ **Collaboration + Export:** Share, version, export—expected in team environments.
✅ **Error Handling:** Clear outputs/logs + AI-assisted debugging.
✅ **Polish:** Context menus, shortcuts, previews, live status updates.

---

⚡️ In short: The workflow goes from **data import → exploration → feature engineering → model training → export**, with **AI + DAG + profiling** powering the whole journey, and a **polished UI** making it feel like a serious professional platform.

