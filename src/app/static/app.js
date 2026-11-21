// Frontend von Coniuga: Vue 3 über CDN, ohne Build-Schritt.
// Alle Daten kommen über die REST-Schnittstelle des FastAPI-Backends (/api/...).

const { createApp, nextTick } = Vue;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
    throw new Error(detail || `Fehler ${response.status}`);
  }
  return data;
}

function storage(key, value) {
  // localStorage kann je nach Browser fehlen oder gesperrt sein
  try {
    if (value === undefined) return localStorage.getItem(key);
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch (e) {
    return null;
  }
}

const ExamplesList = {
  props: ["data"],
  template: `
    <div v-if="data" class="examples">
      <p v-if="data.loading" class="muted">Lade Beispielsätze …</p>
      <p v-else-if="data.source === 'unavailable'" class="muted">Der Beispieldienst ist gerade nicht erreichbar.</p>
      <p v-else-if="!data.examples.length" class="muted">Keine Beispielsätze für «{{ data.query }}» gefunden.</p>
      <ul v-else class="plain">
        <li v-for="e in data.examples" :key="e.url">
          <b>{{ e.italian }}</b><br><span class="muted">{{ e.german }}</span>
          <a :href="e.url" target="_blank" rel="noopener" class="src">Quelle</a>
        </li>
      </ul>
    </div>`,
};

createApp({
  components: { ExamplesList },
  data() {
    return {
      user: storage("coniuga-user"),
      nameInput: "",
      error: "",
      tabs: [
        { id: "practice", label: "Üben" },
        { id: "lookup", label: "Nachschlagen" },
        { id: "progress", label: "Fortschritt" },
      ],
      tab: "practice",
      verbs: [],
      exercise: null,
      answer: "",
      feedback: null,
      focusVerb: "",
      tenses: [],
      selectedTenses: null,
      accents: ["à", "è", "é", "ì", "ò", "ù"],
      lookupInput: "",
      lookupError: "",
      lookupChoices: [],
      suggestOpen: false,
      table: null,
      examples: null,
      progress: null,
    };
  },
  async mounted() {
    [this.verbs, this.tenses] = await Promise.all([api("/api/verbs"), api("/api/tenses")]);
    if (this.user) {
      try {
        const data = await api("/api/users", { method: "POST", body: JSON.stringify({ name: this.user }) });
        this.selectedTenses = data.tenses;
        this.nextExercise();
      } catch (e) {
        this.logout();
      }
    }
  },
  computed: {
    // Vorschlagsliste im Nachschlagen (eigene Liste statt <datalist>, die auf
    // Handys unzuverlässig ist). Leeres Feld: alle Verben, alphabetisch.
    // Beim Tippen: Infinitiv oder deutsches Wort beginnt mit der Eingabe.
    suggestions() {
      const q = this.lookupInput.trim().toLowerCase();
      const sorted = [...this.verbs].sort((a, b) => a.infinitive.localeCompare(b.infinitive, "it"));
      if (!q) return sorted;
      return sorted.filter((v) => {
        const words = v.meaning.toLowerCase().split(",").map((w) => w.trim());
        return (
          v.infinitive.startsWith(q) ||
          words.some((w) => w.startsWith(q) || w.replace(/^sich /, "").startsWith(q))
        );
      });
    },
  },
  methods: {
    async login() {
      this.error = "";
      try {
        const data = await api("/api/users", { method: "POST", body: JSON.stringify({ name: this.nameInput }) });
        this.user = data.name;
        this.selectedTenses = data.tenses;
        storage("coniuga-user", data.name);
        this.nextExercise();
      } catch (e) {
        this.error = e.message;
      }
    },
    logout() {
      this.user = null;
      storage("coniuga-user", null);
      this.exercise = this.feedback = this.progress = null;
    },
    openTab(id) {
      this.tab = id;
      this.examples = null;
      if (id === "progress") this.loadProgress();
      if (id === "practice" && !this.exercise) this.nextExercise();
    },
    async nextExercise() {
      const params = new URLSearchParams();
      if (this.focusVerb) params.set("verb", this.focusVerb);
      if (this.exercise) {
        params.set("last_verb", this.exercise.verb);
        params.set("last_tense", this.exercise.tense);
        params.set("last_person", this.exercise.person);
      }
      this.exercise = await api(`/api/users/${encodeURIComponent(this.user)}/exercise?${params}`);
      this.answer = "";
      this.feedback = null;
      this.examples = null;
      await nextTick();
      this.$refs.answerInput && this.$refs.answerInput.focus();
    },
    async submit() {
      const e = this.exercise;
      this.feedback = await api(`/api/users/${encodeURIComponent(this.user)}/answers`, {
        method: "POST",
        body: JSON.stringify({ verb: e.verb, tense: e.tense, person: e.person, answer: this.answer }),
      });
    },
    async setTenses(list) {
      const data = await api(`/api/users/${encodeURIComponent(this.user)}/settings`, {
        method: "PUT",
        body: JSON.stringify({ tenses: list }),
      });
      this.selectedTenses = data.tenses;
      this.nextExercise();
    },
    toggleTense(key) {
      const current = this.selectedTenses ? [...this.selectedTenses] : [];
      const next = current.includes(key) ? current.filter((t) => t !== key) : [...current, key];
      this.setTenses(next.length ? next : null);
    },
    addAccent(a) {
      this.answer += a;
      this.$refs.answerInput.focus();
    },
    pickSuggestion(infinitive) {
      this.lookupInput = infinitive;
      this.suggestOpen = false;
      this.lookupError = "";
      this.showTable(infinitive);
    },
    async lookup(query) {
      // Italienisch oder Deutsch; ein deutsches Wort kann mehrere Verben ergeben
      this.suggestOpen = false;
      this.lookupError = "";
      this.lookupChoices = [];
      this.examples = null;
      this.table = null;
      const q = query.trim();
      if (!q) return;
      const hits = await api(`/api/verbs/search?q=${encodeURIComponent(q)}`);
      if (hits.length === 1) {
        this.showTable(hits[0].infinitive);
      } else if (hits.length > 1) {
        this.lookupChoices = hits;
      } else {
        this.lookupError = `«${q}» ist weder als italienisches Verb noch als deutsche Bedeutung in Coniuga enthalten.`;
      }
    },
    async showTable(infinitive) {
      this.lookupChoices = [];
      this.examples = null;
      this.table = await api(`/api/verbs/${encodeURIComponent(infinitive)}`);
    },
    practiceVerb(verb) {
      this.focusVerb = verb;
      this.tab = "practice";
      this.nextExercise();
    },
    async loadExamples(verb, tense, person) {
      this.examples = { loading: true };
      this.examples = await api(`/api/verbs/${verb}/examples?tense=${tense}&person=${person}`);
    },
    async loadProgress() {
      this.progress = await api(`/api/users/${encodeURIComponent(this.user)}/progress`);
    },
  },
}).mount("#app");
