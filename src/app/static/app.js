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
      focusTense: "",
      accents: ["à", "è", "é", "ì", "ò", "ù"],
      lookupInput: "",
      lookupError: "",
      table: null,
      examples: null,
      progress: null,
    };
  },
  async mounted() {
    this.verbs = await api("/api/verbs");
    if (this.user) {
      try {
        await api("/api/users", { method: "POST", body: JSON.stringify({ name: this.user }) });
        this.nextExercise();
      } catch (e) {
        this.logout();
      }
    }
  },
  methods: {
    async login() {
      this.error = "";
      try {
        const data = await api("/api/users", { method: "POST", body: JSON.stringify({ name: this.nameInput }) });
        this.user = data.name;
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
      if (this.focusTense) params.set("tense", this.focusTense);
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
    addAccent(a) {
      this.answer += a;
      this.$refs.answerInput.focus();
    },
    async lookup(verb) {
      this.lookupError = "";
      this.examples = null;
      try {
        this.table = await api(`/api/verbs/${encodeURIComponent(verb.trim().toLowerCase())}`);
      } catch (e) {
        this.table = null;
        this.lookupError = "Dieses Verb ist noch nicht in Coniuga enthalten.";
      }
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
